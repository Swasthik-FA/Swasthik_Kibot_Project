#!/usr/bin/env python3
"""
Netlist Validation Script for KiCad Projects
=============================================
Parses a KiCad netlist (.net) file and validates component connections
using both generic category-based rules and part-specific rules.
Outputs .txt and .html reports.

Usage:
    python validate_netlist.py -n <netlist_file> [-o <output_dir>]

Generic rules apply automatically to all components by category (regulators,
MCUs, ICs, crystals, connectors). Part-specific rules override or extend
generic rules for known components.
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone


# =============================================================================
# Generic category-based rules (apply to ALL components matching the category)
# =============================================================================

# Categories are matched by KiCad library name or pin type patterns.
# These catch ~80% of common mistakes without per-part definitions.

CATEGORY_RULES = {
    "voltage_regulator": {
        "description": "Voltage regulators (LDO, DC-DC, linear)",
        "match_libs": ["Regulator_Linear", "Regulator_Switching"],
        "match_keywords": ["regulator", "LDO", "VREG", "voltage reg"],
        "checks": [
            {
                "name": "gnd_connected",
                "type": "pin_on_net",
                "pin_types": ["power_in"],
                "pin_names": ["GND", "VSS", "PGND", "AGND", "EP", "PAD"],
                "net_contains": "GND",
                "severity": "error",
                "description": "Ground pin must connect to a GND net",
            },
            {
                "name": "input_not_floating",
                "type": "pin_not_floating",
                "pin_names": ["VI", "VIN", "IN", "INPUT"],
                "severity": "error",
                "description": "Input power pin must not be floating",
            },
            {
                "name": "output_not_floating",
                "type": "pin_not_floating",
                "pin_names": ["VO", "VOUT", "OUT", "OUTPUT", "FB"],
                "severity": "error",
                "description": "Output pin must not be floating",
            },
            {
                "name": "input_decoupling",
                "type": "pin_has_comp",
                "pin_names": ["VI", "VIN", "IN", "INPUT"],
                "comp_prefix": "C",
                "severity": "error",
                "description": "Input pin requires a decoupling capacitor",
            },
            {
                "name": "output_capacitor",
                "type": "pin_has_comp",
                "pin_names": ["VO", "VOUT", "OUT", "OUTPUT"],
                "comp_prefix": "C",
                "severity": "error",
                "description": "Output pin requires a capacitor for stability",
            },
            {
                "name": "enable_not_floating",
                "type": "pin_not_floating",
                "pin_names": ["EN", "ENABLE", "CE", "SHDN", "SHUTDOWN", "ON/OFF"],
                "severity": "warning",
                "description": "Enable/shutdown pin should not be floating",
            },
        ],
    },
    "mcu": {
        "description": "Microcontrollers (STM32, ESP32, ATmega, PIC, etc.)",
        "match_libs": ["MCU_ST", "MCU_Microchip", "MCU_NXP", "MCU_Nordic",
                       "MCU_Espressif", "MCU_Texas", "MCU_Atmel"],
        "match_keywords": ["STM32", "ESP32", "ATmega", "PIC", "nRF", "SAMD",
                           "MSP430", "RP2040", "microcontroller"],
        "checks": [
            {
                "name": "vdd_not_floating",
                "type": "power_pin_not_floating",
                "pin_names": ["VDD", "VDDA", "VDDIO", "VCC", "VCAP", "VBAT",
                              "3V3", "DVDD", "AVDD"],
                "severity": "error",
                "description": "Power supply pin must be connected",
            },
            {
                "name": "vss_on_gnd",
                "type": "pin_on_net",
                "pin_types": ["power_in"],
                "pin_names": ["VSS", "VSSA", "GND", "AGND", "DGND", "EP", "PAD"],
                "net_contains": "GND",
                "severity": "error",
                "description": "Ground pin must connect to a GND net",
            },
            {
                "name": "vdd_decoupling",
                "type": "pin_has_comp",
                "pin_names": ["VDD", "VDDA", "VDDIO", "VCC", "DVDD", "AVDD"],
                "comp_prefix": "C",
                "severity": "error",
                "description": "Power pin requires a bypass capacitor (typically 100nF)",
            },
            {
                "name": "reset_not_floating",
                "type": "pin_not_floating",
                "pin_names": ["NRST", "RESET", "RST", "~{RST}", "~{RESET}",
                              "MCLR", "~{MCLR}"],
                "severity": "warning",
                "description": "Reset pin should not be floating (add pull-up or connect to reset circuit)",
            },
            {
                "name": "boot_not_floating",
                "type": "pin_not_floating",
                "pin_names": ["BOOT0", "BOOT1", "BOOT"],
                "severity": "warning",
                "description": "Boot pin should not be floating (tie to GND or VDD)",
            },
        ],
    },
    "ic_generic": {
        "description": "Generic ICs (op-amps, interfaces, sensors, etc.)",
        "match_libs": ["Amplifier_Operational", "Interface", "Sensor",
                       "Analog_ADC", "Analog_DAC", "Timer", "Logic",
                       "Interface_USB", "Interface_UART", "Interface_CAN",
                       "Interface_Ethernet"],
        "match_keywords": [],
        "checks": [
            {
                "name": "power_not_floating",
                "type": "power_pin_not_floating",
                "pin_names": ["VCC", "VDD", "V+", "VS+", "AVCC", "DVCC"],
                "severity": "error",
                "description": "Power supply pin must be connected",
            },
            {
                "name": "gnd_on_gnd",
                "type": "pin_on_net",
                "pin_types": ["power_in"],
                "pin_names": ["GND", "VSS", "V-", "VS-", "AGND", "DGND",
                              "EP", "PAD"],
                "net_contains": "GND",
                "severity": "error",
                "description": "Ground pin must connect to a GND net",
            },
            {
                "name": "power_decoupling",
                "type": "pin_has_comp",
                "pin_names": ["VCC", "VDD", "V+", "VS+", "AVCC", "DVCC"],
                "comp_prefix": "C",
                "severity": "warning",
                "description": "Power pin should have a bypass capacitor",
            },
        ],
    },
    "crystal": {
        "description": "Crystals and oscillators",
        "match_libs": ["Device"],
        "match_keywords": ["crystal", "Crystal", "MHz", "oscillator"],
        "match_parts": ["Crystal", "Crystal_GND24", "Crystal_GND2",
                        "Resonator"],
        "checks": [
            {
                "name": "crystal_load_caps",
                "type": "pin_has_comp",
                "pin_names": ["1", "2"],
                "comp_prefix": "C",
                "severity": "warning",
                "description": "Crystal pins typically need load capacitors",
            },
        ],
    },
    "connector": {
        "description": "Connectors (headers, terminals, USB, etc.)",
        "match_libs": ["Connector", "Connector_Generic"],
        "match_keywords": ["connector", "header", "terminal", "socket"],
        "checks": [
            {
                "name": "no_floating_pins",
                "type": "all_pins_not_floating",
                "severity": "warning",
                "description": "Connector pin appears unconnected (if intentional, add no-connect flag in schematic)",
            },
        ],
    },
}


# =============================================================================
# Part-specific rules (override/extend generic rules for known components)
# =============================================================================

PART_RULES = {
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
    # Add more part-specific rules as your team encounters new ICs:
    # "AMS1117-3.3": { ... },
    # "STM32F405RGT6": { ... },
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
    lib: str = ""
    description: str = ""
    keywords: str = ""
    pins: dict = field(default_factory=dict)       # pin_num -> pin_name
    pin_types: dict = field(default_factory=dict)   # pin_num -> pin_type


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
        # Extract libsource
        libsrc_match = re.search(
            r'\(libsource\s+\(lib\s+"([^"]+)"\)\s+\(part\s+"([^"]+)"\)', body
        )
        if libsrc_match:
            comp.lib = libsrc_match.group(1)
            comp.part = libsrc_match.group(2)
        # Extract keywords
        kw_match = re.search(r'\(property\s+\(name\s+"ki_keywords"\)\s+\(value\s+"([^"]*?)"\)\)', body)
        if kw_match:
            comp.keywords = kw_match.group(1)
        components[ref] = comp

    # Parse libparts for pin info
    libpart_pattern = re.compile(
        r'\(libpart\s+\(lib\s+"[^"]+"\)\s+\(part\s+"([^"]+)"\)(.*?)\)\s*(?=\(libpart|\(libraries)',
        re.DOTALL,
    )
    part_pins = {}
    part_pin_types = {}
    for match in libpart_pattern.finditer(content):
        part_name = match.group(1)
        body = match.group(2)
        pins = {}
        pin_types = {}
        pin_pattern = re.compile(
            r'\(pin\s+\(num\s+"([^"]+)"\)\s+\(name\s+"([^"]*?)"\)\s+\(type\s+"([^"]+)"\)\)'
        )
        for pin_match in pin_pattern.finditer(body):
            pins[pin_match.group(1)] = pin_match.group(2)
            pin_types[pin_match.group(1)] = pin_match.group(3)
        part_pins[part_name] = pins
        part_pin_types[part_name] = pin_types

    # Map part pins back to components using libsource
    for ref, comp in components.items():
        if comp.part in part_pins:
            comp.pins = part_pins[comp.part]
            comp.pin_types = part_pin_types[comp.part]

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
# Validation helpers
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
    try:
        return float(value_str)
    except ValueError:
        return None


def find_net_for_pin(nets, comp_ref, pin_function=None, pin_num=None):
    """Find which net a component pin is on."""
    for net_name, net in nets.items():
        for node in net.nodes:
            if node.ref != comp_ref:
                continue
            if pin_function and node.pinfunction == pin_function:
                return net_name, net
            if pin_num and node.pin == pin_num:
                return net_name, net
    return None, None


def get_comps_on_net(net, exclude_ref=None):
    """Get list of component refs on a net, optionally excluding one."""
    return [n.ref for n in net.nodes if n.ref != exclude_ref]


def find_matching_pins(comp, pin_names):
    """Find pin numbers that match any of the given pin names."""
    matched = []
    for pin_num, pin_name in comp.pins.items():
        if pin_name in pin_names:
            matched.append((pin_num, pin_name))
    return matched


# =============================================================================
# Category matching
# =============================================================================

def match_category(comp):
    """Determine which category rules apply to a component."""
    matched = []
    for cat_name, cat_rules in CATEGORY_RULES.items():
        # Match by library
        if comp.lib in cat_rules.get("match_libs", []):
            # For crystals, also check part name
            if "match_parts" in cat_rules:
                if any(p == comp.part or p in comp.part for p in cat_rules["match_parts"]):
                    matched.append(cat_name)
                continue
            matched.append(cat_name)
            continue
        # Match by keywords
        for kw in cat_rules.get("match_keywords", []):
            if (kw.lower() in comp.description.lower() or
                    kw.lower() in comp.keywords.lower() or
                    kw.lower() in comp.value.lower()):
                matched.append(cat_name)
                break
    return matched


# =============================================================================
# Generic category validation engine
# =============================================================================

@dataclass
class CheckResult:
    status: str = ""   # "pass", "warn", "error"
    message: str = ""
    rule_name: str = ""
    category: str = ""


def run_category_checks(comp_ref, comp, category_name, checks, components, nets):
    """Run generic category checks on a component."""
    results = []

    for check in checks:
        check_type = check["type"]
        check_name = check["name"]
        desc = check["description"]
        severity = check["severity"]

        if check_type == "pin_on_net":
            pin_names = check.get("pin_names", [])
            net_contains = check["net_contains"]
            matched_pins = find_matching_pins(comp, pin_names)
            if not matched_pins:
                continue  # Component doesn't have these pins
            for pin_num, pin_name in matched_pins:
                net_name, net = find_net_for_pin(nets, comp_ref, pin_function=pin_name, pin_num=pin_num)
                if not net_name:
                    results.append(CheckResult("error", f"Pin {pin_name} ({pin_num}) not found in any net", check_name, category_name))
                elif net_contains.upper() in net_name.upper():
                    results.append(CheckResult("pass", f"Pin {pin_name} connected to '{net_name}'", check_name, category_name))
                else:
                    results.append(CheckResult(severity, f"Pin {pin_name} on net '{net_name}' but expected '{net_contains}' — {desc}", check_name, category_name))

        elif check_type in ("pin_not_floating", "power_pin_not_floating"):
            pin_names = check.get("pin_names", [])
            matched_pins = find_matching_pins(comp, pin_names)
            if not matched_pins:
                continue
            for pin_num, pin_name in matched_pins:
                net_name, net = find_net_for_pin(nets, comp_ref, pin_function=pin_name, pin_num=pin_num)
                if not net_name:
                    results.append(CheckResult(severity, f"Pin {pin_name} ({pin_num}) not in netlist — {desc}", check_name, category_name))
                else:
                    others = get_comps_on_net(net, exclude_ref=comp_ref)
                    if len(others) > 0:
                        results.append(CheckResult("pass", f"Pin {pin_name} connected (net '{net_name}', {len(others)} connection(s))", check_name, category_name))
                    else:
                        results.append(CheckResult(severity, f"Pin {pin_name} floating on net '{net_name}' — {desc}", check_name, category_name))

        elif check_type == "pin_has_comp":
            pin_names = check.get("pin_names", [])
            comp_prefix = check["comp_prefix"]
            matched_pins = find_matching_pins(comp, pin_names)
            if not matched_pins:
                continue
            for pin_num, pin_name in matched_pins:
                net_name, net = find_net_for_pin(nets, comp_ref, pin_function=pin_name, pin_num=pin_num)
                if not net_name:
                    continue
                others = get_comps_on_net(net, exclude_ref=comp_ref)
                matching_comps = [r for r in others if r.startswith(comp_prefix)]
                if matching_comps:
                    detail = ", ".join(f"{r}={components[r].value}" for r in matching_comps if r in components)
                    results.append(CheckResult("pass", f"Pin {pin_name} has {comp_prefix}: {detail}", check_name, category_name))
                else:
                    results.append(CheckResult(severity, f"Pin {pin_name} missing {comp_prefix} component — {desc}", check_name, category_name))

        elif check_type == "all_pins_not_floating":
            for pin_num, pin_name in comp.pins.items():
                net_name, net = find_net_for_pin(nets, comp_ref, pin_function=pin_name, pin_num=pin_num)
                label = pin_name if pin_name else f"pin {pin_num}"
                if not net_name:
                    results.append(CheckResult(severity, f"{label} not connected — {desc}", check_name, category_name))
                else:
                    results.append(CheckResult("pass", f"{label} connected (net '{net_name}')", check_name, category_name))

    return results


# =============================================================================
# Part-specific validation engine (kept from original)
# =============================================================================

def run_part_checks(comp_ref, comp, rules, components, nets):
    """Run part-specific checks on a component."""
    results = []
    pin_rules = rules.get("pins", {})

    # Build pin -> net map
    pin_nets = {}
    for pin_num, pin_func in comp.pins.items():
        net_name, net = find_net_for_pin(nets, comp_ref, pin_function=pin_func, pin_num=pin_num)
        if net_name:
            pin_nets[pin_func] = (net_name, net)

    # Per-pin checks
    for pin_func, checks in pin_rules.items():
        desc = checks.get("description", "")
        net_info = pin_nets.get(pin_func)

        if not net_info:
            results.append(CheckResult("error", f"Pin {pin_func} not found in any net (disconnected?)", "part_specific", "part"))
            continue

        net_name, net = net_info
        other_comps = get_comps_on_net(net, exclude_ref=comp_ref)

        required_net = checks.get("must_connect_to_net")
        if required_net:
            if required_net.upper() in net_name.upper():
                results.append(CheckResult("pass", f"Pin {pin_func} connected to '{net_name}'", "part_specific", "part"))
            else:
                results.append(CheckResult("error", f"Pin {pin_func} on net '{net_name}' but must be '{required_net}' — {desc}", "part_specific", "part"))

        if checks.get("must_not_float"):
            if len(other_comps) > 0:
                results.append(CheckResult("pass", f"Pin {pin_func} not floating ({len(other_comps)} connection(s))", "part_specific", "part"))
            else:
                results.append(CheckResult("error", f"Pin {pin_func} floating — {desc}", "part_specific", "part"))

        required_prefix = checks.get("must_have_comp")
        if required_prefix:
            matching = [r for r in other_comps if r.startswith(required_prefix)]
            if matching:
                detail = ", ".join(f"{r}={components[r].value}" for r in matching if r in components)
                results.append(CheckResult("pass", f"Pin {pin_func} has {required_prefix}: {detail}", "part_specific", "part"))
                rec_value = checks.get("rec_cap_value_uf")
                if rec_value and required_prefix == "C":
                    for r in matching:
                        if r in components:
                            cap_uf = parse_cap_value(components[r].value)
                            if cap_uf is not None and cap_uf < rec_value:
                                results.append(CheckResult("warn", f"{r} ({components[r].value}) below recommended {rec_value}uF — {desc}", "part_specific", "part"))
                            elif cap_uf is not None:
                                results.append(CheckResult("pass", f"{r} ({components[r].value}) meets minimum {rec_value}uF", "part_specific", "part"))
            else:
                results.append(CheckResult("error", f"Pin {pin_func} missing {required_prefix} — {desc}", "part_specific", "part"))

    # Global bridge checks
    for check_name, check in rules.get("global_checks", {}).items():
        pin_a, pin_b = check["pin_a"], check["pin_b"]
        bridge_prefix = check["bridge_comp"]
        desc = check["description"]

        net_a = pin_nets.get(pin_a)
        net_b = pin_nets.get(pin_b)
        if not net_a or not net_b:
            results.append(CheckResult("error", f"[{check_name}] Cannot verify — pin(s) not in netlist", "part_specific", "part"))
            continue

        comps_a = {n.ref for n in net_a[1].nodes if n.ref.startswith(bridge_prefix)}
        comps_b = {n.ref for n in net_b[1].nodes if n.ref.startswith(bridge_prefix)}
        bridging = comps_a & comps_b
        if bridging:
            detail = ", ".join(f"{r}={components[r].value}" for r in bridging if r in components)
            results.append(CheckResult("pass", f"[{check_name}] {desc} — bridged by {detail}", "part_specific", "part"))
        else:
            results.append(CheckResult("error", f"[{check_name}] {desc} — no {bridge_prefix} between {pin_a} and {pin_b}", "part_specific", "part"))

    return results


# =============================================================================
# Report generation — TXT
# =============================================================================

def generate_txt_report(all_results, components, netlist_path):
    """Generate a plain text validation report."""
    lines = []
    lines.append("=" * 72)
    lines.append("SCHEMATIC NETLIST VALIDATION REPORT")
    lines.append("=" * 72)
    lines.append(f"Date         : {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append(f"Netlist file : {netlist_path}")
    lines.append(f"Components   : {len(components)}")
    lines.append("")

    total_pass = total_warn = total_fail = 0

    for comp_ref, comp_data in sorted(all_results.items()):
        comp = comp_data["comp"]
        categories = comp_data.get("categories", [])
        has_part_rule = comp_data.get("has_part_rule", False)
        results = comp_data["results"]

        if not results:
            continue

        rule_info = []
        if categories:
            rule_info.append(f"Categories: {', '.join(categories)}")
        if has_part_rule:
            rule_info.append(f"Part rule: {comp.part}")

        lines.append("-" * 72)
        lines.append(f"Component : {comp_ref} ({comp.value})")
        lines.append(f"Part      : {comp.part} [{comp.lib}]")
        lines.append(f"Rules     : {'; '.join(rule_info) if rule_info else 'none'}")
        lines.append("")

        for r in results:
            if r.status == "pass":
                lines.append(f"  PASS: {r.message}")
                total_pass += 1
            elif r.status == "warn":
                lines.append(f"  WARN: {r.message}")
                total_warn += 1
            else:
                lines.append(f"  FAIL: {r.message}")
                total_fail += 1
        lines.append("")

    # Unvalidated components
    unvalidated = [ref for ref, data in all_results.items() if not data["results"]]
    if unvalidated:
        lines.append("-" * 72)
        lines.append("COMPONENTS WITHOUT MATCHING RULES (manual review needed):")
        for ref in sorted(unvalidated):
            c = all_results[ref]["comp"]
            lines.append(f"  {ref:10s} {c.value:24s} {c.part} [{c.lib}]")
        lines.append("")

    lines.append("=" * 72)
    lines.append("SUMMARY")
    lines.append("=" * 72)
    validated = sum(1 for d in all_results.values() if d["results"])
    lines.append(f"Components validated : {validated} / {len(components)}")
    lines.append(f"Checks passed       : {total_pass}")
    lines.append(f"Warnings            : {total_warn}")
    lines.append(f"Errors              : {total_fail}")
    lines.append("")

    if total_fail > 0:
        lines.append("RESULT: FAIL")
    elif total_warn > 0:
        lines.append("RESULT: PASS WITH WARNINGS")
    else:
        lines.append("RESULT: PASS")
    lines.append("=" * 72)

    return "\n".join(lines), total_fail


# =============================================================================
# Report generation — HTML
# =============================================================================

def generate_html_report(all_results, components, netlist_path):
    """Generate an HTML validation report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    total_pass = total_warn = total_fail = 0
    validated = sum(1 for d in all_results.values() if d["results"])

    for data in all_results.values():
        for r in data["results"]:
            if r.status == "pass":
                total_pass += 1
            elif r.status == "warn":
                total_warn += 1
            else:
                total_fail += 1

    if total_fail > 0:
        overall = "FAIL"
        overall_color = "#e74c3c"
    elif total_warn > 0:
        overall = "PASS WITH WARNINGS"
        overall_color = "#f39c12"
    else:
        overall = "PASS"
        overall_color = "#27ae60"

    html = []
    html.append("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Netlist Validation Report</title>
<style>
  :root {
    --bg: #1a1a2e;
    --bg-card: #16213e;
    --bg-row-alt: #1a2640;
    --text: #e0e0e0;
    --text-dim: #8899aa;
    --border: #2a3a5c;
    --pass: #27ae60;
    --warn: #f39c12;
    --fail: #e74c3c;
    --accent: #3498db;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, monospace;
    background: var(--bg);
    color: var(--text);
    padding: 20px;
    line-height: 1.6;
  }
  .container { max-width: 1200px; margin: 0 auto; }
  h1 { color: var(--accent); margin-bottom: 5px; font-size: 1.5em; }
  .subtitle { color: var(--text-dim); margin-bottom: 20px; font-size: 0.9em; }
  .summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
    margin-bottom: 25px;
  }
  .summary-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 15px;
    text-align: center;
  }
  .summary-card .number {
    font-size: 2em;
    font-weight: bold;
    display: block;
  }
  .summary-card .label {
    font-size: 0.85em;
    color: var(--text-dim);
  }
  .overall-badge {
    display: inline-block;
    padding: 6px 20px;
    border-radius: 20px;
    font-weight: bold;
    font-size: 1.1em;
    margin-bottom: 20px;
  }
  .comp-section {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    margin-bottom: 12px;
    overflow: hidden;
  }
  .comp-header {
    padding: 12px 16px;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border);
    user-select: none;
  }
  .comp-header:hover { background: var(--bg-row-alt); }
  .comp-header .comp-name { font-weight: bold; font-size: 1.05em; }
  .comp-header .comp-info { color: var(--text-dim); font-size: 0.85em; }
  .comp-header .badges { display: flex; gap: 6px; }
  .badge {
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.8em;
    font-weight: bold;
  }
  .badge-pass { background: var(--pass); color: #fff; }
  .badge-warn { background: var(--warn); color: #fff; }
  .badge-fail { background: var(--fail); color: #fff; }
  .badge-cat {
    background: transparent;
    border: 1px solid var(--accent);
    color: var(--accent);
  }
  .comp-body { padding: 0; display: none; }
  .comp-body.open { display: block; }
  .check-row {
    display: flex;
    align-items: flex-start;
    padding: 8px 16px;
    border-bottom: 1px solid var(--border);
    font-size: 0.9em;
  }
  .check-row:last-child { border-bottom: none; }
  .check-row:nth-child(even) { background: var(--bg-row-alt); }
  .check-icon {
    width: 22px;
    min-width: 22px;
    font-size: 1.1em;
    margin-right: 10px;
    text-align: center;
  }
  .check-pass .check-icon { color: var(--pass); }
  .check-warn .check-icon { color: var(--warn); }
  .check-fail .check-icon { color: var(--fail); }
  .unvalidated-section {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
    margin-top: 20px;
  }
  .unvalidated-section h3 { color: var(--text-dim); margin-bottom: 10px; }
  .unvalidated-list { color: var(--text-dim); font-size: 0.9em; }
  .unvalidated-list div { padding: 3px 0; font-family: monospace; }
  .chevron {
    transition: transform 0.2s;
    display: inline-block;
    margin-right: 5px;
  }
  .chevron.open { transform: rotate(90deg); }
  footer {
    text-align: center;
    color: var(--text-dim);
    font-size: 0.8em;
    margin-top: 30px;
    padding-top: 15px;
    border-top: 1px solid var(--border);
  }
</style>
</head>
<body>
<div class="container">
""")

    html.append(f'<h1>Netlist Validation Report</h1>')
    html.append(f'<div class="subtitle">{now} &mdash; {os.path.basename(netlist_path)}</div>')

    html.append(f'<div class="overall-badge" style="background:{overall_color};color:#fff;">{overall}</div>')

    html.append('<div class="summary-grid">')
    html.append(f'<div class="summary-card"><span class="number">{validated}/{len(components)}</span><span class="label">Components Validated</span></div>')
    html.append(f'<div class="summary-card"><span class="number" style="color:var(--pass)">{total_pass}</span><span class="label">Passed</span></div>')
    html.append(f'<div class="summary-card"><span class="number" style="color:var(--warn)">{total_warn}</span><span class="label">Warnings</span></div>')
    html.append(f'<div class="summary-card"><span class="number" style="color:var(--fail)">{total_fail}</span><span class="label">Errors</span></div>')
    html.append('</div>')

    # Component sections
    for comp_ref, comp_data in sorted(all_results.items()):
        results = comp_data["results"]
        if not results:
            continue

        comp = comp_data["comp"]
        categories = comp_data.get("categories", [])
        has_part_rule = comp_data.get("has_part_rule", False)

        n_pass = sum(1 for r in results if r.status == "pass")
        n_warn = sum(1 for r in results if r.status == "warn")
        n_fail = sum(1 for r in results if r.status == "error")

        html.append('<div class="comp-section">')
        html.append(f'<div class="comp-header" onclick="toggleBody(this)">')
        html.append(f'<div><span class="chevron">&#9654;</span><span class="comp-name">{comp_ref}</span> ')
        html.append(f'<span class="comp-info">&mdash; {comp.value} [{comp.lib}]</span></div>')
        html.append('<div class="badges">')
        for cat in categories:
            html.append(f'<span class="badge badge-cat">{cat}</span>')
        if has_part_rule:
            html.append(f'<span class="badge badge-cat">part-specific</span>')
        if n_pass > 0:
            html.append(f'<span class="badge badge-pass">{n_pass} pass</span>')
        if n_warn > 0:
            html.append(f'<span class="badge badge-warn">{n_warn} warn</span>')
        if n_fail > 0:
            html.append(f'<span class="badge badge-fail">{n_fail} fail</span>')
        html.append('</div></div>')

        html.append('<div class="comp-body">')
        for r in results:
            if r.status == "pass":
                css = "check-pass"
                icon = "&#10003;"
            elif r.status == "warn":
                css = "check-warn"
                icon = "&#9888;"
            else:
                css = "check-fail"
                icon = "&#10007;"
            msg = r.message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            html.append(f'<div class="check-row {css}"><span class="check-icon">{icon}</span><span>{msg}</span></div>')
        html.append('</div></div>')

    # Unvalidated
    unvalidated = [(ref, data["comp"]) for ref, data in sorted(all_results.items()) if not data["results"]]
    if unvalidated:
        html.append('<div class="unvalidated-section">')
        html.append(f'<h3>Components Without Matching Rules ({len(unvalidated)})</h3>')
        html.append('<div class="unvalidated-list">')
        for ref, c in unvalidated:
            html.append(f'<div>{ref:10s} &mdash; {c.value} &mdash; {c.part} [{c.lib}]</div>')
        html.append('</div></div>')

    html.append("""
<footer>Generated by validate_netlist.py &mdash; Netlist Validation Script for KiCad</footer>
</div>
<script>
function toggleBody(header) {
  const body = header.nextElementSibling;
  const chevron = header.querySelector('.chevron');
  if (body.classList.contains('open')) {
    body.classList.remove('open');
    chevron.classList.remove('open');
  } else {
    body.classList.add('open');
    chevron.classList.add('open');
  }
}
// Expand sections with errors/warnings by default
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.comp-section').forEach(function(section) {
    if (section.querySelector('.check-fail, .check-warn')) {
      const body = section.querySelector('.comp-body');
      const chevron = section.querySelector('.chevron');
      body.classList.add('open');
      chevron.classList.add('open');
    }
  });
});
</script>
</body>
</html>""")

    return "\n".join(html)


# =============================================================================
# Main runner
# =============================================================================

def run_validation(netlist_path, output_dir):
    """Main validation runner."""
    components, nets = parse_netlist(netlist_path)

    # Build results for every component
    all_results = {}
    for comp_ref, comp in sorted(components.items()):
        comp_results = []
        categories = match_category(comp)
        has_part_rule = False

        # Run category-based checks
        for cat_name in categories:
            cat_checks = CATEGORY_RULES[cat_name]["checks"]
            comp_results.extend(run_category_checks(comp_ref, comp, cat_name, cat_checks, components, nets))

        # Run part-specific checks (if defined)
        for rule_name, rules in PART_RULES.items():
            if rule_name == comp.part or rule_name == comp.value:
                has_part_rule = True
                comp_results.extend(run_part_checks(comp_ref, comp, rules, components, nets))
                break

        all_results[comp_ref] = {
            "comp": comp,
            "categories": categories,
            "has_part_rule": has_part_rule,
            "results": comp_results,
        }

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Generate TXT report
    txt_path = os.path.join(output_dir, "validation_report.txt")
    txt_report, error_count = generate_txt_report(all_results, components, netlist_path)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(txt_report)
    print(txt_report)

    # Generate HTML report
    html_path = os.path.join(output_dir, "validation_report.html")
    html_report = generate_html_report(all_results, components, netlist_path)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_report)

    print(f"\nReports saved to:")
    print(f"  TXT:  {txt_path}")
    print(f"  HTML: {html_path}")

    return error_count


def main():
    parser = argparse.ArgumentParser(
        description="Validate KiCad netlist connections against datasheet rules."
    )
    parser.add_argument(
        "-n", "--netlist", required=True, help="Path to KiCad .net file"
    )
    parser.add_argument(
        "-o", "--output-dir", default="Reports",
        help="Output directory for reports (default: Reports)",
    )
    args = parser.parse_args()

    error_count = run_validation(args.netlist, args.output_dir)
    sys.exit(1 if error_count > 0 else 0)


if __name__ == "__main__":
    main()
