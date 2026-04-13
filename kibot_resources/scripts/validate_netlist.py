#!/usr/bin/env python3
"""
Netlist Validation Script for KiCad Projects
=============================================
Parses a KiCad netlist (.net) file and validates component connections
against datasheet-defined rules. Outputs a .txt report.

Usage:
    python validate_netlist.py -n <netlist_file> [-o <output_file>]

Rules are defined per component in the COMPONENT_RULES dictionary.
Each rule specifies what must be connected to each pin of a component.
"""

import argparse
import re
import sys
from dataclasses import dataclass, field


# =============================================================================
# Rule definitions — add your components here
# =============================================================================

# Each component rule maps pin functions to a list of checks.
# Checks:
#   "must_connect_to_net"  : pin must be on a net containing this name
#   "must_have_comp"       : net must contain a component whose ref starts with this prefix
#   "must_not_float"       : pin must have at least one other connection
#   "rec_cap_value_uf"     : recommended minimum capacitor value in uF (advisory)

COMPONENT_RULES = {
    "NCP1117-3.3_SOT223": {
        "part_description": "1A 3.3V Fixed LDO Regulator (NCP1117)",
        "datasheet": "http://www.onsemi.com/pub_link/Collateral/NCP1117-D.PDF",
        "pins": {
            "GND": {
                "must_connect_to_net": "GND",
                "description": "Ground pin must connect to GND net",
            },
            "VI": {
                "must_not_float": True,
                "must_have_comp": "C",
                "rec_cap_value_uf": 1.0,
                "description": "Input pin requires decoupling capacitor (min 1uF, 10uF recommended)",
            },
            "VO": {
                "must_not_float": True,
                "must_have_comp": "C",
                "rec_cap_value_uf": 1.0,
                "description": "Output pin requires capacitor for stability (min 1uF, 10uF recommended)",
            },
        },
        "global_checks": {
            "input_cap_to_gnd": {
                "description": "Input capacitor must connect between VI and GND",
                "pin_a": "VI",
                "pin_b": "GND",
                "bridge_comp": "C",
            },
            "output_cap_to_gnd": {
                "description": "Output capacitor must connect between VO and GND",
                "pin_a": "VO",
                "pin_b": "GND",
                "bridge_comp": "C",
            },
        },
    },
    # Add more components below as needed. Example:
    # "AMS1117-3.3": { ... },
}


# =============================================================================
# Netlist parser
# =============================================================================

@dataclass
class Component:
    ref: str = ""
    value: str = ""
    footprint: str = ""
    part: str = ""
    description: str = ""
    pins: dict = field(default_factory=dict)  # pin_num -> pin_function


@dataclass
class NetNode:
    ref: str = ""
    pin: str = ""
    pinfunction: str = ""
    pintype: str = ""


@dataclass
class Net:
    code: str = ""
    name: str = ""
    nodes: list = field(default_factory=list)


def parse_sexp_field(text, field_name):
    """Extract a simple field value from s-expression text."""
    pattern = rf'\({field_name}\s+"([^"]*?)"\)'
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    pattern = rf'\({field_name}\s+([^\s\)]+)\)'
    match = re.search(pattern, text)
    return match.group(1) if match else ""


def parse_netlist(filepath):
    """Parse a KiCad .net file and return components and nets."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    components = {}
    nets = {}

    # Parse components
    comp_pattern = re.compile(
        r'\(comp\s+\(ref\s+"([^"]+)"\)(.*?)\)\s*(?=\(comp|\(libparts)',
        re.DOTALL,
    )
    for match in comp_pattern.finditer(content):
        ref = match.group(1)
        body = match.group(2)
        comp = Component(
            ref=ref,
            value=parse_sexp_field(body, "value"),
            footprint=parse_sexp_field(body, "footprint"),
            description=parse_sexp_field(body, "description"),
        )
        components[ref] = comp

    # Parse libparts for pin info
    libpart_pattern = re.compile(
        r'\(libpart\s+\(lib\s+"[^"]+"\)\s+\(part\s+"([^"]+)"\)(.*?)\)\s*(?=\(libpart|\(libraries)',
        re.DOTALL,
    )
    part_pins = {}
    for match in libpart_pattern.finditer(content):
        part_name = match.group(1)
        body = match.group(2)
        pins = {}
        pin_pattern = re.compile(
            r'\(pin\s+\(num\s+"([^"]+)"\)\s+\(name\s+"([^"]*?)"\)\s+\(type\s+"([^"]+)"\)\)'
        )
        for pin_match in pin_pattern.finditer(body):
            pins[pin_match.group(1)] = pin_match.group(2)
        part_pins[part_name] = pins

    # Map part pins back to components using libsource (authoritative)
    for ref, comp in components.items():
        libsrc_pattern = re.compile(
            rf'\(comp\s+\(ref\s+"{re.escape(ref)}"\).*?\(libsource\s+\(lib\s+"[^"]+"\)\s+\(part\s+"([^"]+)"\)',
            re.DOTALL,
        )
        libsrc_match = libsrc_pattern.search(content)
        if libsrc_match:
            pname = libsrc_match.group(1)
            comp.part = pname
            if pname in part_pins:
                comp.pins = part_pins[pname]

    # Parse nets
    net_pattern = re.compile(
        r'\(net\s+\(code\s+"(\d+)"\)\s+\(name\s+"([^"]+)"\)\s+\(class\s+"[^"]*"\)(.*?)\)\s*(?=\(net\s|\)\)$)',
        re.DOTALL,
    )
    for match in net_pattern.finditer(content):
        net = Net(code=match.group(1), name=match.group(2))
        node_pattern = re.compile(
            r'\(node\s+\(ref\s+"([^"]+)"\)\s+\(pin\s+"([^"]+)"\)'
            r'(?:\s+\(pinfunction\s+"([^"]*?)"\))?'
            r'(?:\s+\(pintype\s+"([^"]*?)"\))?'
        )
        for node_match in node_pattern.finditer(match.group(3)):
            node = NetNode(
                ref=node_match.group(1),
                pin=node_match.group(2),
                pinfunction=node_match.group(3) or "",
                pintype=node_match.group(4) or "",
            )
            net.nodes.append(node)
        nets[net.name] = net

    return components, nets


# =============================================================================
# Validation engine
# =============================================================================

def parse_cap_value(value_str):
    """Parse capacitor value string to uF. Returns None if unparseable."""
    value_str = value_str.strip().upper()
    multipliers = {"PF": 1e-6, "NF": 1e-3, "UF": 1.0, "MF": 1000.0}
    for suffix, mult in multipliers.items():
        if value_str.endswith(suffix):
            try:
                return float(value_str[: -len(suffix)]) * mult
            except ValueError:
                return None
    # Try plain number (assume uF if no unit)
    try:
        return float(value_str)
    except ValueError:
        return None


def find_net_for_component_pin(nets, comp_ref, pin_function):
    """Find which net a component pin is on, by pin function name."""
    for net_name, net in nets.items():
        for node in net.nodes:
            if node.ref == comp_ref and node.pinfunction == pin_function:
                return net_name, net
    return None, None


def find_net_for_component_pin_num(nets, comp_ref, pin_num):
    """Find which net a component pin is on, by pin number."""
    for net_name, net in nets.items():
        for node in net.nodes:
            if node.ref == comp_ref and node.pin == pin_num:
                return net_name, net
    return None, None


def get_comps_on_net(net, exclude_ref=None):
    """Get list of component refs on a net, optionally excluding one."""
    return [n.ref for n in net.nodes if n.ref != exclude_ref]


def validate_component(comp_ref, comp, rules, components, nets):
    """Validate a single component against its rules. Returns (passes, warnings, errors)."""
    passes = []
    warnings = []
    errors = []

    pin_rules = rules.get("pins", {})

    # Build a map: pin_function -> (net_name, net)
    pin_nets = {}
    for pin_num, pin_func in comp.pins.items():
        net_name, net = find_net_for_component_pin(nets, comp_ref, pin_func)
        if not net_name:
            net_name, net = find_net_for_component_pin_num(nets, comp_ref, pin_num)
        if net_name:
            pin_nets[pin_func] = (net_name, net)

    # Check each pin rule
    for pin_func, checks in pin_rules.items():
        desc = checks.get("description", "")
        net_info = pin_nets.get(pin_func)

        if not net_info:
            errors.append(f"  FAIL: Pin {pin_func} - not found in any net (disconnected?)")
            continue

        net_name, net = net_info
        other_comps = get_comps_on_net(net, exclude_ref=comp_ref)

        # Check: must_connect_to_net
        required_net = checks.get("must_connect_to_net")
        if required_net:
            if required_net.upper() in net_name.upper():
                passes.append(f"  PASS: Pin {pin_func} connected to '{net_name}' (requires '{required_net}')")
            else:
                errors.append(f"  FAIL: Pin {pin_func} on net '{net_name}' but must connect to '{required_net}' — {desc}")

        # Check: must_not_float
        if checks.get("must_not_float"):
            if len(other_comps) > 0:
                passes.append(f"  PASS: Pin {pin_func} is not floating (net '{net_name}', {len(other_comps)} other connection(s))")
            else:
                errors.append(f"  FAIL: Pin {pin_func} appears to be floating on net '{net_name}' — {desc}")

        # Check: must_have_comp
        required_prefix = checks.get("must_have_comp")
        if required_prefix:
            matching = [r for r in other_comps if r.startswith(required_prefix)]
            if matching:
                # Get values
                comp_details = ", ".join(
                    f"{r}={components[r].value}" for r in matching if r in components
                )
                passes.append(f"  PASS: Pin {pin_func} has required component(s): {comp_details}")

                # Advisory: check capacitor value
                rec_value = checks.get("rec_cap_value_uf")
                if rec_value and required_prefix == "C":
                    for r in matching:
                        if r in components:
                            cap_uf = parse_cap_value(components[r].value)
                            if cap_uf is not None and cap_uf < rec_value:
                                warnings.append(
                                    f"  WARN: {r} ({components[r].value}) on pin {pin_func} is below "
                                    f"recommended {rec_value}uF — {desc}"
                                )
                            elif cap_uf is not None and cap_uf >= rec_value:
                                passes.append(f"  PASS: {r} value ({components[r].value}) meets minimum {rec_value}uF")
            else:
                errors.append(
                    f"  FAIL: Pin {pin_func} missing required component (prefix '{required_prefix}') — {desc}"
                )

    # Global checks (e.g., cap bridges between two pins)
    global_checks = rules.get("global_checks", {})
    for check_name, check in global_checks.items():
        pin_a = check["pin_a"]
        pin_b = check["pin_b"]
        bridge_prefix = check["bridge_comp"]
        desc = check["description"]

        net_a_info = pin_nets.get(pin_a)
        net_b_info = pin_nets.get(pin_b)

        if not net_a_info or not net_b_info:
            errors.append(f"  FAIL: [{check_name}] Cannot verify — pin(s) not found in netlist")
            continue

        net_a_name, net_a = net_a_info
        net_b_name, net_b = net_b_info

        comps_on_a = {n.ref for n in net_a.nodes if n.ref.startswith(bridge_prefix)}
        comps_on_b = {n.ref for n in net_b.nodes if n.ref.startswith(bridge_prefix)}
        bridging = comps_on_a & comps_on_b

        if bridging:
            bridge_details = ", ".join(
                f"{r}={components[r].value}" for r in bridging if r in components
            )
            passes.append(f"  PASS: [{check_name}] {desc} — bridged by {bridge_details}")
        else:
            errors.append(f"  FAIL: [{check_name}] {desc} — no '{bridge_prefix}' component found between {pin_a} and {pin_b}")

    return passes, warnings, errors


def run_validation(netlist_path, output_path):
    """Main validation runner."""
    components, nets = parse_netlist(netlist_path)

    lines = []
    lines.append("=" * 72)
    lines.append("SCHEMATIC NETLIST VALIDATION REPORT")
    lines.append("=" * 72)
    lines.append(f"Netlist file : {netlist_path}")
    lines.append(f"Components   : {len(components)}")
    lines.append(f"Nets         : {len(nets)}")
    lines.append("")

    total_pass = 0
    total_warn = 0
    total_fail = 0
    validated_count = 0

    # Find components that match rules
    for comp_ref, comp in sorted(components.items()):
        matched_rule = None
        matched_rule_name = None
        for rule_name, rules in COMPONENT_RULES.items():
            if rule_name in comp.part or rule_name in comp.value:
                matched_rule = rules
                matched_rule_name = rule_name
                break

        if not matched_rule:
            continue

        validated_count += 1
        lines.append("-" * 72)
        lines.append(f"Component    : {comp_ref}")
        lines.append(f"Value        : {comp.value}")
        lines.append(f"Part         : {comp.part}")
        lines.append(f"Rule matched : {matched_rule_name}")
        lines.append(f"Datasheet    : {matched_rule.get('datasheet', 'N/A')}")
        lines.append(f"Description  : {matched_rule.get('part_description', '')}")
        lines.append("")

        passes, warnings, errors = validate_component(
            comp_ref, comp, matched_rule, components, nets
        )

        for line in passes:
            lines.append(line)
        for line in warnings:
            lines.append(line)
        for line in errors:
            lines.append(line)

        total_pass += len(passes)
        total_warn += len(warnings)
        total_fail += len(errors)
        lines.append("")

    # Components without rules
    unvalidated = [
        ref for ref, c in components.items()
        if not any(rn in c.part or rn in c.value for rn in COMPONENT_RULES)
    ]
    if unvalidated:
        lines.append("-" * 72)
        lines.append("COMPONENTS WITHOUT VALIDATION RULES (manual review needed):")
        for ref in sorted(unvalidated):
            c = components[ref]
            lines.append(f"  {ref:8s} {c.value:20s} {c.part}")
        lines.append("")

    # Summary
    lines.append("=" * 72)
    lines.append("SUMMARY")
    lines.append("=" * 72)
    lines.append(f"Components validated : {validated_count}")
    lines.append(f"Checks passed       : {total_pass}")
    lines.append(f"Warnings            : {total_warn}")
    lines.append(f"Errors              : {total_fail}")
    lines.append("")

    if total_fail > 0:
        lines.append("RESULT: FAIL — Errors found. Review and fix before proceeding.")
    elif total_warn > 0:
        lines.append("RESULT: PASS WITH WARNINGS — Review warnings against datasheet.")
    else:
        lines.append("RESULT: PASS — All checks passed.")

    lines.append("=" * 72)

    report = "\n".join(lines)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(report)

    return total_fail


def main():
    parser = argparse.ArgumentParser(
        description="Validate KiCad netlist connections against datasheet rules."
    )
    parser.add_argument(
        "-n", "--netlist", required=True, help="Path to KiCad .net file"
    )
    parser.add_argument(
        "-o", "--output", default="Reports/validation_report.txt",
        help="Output .txt report path (default: Reports/validation_report.txt)",
    )
    args = parser.parse_args()

    error_count = run_validation(args.netlist, args.output)
    sys.exit(1 if error_count > 0 else 0)


if __name__ == "__main__":
    main()
