# Project Configuration

> Fill this in at project kickoff. It is the single source of truth for the project's
> tier, complexity, tooling, and key metadata. Referenced throughout the SOP.

## Project identity

| Field | Value |
|---|---|
| **Project name** | Swasthik KiBot Project |
| **Project code** | Swasthik_KiBot_Project |
| **Client** | <!-- sssssss --> |
| **Client technical contact** | <!-- Name, email, phone --> |
| **Client business contact** | <!-- Name, email, phone --> |
| **SOW reference** | <!-- SOW-YYYY-NNN --> |
| **Start date** | <!-- YYYY-MM-DD --> |
| **Target first-proto date** | <!-- YYYY-MM-DD --> |

## Service tier (from MSA Schedule A)

| Field | Value |
|---|---|
| **Service tier** | <!-- Professional / Validated / Assured --> |
| **Tier rationale** | <!-- Why this tier was sold. Client risk profile. --> |
| **Revisions included** | <!-- 2 (Professional) / 3 (Validated, Assured) --> |
| **Re-spin coverage** | <!-- Per tier definition in MSA Schedule A --> |
| **Bring-up support hours** | <!-- 4 / 8 / 16 per tier --> |

## Internal complexity classification (per SOP §5.4)

| Field | Value |
|---|---|
| **Complexity class** | <!-- Class A / Class B / Class C --> |
| **Layer count** | <!-- 2 / 4 / 6+ --> |
| **Impedance control** | <!-- None / USB only / Full / etc --> |
| **Wireless** | <!-- None / BLE / Wi-Fi / LoRa / etc --> |
| **EMC target** | <!-- None / CE Class B / FCC Part 15 / custom --> |
| **Temperature range** | <!-- Commercial / Industrial / Automotive --> |
| **Safety-critical?** | <!-- Yes / No (if yes, specify standard) --> |
| **Tier-complexity divergence?** | <!-- Yes / No. If yes, escalation status --> |

## Add-on services purchased (per MSA Schedule B)

List add-ons from the SOW. Delete lines that don't apply.

- [ ] Pre-compliance EMC testing
- [ ] Formal EMC compliance testing coordination
- [ ] EMC design review (Professional tier add-on)
- [ ] Compliance matrix
- [ ] Signal integrity (SI) simulation
- [ ] Power integrity (PI/PDN) analysis
- [ ] Thermal analysis (calculation / simulation)
- [ ] Design FMEA
- [ ] Stackup confirmation with specific fab house
- [ ] Long-term BOM monitoring
- [ ] Second-source qualification
- [ ] Pre-purchase BOM review
- [ ] Production support per batch
- [ ] Field failure investigation
- [ ] Schematic / layout audit of third-party design

## EDA tooling

| Field | Value |
|---|---|
| **Primary tool** | KiCad 9.x |
| **KiCad version (if KiCad)** | 9.0 |
| **Library source** | KiCad default + project-local (design/pcb/kicad/libraries/) |
| **CI automation path** | KiCad automated (KiBot + kicad-cli) |

## Target manufacturing

| Field | Value |
|---|---|
| **Target fab house** | <!-- JLCPCB / PCBWay / specific vendor --> |
| **Target assembly** | <!-- In-house / fab house / specific assembly vendor --> |
| **Prototype quantity** | <!-- 2 / 5 / 10 --> |
| **Target production volume** | <!-- One-off / pilot / volume / mass --> |
| **Stackup** | <!-- e.g., 6-layer 1.6mm FR4 HASL (see design/pcb/stackup.md) --> |
| **Impedance-controlled?** | <!-- Yes / No --> |

## Firmware co-design

| Field | Value |
|---|---|
| **Co-design required?** | <!-- Yes / No --> |
| **Firmware repo** | <!-- URL or path --> |
| **MCU family** | <!-- STM32F4 / ESP32 / nRF52 --> |
| **RTOS / platform** | <!-- Zephyr / bare-metal / FreeRTOS / ESP-IDF --> |
| **HW-FW milestone sync points** | <!-- List key handoffs --> |

## Team

| Role | Name | Notes |
|---|---|---|
| **PCB Design Engineer** | | Owner of the design files |
| **Peer Reviewer** | | Required for Validated; two reviewers required for Assured |
| **Tech Lead** | | Signs off at G1, G4, G5 |
| **QA / Release Owner** | | |
| **Library Owner** | | May be same as PCB Design Engineer |
| **Project Manager** | | |
| **Client contact** | | |

## Milestones

| # | Milestone | Target date | SOW amount | Status |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

## Key risks (initial)

Populated at G1 (Specification Lock). Maintained in `design/pcb/risk_register.md`.

1.
2.
3.

## Notes

<!-- Anything project-specific that doesn't fit the fields above. -->
