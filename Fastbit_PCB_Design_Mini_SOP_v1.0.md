# Fastbit PCB Design Mini SOP

> **Purpose:** This is the working day-to-day SOP for every PCB project Fastbit delivers. It is short on purpose. Every designer reads it once and then follows it on every project, regardless of board complexity, client size, or who is sitting in the chair.
>
> **Single rule that everything else exists to serve:** No PCB leaves Fastbit for fabrication without passing every review gate, with every required report on file, and with the founder's signoff on any gap.

| Field | Value |
|---|---|
| Document ID | SOP-HW-002 |
| Version | 1.0 |
| Status | Working |
| Scope | Every PCB project Fastbit delivers |
| Primary tool | KiCad |
| Issue tracking | Jira (HW- prefix) |
| Owner | Fastbit Embedded Technologies Pvt Ltd |
| Companion document | `Fastbit_PCB_Design_SOP_v1.0.md` (the bigger reference SOP, kept for tier-based commercial offerings, EMC depth, and edge cases) |

---

## How to use this document

Read it end to end once. Then keep it open on the side for every PCB project. Walk through the gates in order. Tick off the inlined checklists as you work. If you need to skip something, raise a waiver and email the founder before you push to fab.

The mini SOP is written for a small team that is still building experience. It deliberately leaves out tier classifications, complexity classes, and most of the policy machinery from the bigger SOP. There is one process. Every project follows it.

---

## 1. The non-negotiable promise

Every board Fastbit ships to fab has been:

1. Reviewed at five points in the design flow
2. Backed by every required report (ERC, DRC, BOM validation, DFM check)
3. Signed off by the designer and one other engineer wherever a second engineer exists
4. Released with a fab pack that another engineer could re-verify from scratch

If any of these is missing at the moment of fab release, the merge to `main` does not happen until the founder has approved the gap in writing. No exceptions.

---

## 2. Branching model

Three branches. No surprises.

| Branch | Purpose | Who pushes |
|---|---|---|
| `main` | Released, fab-ready designs only. Every commit is tagged. | Nobody pushes directly. Reaches main only via PR from `qa`. |
| `qa` | Pre-release validation. This is where the final pre-fab review gate (G4) and the fab release gate (G5) run. | Reached only via PR from `dev`. |
| `dev` | Active design work. Feature branches merge here. | Reached only via PR from feature branches. |

**Branch naming** (use `/fastbit-branch` to create):

```
feature/HW-123-power-section
feature/HW-124-mcu-schematic
feature/HW-125-layout-placement
feature/HW-126-routing
bugfix/HW-456-fix-uart-pinout
hotfix/HW-789-eco-reverse-polarity
release/hw-v1.0.0-revA
```

**Rules:**

1. Never push directly to `main`, `qa`, or `dev`. Always feature branch and PR.
2. Feature branches come from `dev`. Hotfixes and ECOs come from `main`.
3. The PR author does not self-merge. Another engineer reviews and approves. If no second engineer is on the project, the founder reviews.
4. Sync your branch with `dev` (or `qa` or `main` for hotfixes) before raising the PR. Re-run ERC and DRC after the rebase.
5. Never force push.
6. Delete the feature branch after merge.
7. After merging a hotfix to `main`, cherry-pick it to `dev` immediately so the fix is not lost.

---

## 3. Project folder structure

Every PCB project uses this layout. Create it on day one. Do not deviate.

```
projects/<client>-<project>/
└── design/
    └── pcb/
        ├── kicad/                  KiCad source files (.kicad_pro, .kicad_sch, .kicad_pcb)
        ├── outputs/                Gerber, drill, BOM exports per release
        ├── reports/                ERC, DRC, BOM validation reports per gate
        ├── reviews/                Completed gate checklists
        │   ├── g1_spec_lock/
        │   ├── g2_schematic/
        │   ├── g3_layout/
        │   ├── g4_pre_fab/
        │   └── g5_fab_release/
        ├── waivers/                Founder-approved waiver notes (see Section 9)
        ├── ecos/                   ECO documents
        ├── bring_up/               Post-fab bring-up evidence (scope shots, photos)
        ├── gate_log.md             Gate execution log (one section per gate)
        ├── stackup.md              Stackup decision and fab confirmation
        ├── bring_up_plan.md        Drafted at G4, executed post-fab
        └── release_notes.md        Drafted at G5
```

The `gate_log.md` is the at-a-glance status of the project. Every gate, every reviewer, every date, every outcome. Update it as you close each gate.

---

## 4. The five review gates

Five gates. Every project. No exceptions. Each gate has entry criteria, an inlined checklist, what evidence to file, and who signs off.

```
Requirements -> [G1] -> Schematic -> [G2] -> Placement+Routing -> [G3] -> Pre-fab -> [G4] -> [G5] -> Fab
```

For every gate:

- **Designer** runs the checklist as they work. Closes Critical and Major findings. Drafts a waiver for anything that cannot be closed.
- **Reviewer** (a second engineer, or the founder if no second engineer is available) opens the design, walks the checklist independently, and signs off.
- **Evidence** is committed to git in the appropriate `reviews/` or `reports/` subfolder before the PR is approved.
- **Severity:** Critical = blocks gate, must be fixed. Major = must be fixed or waived in writing. Minor = log and move on.

---

### Gate 1: Specification lock

**When:** Before any schematic work begins.

**Why this gate exists:** A schematic drawn on top of a vague spec produces a vague schematic. Lock the spec first and the rest of the project gets faster, not slower.

**Entry criteria:**

- Client requirements captured in `requirements_spec.md` in the project folder
- High-level block diagram showing major subsystems and signal flow
- Preliminary power budget (rails, currents, sequencing)
- Interface list (connectors, buses, mechanical interfaces)
- Mechanical envelope and mounting constraints known
- Target layer count estimated

**Checklist (Gate 1):**

| # | Item | P/F/W/N/A | Notes |
|---|---|---|---|
| 1.1 | Functional requirements written down with use cases and operating modes | | |
| 1.2 | Block diagram present and complete | | |
| 1.3 | Every external interface identified (USB, UART, sensors, wireless, etc.) with connector type and pinout |  | |
| 1.4 | Power input source and voltage range specified | | |
| 1.5 | Every output rail listed with voltage, current, and tolerance | | |
| 1.6 | Power sequencing rules noted if any | | |
| 1.7 | Battery chemistry, capacity and charging method specified (if battery powered) | | |
| 1.8 | Board dimensions, mounting holes, enclosure type known | | |
| 1.9 | Operating and storage temperature range defined | | |
| 1.10 | Target regulatory markets identified (CE, FCC, India, none) | | |
| 1.11 | Responsibility for formal compliance testing is documented (Fastbit advisory only vs client owns) | | |
| 1.12 | Target fab house and assembly house known or marked TBD with deadline | | |
| 1.13 | Prototype quantity and rough production volume estimated | | |
| 1.14 | MCU family selected and programming/debug interface defined (SWD / JTAG / UART boot) | | |
| 1.15 | Hardware-firmware interface contract drafted (which signal on which pin) | | |
| 1.16 | Top 5 technical, schedule, supply-chain risks listed in `risk_register.md` | | |
| 1.17 | Scope-in, scope-out, and client responsibilities written down | | |
| 1.18 | All TBD items on critical interfaces have a deadline and an owner | | |

**Blocking defects:** Missing fundamental interface definition, no power budget, no mechanical envelope, infeasible requirement.

**Exit criteria:** Every Critical and Major item closed. TBD items on critical interfaces resolved. Stackup approach selected. Spec signed off.

**Evidence to commit (in `reviews/g1_spec_lock/`):** completed checklist, signed-off requirements spec, block diagram, preliminary BOM (key components), risk register, gate_log entry.

**Sign-off:** Designer + one other engineer. If no second engineer, founder.

---

### Gate 2: Schematic review

**When:** Schematic capture complete, ERC clean, before any layout work starts.

**Why this gate exists:** Catching a missing decoupling cap on the schematic costs minutes. Catching it after the board is fabricated costs weeks and money.

**Entry criteria:**

- Every sheet populated, no placeholder blocks
- ERC passing with zero errors; warnings reviewed and resolved or explicitly suppressed with comment
- Every component has a manufacturer part number and footprint assigned
- Power architecture complete with rails, sequencing, enable signals defined
- All external interfaces fully connected with protection (ESD, polarity, overcurrent)
- Reset and boot logic defined and verified
- Debug and programming interfaces present
- Decoupling capacitors placed on every IC power pin
- BOM export matches schematic component count

**Checklist (Gate 2 — schematic review):**

| # | Item | P/F/W/N/A | Notes |
|---|---|---|---|
| **Power architecture** | | | |
| 2.1 | Every voltage rail has a clearly identified source (regulator, battery, external) | | |
| 2.2 | Every IC load has a rail at correct voltage per datasheet | | |
| 2.3 | Bulk decoupling cap on each rail (value per regulator datasheet) | | |
| 2.4 | HF decoupling (100 nF or per datasheet) at every IC power pin | | |
| 2.5 | Regulator output cap type matches stability requirement (ceramic / tantalum / polymer) | | |
| 2.6 | Regulator enable pin is driven or tied (not floating) | | |
| 2.7 | Power good / reset output is connected to MCU reset logic if present | | |
| 2.8 | Power sequencing verified where rails must come up in order | | |
| 2.9 | Power budget per rail is within regulator capability | | |
| 2.10 | Reverse polarity protection on external power inputs | | |
| 2.11 | Overcurrent / fuse protection where required | | |
| 2.12 | TVS / transient protection on power inputs exposed to surges | | |
| 2.13 | Test point on every power rail | | |
| 2.14 | Switching regulator feedback network values verified | | |
| 2.15 | LDO dropout sufficient for worst-case input | | |
| 2.16 | LDO thermal dissipation within package rating | | |
| **Reset, clock, boot** | | | |
| 2.17 | Reset circuit has filter cap and pull-up per MCU datasheet, correct polarity | | |
| 2.18 | Crystal load caps match crystal spec | | |
| 2.19 | Boot strapping pins in correct state at power-on | | |
| 2.20 | Boot mode selection consistent with firmware plan | | |
| **MCU and main IC** | | | |
| 2.21 | Every MCU pin is connected, tied, or explicitly no-connect with note | | |
| 2.22 | Every VDD/VSS pin pair present and decoupled | | |
| 2.23 | VDDA filtered from VDD (ferrite + cap, or per datasheet) | | |
| 2.24 | VREF filtered and referenced to analog ground | | |
| 2.25 | SWD / JTAG header broken out, standard pinout | | |
| 2.26 | Programming pins not shared with critical application signals | | |
| **Communication interfaces** | | | |
| 2.27 | UART TX/RX crossover verified against external device, level translation if needed | | |
| 2.28 | SPI CS polarity correct, pull-up for boot default | | |
| 2.29 | I2C pull-ups present and sized for bus capacitance | | |
| 2.30 | I2C addresses checked, no conflicts | | |
| 2.31 | USB D+/D- correctly routed (no swap), ESD protection present | | |
| 2.32 | CAN / RS-485 termination present | | |
| 2.33 | Wireless module antenna path is RF-correct, antenna keep-out marked for layout | | |
| **Connectors** | | | |
| 2.34 | Connector pinouts verified line by line against the mating device spec | | |
| 2.35 | Polarity / keying prevents reverse insertion | | |
| 2.36 | Power pins rated for expected current | | |
| 2.37 | ESD protection on every cable-connected signal pin | | |
| **Protection** | | | |
| 2.38 | ESD protection on every external-accessible I/O | | |
| 2.39 | TVS / zener ratings appropriate for bus voltage | | |
| 2.40 | Creepage and clearance planned for high-voltage sections | | |
| **Test and debug** | | | |
| 2.41 | Test points on critical signals (clocks, reset, boot, debug UART) | | |
| 2.42 | Power LED present | | |
| 2.43 | LED current-limit resistors correct value | | |
| **BOM and components** | | | |
| 2.44 | Every symbol has manufacturer part number and footprint | | |
| 2.45 | Capacitor voltage ratings at least 2x applied voltage | | |
| 2.46 | MLCC DC bias derating considered for power rails | | |
| 2.47 | Resistor power ratings adequate | | |
| 2.48 | Inductor saturation current exceeds peak | | |
| 2.49 | MOSFET VDS, ID, RDS(on) appropriate | | |
| 2.50 | No EOL / NRND parts without documented justification | | |
| 2.51 | Every critical component has at least one documented alternate | | |
| **General** | | | |
| 2.52 | Net names are descriptive (e.g., `VCC_3V3`, not `N1`) | | |
| 2.53 | Title block has project, revision, date, author | | |
| 2.54 | ERC report clean, all warnings reviewed | | |
| 2.55 | The board can be powered up step by step if needed (isolation jumpers / staged rails) | | |
| 2.56 | The MCU can be programmed without any other component working | | |

**Blocking defects:** Wrong pin connected, polarity-sensitive component reversed, missing power rail to any IC, missing ground, missing bulk capacitance, wrong voltage to an IC, missing ESD on external interface.

**Evidence to commit (in `reviews/g2_schematic/`):** completed checklist, ERC report (clean), schematic PDF export, BOM CSV, findings list with resolution, gate_log entry.

**Sign-off:** Designer + one other engineer. PR merges to `dev` only after sign-off.

---

### Gate 3: Layout review

**When:** Routing more than 90% complete, before final DRC cleanup.

**Why this gate exists:** Placement mistakes are very expensive to fix after routing. Catch them now.

**Entry criteria:**

- Gate 2 passed
- Component placement complete
- Stackup defined and matches what was assumed at G1
- Routing > 90% complete
- Power and ground planes poured
- Critical signals routed
- Mechanical constraints met (mounting holes, connector positions, board outline, keep-outs)
- 3D render generated and matches mechanical expectations

**Checklist (Gate 3 — layout review):**

| # | Item | P/F/W/N/A | Notes |
|---|---|---|---|
| **Board outline and mechanical** | | | |
| 3.1 | Board outline matches mechanical drawing | | |
| 3.2 | Mounting holes correct size and position, with keep-out for hardware | | |
| 3.3 | Board edge keep-out (0.5–1 mm) observed, no copper too close to edge | | |
| 3.4 | Fiducials present (minimum 3, asymmetric) | | |
| **Connectors** | | | |
| 3.5 | Connectors positioned per mechanical drawing | | |
| 3.6 | Cable entry clearance adequate for mating connector + strain relief | | |
| **Power placement** | | | |
| 3.7 | Switching converters have short, tight switching loops | | |
| 3.8 | Bulk input/output caps close to converter pins | | |
| 3.9 | HF decoupling caps right at IC power pins (under 1 mm where possible) | | |
| 3.10 | Feedback network short and close to feedback pin | | |
| 3.11 | Inductors oriented to minimise coupling to sensitive circuits | | |
| 3.12 | Heat-dissipating components have room for thermal vias and pours | | |
| **MCU and IC placement** | | | |
| 3.13 | MCU placed to minimise sum of critical signal lengths | | |
| 3.14 | Every MCU power pin has its HF decoupling cap immediately adjacent | | |
| 3.15 | MCU ground pads connected to ground plane via short vias | | |
| **Crystal and clock** | | | |
| 3.16 | Crystal placed within 5–10 mm of MCU oscillator pins | | |
| 3.17 | Continuous ground plane directly under the crystal | | |
| 3.18 | No high-speed or switching signals route under the crystal | | |
| **Analog and wireless (if present)** | | | |
| 3.19 | Analog components grouped together, separated from digital | | |
| 3.20 | Reference voltage sources placed close to ADC / DAC | | |
| 3.21 | Wireless module placed near board edge with antenna clearance | | |
| 3.22 | Antenna keep-out observed (no ground pour, traces, or components) | | |
| **Thermal** | | | |
| 3.23 | Hot components separated from thermally sensitive components | | |
| **Test and debug access** | | | |
| 3.24 | Power rail test points accessible during bring-up | | |
| 3.25 | Debug header on top side, accessible, cable can exit cleanly | | |
| **3D and mechanical fit** | | | |
| 3.26 | 3D model generated and reviewed | | |
| 3.27 | All components fit within enclosure envelope | | |
| 3.28 | Connectors align with enclosure openings | | |
| 3.29 | No collision with standoffs or mounting hardware | | |
| **Power distribution routing** | | | |
| 3.30 | Power traces wide enough for current (IPC-2221 or fab rec) | | |
| 3.31 | Polygon pours used for high-current paths where possible | | |
| 3.32 | Multiple vias on high-current paths > 1 A | | |
| 3.33 | Switching regulator input/output loop areas minimised | | |
| 3.34 | HF decoupling has short loops (cap pad to IC power pin to IC ground pin to cap pad) | | |
| **Ground and plane integrity** | | | |
| 3.35 | Continuous ground plane on the designated reference layer | | |
| 3.36 | No unintended splits or slots in the ground plane under high-speed signals | | |
| 3.37 | Plenty of ground vias near high-speed signal vias (stitching) | | |
| 3.38 | No floating plane islands or slivers | | |
| **High-speed routing** | | | |
| 3.39 | Every high-speed signal has a continuous reference plane beneath its length | | |
| 3.40 | Trace width matches stackup impedance calculation | | |
| 3.41 | Differential pairs routed parallel with constant spacing, length matched within tolerance | | |
| 3.42 | Layer changes on high-speed signals have return vias close by | | |
| 3.43 | No stubs on high-speed signals | | |
| 3.44 | 45° or curved bends on high-speed (no 90° turns) | | |
| 3.45 | USB D+/D- length matched and impedance controlled | | |
| **Clock routing** | | | |
| 3.46 | Clock traces short, with continuous ground reference | | |
| 3.47 | Clock traces separated from sensitive signals | | |
| **Analog routing** | | | |
| 3.48 | Analog traces short, direct, do not cross switching nodes | | |
| **ESD and protection routing** | | | |
| 3.49 | ESD devices placed at the connector (first component the signal sees) | | |
| 3.50 | ESD device ground path short and direct | | |
| **Silkscreen** | | | |
| 3.51 | Every component has reference designator on silk | | |
| 3.52 | Silkscreen does not overlap pads | | |
| 3.53 | Polarity markers on polarised components | | |
| 3.54 | Pin 1 indicator on all multi-pin ICs | | |
| 3.55 | Board name, revision letter, date printed on the board | | |
| **Preliminary DRC** | | | |
| 3.56 | Preliminary DRC run, results reviewed, remaining errors understood | | |
| 3.57 | Net classes assigned with sensible constraints | | |

**Blocking defects:** Signal returns over plane split, high-current path undersized, impedance-controlled signal without reference plane, unrouted net, decoupling loop significantly longer than IC datasheet maximum, component outside mechanical envelope.

**Evidence to commit (in `reviews/g3_layout/`):** completed checklist, 3D render, layer-by-layer screenshots of critical areas, plane integrity screenshots with reference plane highlighted for each high-speed net, length matching report (if applicable), thermal calculation, gate_log entry.

**Sign-off:** Designer + one other engineer.

---

### Gate 4: Pre-fabrication review

**When:** Layout finalised, all DRC and ERC errors resolved, before assembling the fab pack.

**Why this gate exists:** Last chance to catch problems before money is spent on fab and assembly.

**Entry criteria:**

- Gate 3 passed
- DRC clean (zero errors, zero unwaived warnings)
- ERC clean (zero errors)
- BOM finalised with availability confirmed
- Fabrication drawing prepared (stackup, material, surface finish, tolerances, impedance, board notes)
- Assembly drawing prepared
- Pick-and-place file generated
- 3D render final

**Checklist (Gate 4 — DFM):**

| # | Item | P/F/W/N/A | Notes |
|---|---|---|---|
| **Trace width and spacing** | | | |
| 4.1 | Minimum trace width >= fab capability (typical 5 mil) | | |
| 4.2 | Minimum trace spacing >= fab capability | | |
| 4.3 | Power traces sized for current (IPC-2221) | | |
| 4.4 | Spacing at high voltages meets creepage / clearance | | |
| **Vias** | | | |
| 4.5 | Minimum via drill >= fab capability (typical 0.25–0.30 mm) | | |
| 4.6 | Annular ring >= fab capability (typical 4–5 mil) | | |
| 4.7 | Aspect ratio (board thickness / drill) <= fab limit (typically 8:1) | | |
| 4.8 | Blind / buried vias explicitly specified in fab drawing if used | | |
| **Solder mask** | | | |
| 4.9 | Solder mask web between pads >= fab capability (typical 4 mil) | | |
| 4.10 | Solder mask expansion specified | | |
| 4.11 | Solder mask color specified | | |
| **Silkscreen** | | | |
| 4.12 | Minimum text height >= fab capability (typical 0.8 mm) | | |
| 4.13 | No silkscreen on pads | | |
| 4.14 | Reference designators present for every component | | |
| **Board outline** | | | |
| 4.15 | Board outline closed contour on Edge.Cuts layer | | |
| 4.16 | Edge clearance >= 0.2 mm | | |
| 4.17 | Board dimensions within fab panel capability | | |
| 4.18 | Board thickness matches stackup spec | | |
| **Panelisation (if applicable)** | | | |
| 4.19 | Panelisation specified or explicitly deferred to fab | | |
| 4.20 | V-score / mouse-bite dimensions specified | | |
| 4.21 | Panel fiducials present | | |
| **Copper balance** | | | |
| 4.22 | Copper coverage on each layer > 30% (or balanced) to prevent warping | | |
| **Drill file** | | | |
| 4.23 | Drill file in Excellon format | | |
| 4.24 | Plated and non-plated drills separated | | |
| **Fabrication drawing** | | | |
| 4.25 | Stackup, material, Tg specified | | |
| 4.26 | Surface finish specified (HASL / ENIG / OSP) | | |
| 4.27 | Solder mask and silkscreen colors specified | | |
| 4.28 | Copper weight per layer specified | | |
| 4.29 | Impedance control notes with target values (if applicable) | | |
| 4.30 | IPC class specified (Class 2 typical) | | |
| **Gerber output** | | | |
| 4.31 | All copper layers exported | | |
| 4.32 | Solder mask, silkscreen, paste, drill, edge cuts exported | | |
| 4.33 | Gerbers open and display correctly in an independent viewer (gerbv) | | |
| 4.34 | Gerber format is RS-274X | | |

**Checklist (Gate 4 — BOM validation):**

| # | Item | P/F/W/N/A | Notes |
|---|---|---|---|
| 4.35 | Every schematic component appears in the BOM | | |
| 4.36 | Every BOM row has reference designator, value, footprint, MFR, MPN, qty | | |
| 4.37 | DNP components clearly marked | | |
| 4.38 | BOM row count matches schematic count | | |
| 4.39 | Every MPN verified to exist on a distributor site | | |
| 4.40 | MPN package matches schematic symbol footprint | | |
| 4.41 | Every component checked for lifecycle (Active / NRND / EOL / Obsolete) | | |
| 4.42 | EOL / NRND parts have justification and replacement plan | | |
| 4.43 | Lead time checked for every component, > 8 weeks flagged | | |
| 4.44 | Every critical component has at least one alternate | | |
| 4.45 | Single-source components explicitly identified and risk-assessed | | |
| 4.46 | Capacitor voltage ratings >= 2x applied voltage | | |
| 4.47 | MLCC DC bias derating considered for power rails | | |
| 4.48 | Resistor power dissipation <= 50% of rated | | |
| 4.49 | Inductor saturation current >= peak circuit current | | |
| 4.50 | Operating temperature range covers board environment | | |
| 4.51 | RoHS compliance verified if required | | |
| 4.52 | BOM committed to git alongside design files | | |

**EMC sanity check (compressed):** Fastbit does design-stage EMC review only. Formal compliance is the client's responsibility unless contracted separately. At Gate 4, the reviewer walks the layout once with EMC eyes — return paths continuous under high-speed signals, ground stitching around clocks and switching converters, ESD on every cable-connected interface, common-mode chokes where the application asks for them. Findings go in the same checklist. Release notes must say: "Preventive EMI/EMC design review completed. Formal compliance is the client's responsibility per the SOW." Never write "EMC compliant" or "passes CE/FCC" unless an accredited lab actually tested it.

**Blocking defects:** DRC error unresolved, fab capability violated, critical EMI error (no ground plane under clock), critical component EOL with no alternate, solderability failure.

**Evidence to commit (in `reviews/g4_pre_fab/`):** DFM checklist, BOM validation checklist, DRC report (clean), ERC report (clean), fabrication drawing PDF, assembly drawing PDF, pick-and-place CSV, stackup confirmation from fab (if impedance-controlled), gate_log entry.

**Sign-off:** Designer + one other engineer.

---

### Gate 5: Fabrication release

**When:** Gate 4 has passed. The branch is on `qa`. Files are about to be sent to the fab house. **This is the last gate before money is spent.**

**Why this gate exists:** Verify the release pack is complete, consistent, and traceable. Catch missing files now, not after the fab emails to ask.

**Entry criteria:**

- Gates 1, 2, 3, 4 all passed and signed off
- Release pack assembled (see checklist below)
- Release notes drafted with residual risks
- Tag prepared

**Checklist (Gate 5 — fabrication release):**

| # | Item | P/F/W/N/A | Notes |
|---|---|---|---|
| **Gate prerequisites** | | | |
| 5.1 | G1 spec lock signed off | | |
| 5.2 | G2 schematic review signed off | | |
| 5.3 | G3 layout review signed off | | |
| 5.4 | G4 pre-fab review signed off (DFM + BOM) | | |
| 5.5 | All Critical findings resolved across all gates | | |
| 5.6 | All Major findings resolved or formally waived (founder approval on file) | | |
| **Gerbers** | | | |
| 5.7 | Top and bottom copper Gerbers present | | |
| 5.8 | Inner copper layers present (4+ layer boards) | | |
| 5.9 | Top and bottom solder mask present | | |
| 5.10 | Top and bottom silkscreen present | | |
| 5.11 | Top and bottom solder paste present | | |
| 5.12 | Board outline (Edge.Cuts) present | | |
| 5.13 | Gerber format is RS-274X | | |
| 5.14 | Gerbers open cleanly in an independent viewer (gerbv) | | |
| 5.15 | Gerbers spot-checked against the 3D render | | |
| **Drill** | | | |
| 5.16 | Excellon drill file present | | |
| 5.17 | Plated and non-plated drills separated | | |
| **BOM** | | | |
| 5.18 | BOM CSV present with all mandatory columns | | |
| 5.19 | BOM row count matches schematic | | |
| 5.20 | DNP components marked | | |
| **Assembly** | | | |
| 5.21 | Assembly drawing PDF present, top and bottom views | | |
| 5.22 | Assembly drawing shows reference designators, pin 1, polarity, DNP | | |
| 5.23 | Pick-and-place CSV present with X, Y, rotation, layer per component | | |
| 5.24 | Pick-and-place excludes DNP | | |
| **Fab drawing** | | | |
| 5.25 | Fab drawing PDF present | | |
| 5.26 | Stackup, material, copper weight, surface finish, mask/silk colors specified | | |
| 5.27 | Impedance control notes present (if applicable) | | |
| 5.28 | IPC class specified | | |
| 5.29 | Fab drawing stackup matches layout stackup | | |
| **Reference files** | | | |
| 5.30 | Schematic PDF included | | |
| 5.31 | 3D render included | | |
| 5.32 | Native KiCad source files committed to git | | |
| **Reports and evidence** | | | |
| 5.33 | DRC report (clean) included | | |
| 5.34 | ERC report (clean) included | | |
| 5.35 | Completed G2 schematic review checklist archived | | |
| 5.36 | Completed G3 layout review checklist archived | | |
| 5.37 | Completed G4 DFM checklist archived | | |
| 5.38 | Completed G4 BOM validation checklist archived | | |
| 5.39 | Gate log updated with all five gate outcomes | | |
| **Version control** | | | |
| 5.40 | Release commit is on `main` branch | | |
| 5.41 | Annotated git tag created (`hw-vX.Y.Z-rev<L>`) | | |
| 5.42 | Tag message includes release type, reviewers, gates passed, residual risks | | |
| 5.43 | Tag pushed to origin | | |
| 5.44 | Release pack archived in `projects/<project>/deliverables/hw-vX.Y.Z-rev<L>/` | | |
| **Release notes** | | | |
| 5.45 | `release_notes.md` present | | |
| 5.46 | Summary of the release written | | |
| 5.47 | Changes from previous revision listed (if not first release) | | |
| 5.48 | Known residual risks listed | | |
| 5.49 | Open known issues listed | | |
| 5.50 | Compliance status statement present (preventive EMC review only, formal compliance is client responsibility) | | |
| 5.51 | Contact for questions named | | |
| **Spot check** | | | |
| 5.52 | Open the Gerber archive in an independent viewer and compare against the 3D render | | |
| 5.53 | Open the BOM, pick 3 random components, verify they match the schematic | | |
| 5.54 | Verify the revision letter on silkscreen matches the release tag | | |

**Tag message format:**

```
Release hw-v1.0.0-revA

Release type: Prototype
Fab house: <name>
Stackup: 4-layer 1.6 mm FR4 HASL
Approved by: <reviewer name>
Date: YYYY-MM-DD

Summary:
<1-3 line summary>

Gates passed:
- Gate 1: Specification lock (YYYY-MM-DD)
- Gate 2: Schematic review (YYYY-MM-DD)
- Gate 3: Layout review (YYYY-MM-DD)
- Gate 4: Pre-fab review (YYYY-MM-DD)
- Gate 5: Fab release (YYYY-MM-DD)

Known residual risks:
- <risk 1>
- <risk 2>

Compliance status:
- EMC: preventive design review only; client responsible for formal compliance
```

**Sign-off:** Designer + one other engineer. **And** the founder for any waivers (Section 9). The merge from `qa` to `main` does not happen until both signatures are in place.

---

## 5. Versioning and tagging

**Format:** `hw-vX.Y.Z-rev<L>`

- `X.Y.Z` is semantic version
- `<L>` is the industry-standard revision letter (A, B, C, ..., skip I, O, Q)
- Examples: `hw-v1.0.0-revA`, `hw-v1.1.0-revB`, `hw-v2.0.0-revC`

**Rules:**

1. A new revision letter for any change that requires new fabrication
2. The revision letter must appear on the silkscreen of every board
3. Tags are annotated and pushed
4. Major (X) bump = significant design change. Minor (Y) = ECO or feature. Patch (Z) = BOM-only or doc-only change with no Gerber regen.

---

## 6. The QA-to-main merge gate

This is the moment Gerbers are about to leave Fastbit. Treat it accordingly.

The QA holder (the engineer who owns the `qa` branch for this release) must verify all of the following before approving the PR from `qa` to `main`:

1. **All five gates closed.** The gate log shows G1, G2, G3, G4, G5 all PASSED with reviewer names and dates. No gate is in WAIVED state without a founder-approved waiver note in `waivers/`.
2. **All required reports present and clean.** ERC clean, DRC clean, BOM validation complete, DFM complete. All committed under `reports/`.
3. **All checklists signed off.** G2, G3, G4 (DFM + BOM), G5 — all under `reviews/`. Reviewer names and dates filled in.
4. **Release pack complete.** The Gate 5 checklist (Section 4) is fully ticked. The pack lives at `projects/<project>/deliverables/hw-vX.Y.Z-rev<L>/`.
5. **Spot check done.** Open the Gerbers in gerbv. Compare against the 3D render. Open the BOM, pick three components at random, confirm they match the schematic. Confirm the revision letter on silkscreen matches the tag.
6. **Release notes drafted.** Residual risks listed. Compliance statement present. Contact named.
7. **Tag prepared and message drafted.** Tag is annotated and follows the format in Section 4 G5.
8. **Waivers (if any) approved.** Every skipped item from any gate has a corresponding waiver file in `waivers/` with the founder's approval (Section 9).

**If any of the above is missing, the QA holder does not approve the merge.** The branch goes back. Either the missing item is produced, or the designer raises a waiver and gets the founder's signoff.

When all eight items are satisfied, the QA holder approves the PR, the merge to `main` happens, the tag is pushed, the Gerbers are uploaded to the fab house, and the release pack is marked sent in the gate log.

---

## 7. ECO process

For post-release fixes that are too small to be a full revision but still require new fabrication.

**When to use ECO:**

- Post-release issue found in a prototype or production board
- Small, targeted change (one trace, one component, one footprint)
- No new architecture work

**Process:**

1. Branch from `main`: `hotfix/HW-789-eco-description`
2. Open an ECO record in `projects/<project>/design/pcb/ecos/eco_<nnn>.md` with: ECO number, revision being changed, issue, fix, affected areas, validation plan, firmware impact
3. Make the change
4. Run a Gate 2 mini-review on the changed schematic area only
5. Run a Gate 4 mini-review on the changed layout area only (DRC and ERC on the whole board, not just the changed area)
6. Run Gate 5 release: merge to `main`, tag with new revision letter, generate updated release pack
7. Cherry-pick the ECO commit to `dev` so it does not get lost
8. Update the ECO register: one line per ECO

If multiple ECOs accumulate, they can be rolled into one fabrication release. Reviewed together at Gate 4.

---

## 8. Early-error-catch toolbelt

These are the tools every PCB designer at Fastbit should be using to catch errors before they reach a review gate. The point of the toolbelt is to make Gate 2, 3, and 4 reviews productive — the reviewer should be looking at design judgement calls, not at things a tool would have caught for free.

| Tool | What it catches | How to use |
|---|---|---|
| `kicad-cli sch erc` | Connectivity errors, unconnected pins, conflicting drivers, missing power | Run on every commit. Must be clean before pushing. |
| `kicad-cli pcb drc` | Clearance violations, trace width issues, via spacing, annular ring | Run on every layout commit. Must be clean before raising the G3 PR. |
| `kicad-cli sch export bom` | Drift between schematic and BOM, missing footprints, missing MPNs | Export the BOM after every schematic change. Diff against the previous version. |
| `kicad-cli sch export pdf` and `kicad-cli pcb export pdf` | Reviewable artifacts for PRs (text diffs of `.kicad_pcb` are not human readable) | Export PDF for every PR that touches schematic or layout. Attach to the PR. |
| KiCad ngspice simulator | Analog circuits, power converter compensation, filter response, op-amp stability | Use for any analog or power circuit before committing. Save the simulation file alongside the schematic. |
| KiCad 3D viewer + STEP export | Mechanical fit, component height, connector alignment, collision with standoffs | Check the 3D view at G3. Export STEP and hand to the mechanical engineer. |
| KiCad impedance calculator (Saturn PCB Toolkit as alternate) | Trace width for controlled impedance, current capacity, via current capacity | Use before routing high-speed or high-current traces. Save the calculation in `stackup.md`. |
| KiBot | Fully scripted release pack generation (Gerbers, drill, BOM, PDFs, 3D render, ERC, DRC) | Script the release pack so it is reproducible. Run it from CI. |
| kidiff | Visual PCB diff between two commits or two revisions | Use for ECOs and revision bumps. Attach the visual diff to the PR. |
| InteractiveHtmlBom | Searchable HTML BOM for the assembly house | Generate at Gate 5. Include in the release pack. |
| Pre-commit hooks | ERC and DRC fail at commit time, not at PR time | Set up `.pre-commit-config.yaml` in every project. |
| AI-assisted review (Claude, etc.) | Missing protections, missing decoupling, unusual patterns, BOM lifecycle gaps, checklist completeness | Feed AI the actual schematic PDF, BOM CSV, ERC report, DRC report. AI output is **input** to the reviewer, not a substitute. The reviewer signs the checklist. AI signs nothing. The engineer must be able to explain every design choice in their own words; "AI suggested it" is not a valid answer at any review gate. |

**The discipline:** Run every applicable tool before opening a PR. The PR description states which tools were run and links to the artifacts. A PR that arrives with unclean ERC or DRC is closed without review.

---

## 9. Skip-gate accountability

Sometimes a gate item, a sub-review, or an entire gate cannot be run as written. The reason might be legitimate (a check does not apply to this board, the second engineer is unavailable, the fab house cannot meet a normally required spec). The reason might be expedient (the schedule is tight, the client is pushing). Either way, **skipping is allowed only with a written waiver and the founder's signoff.**

**The waiver process:**

1. The designer writes a waiver note in `projects/<client>-<project>/design/pcb/waivers/<gate>_<YYYY-MM-DD>_<short-name>.md` with the following content:

   ```markdown
   # Waiver: <short title>

   - **Date:** YYYY-MM-DD
   - **Project:** <project>
   - **Gate:** G1 / G2 / G3 / G4 / G5
   - **Item being skipped:** <checklist item or sub-review or gate>
   - **Why it cannot be done as written:** <one or two paragraphs of honest explanation>
   - **What residual risk this creates:** <what could go wrong because of the skip>
   - **What we are doing to mitigate:** <if anything>
   - **What we are NOT doing because of the skip:** <be explicit>
   - **Requested by:** <designer name>
   - **Approved by:** <founder name>
   - **Approval date:** <YYYY-MM-DD>
   - **Approval medium:** email / written note / commit signature
   ```

2. The designer emails the founder (or sends a written note) with a link to the waiver file and a one-paragraph summary. No verbal approvals.

3. The founder reads the waiver, asks questions if needed, and replies with approval or rejection. Approval is captured in the `Approved by` and `Approval date` fields and the waiver is committed to git.

4. The waiver lives in the project repo forever. It appears in the gate log entry for that gate. It appears in the release notes under known residual risks.

**Hard rules:**

- No waiver, no skip. The merge from `qa` to `main` does not happen.
- The waiver must say *what* is being skipped, *why*, and *what risk* it creates. "We did not have time" is acceptable as a reason as long as the residual risk is honest.
- The waiver is approved by the founder, in writing, before the merge. Not after.
- Critical defects cannot be waived. They are fixed or the project does not ship.

The point of this process is not to make waivers difficult. The point is to make them **visible**. If we ship a board with a known gap, the gap is documented, the founder accepted it, and the team can learn from it.

---

## 10. PCB CI gate

Every push to `dev`, `qa`, or `main` runs an automated check. The check fails the build if anything is missing.

**Checks (blocking):**

1. ERC report generation passes
2. DRC report generation passes
3. BOM export generation passes
4. ERC finds zero errors
5. DRC finds zero errors

**Minimal GitHub Actions workflow:**

```yaml
name: PCB CI Gate
on:
  push:
    branches: [dev, qa, main]
  pull_request:
    branches: [dev, qa, main]

jobs:
  pcb-checks:
    runs-on: ubuntu-latest
    container: kicad/kicad:8.0
    steps:
      - uses: actions/checkout@v4
      - name: Run ERC
        run: kicad-cli sch erc --output erc_report.txt --exit-code-violations project.kicad_sch
      - name: Run DRC
        run: kicad-cli pcb drc --output drc_report.txt --exit-code-violations project.kicad_pcb
      - name: Export BOM
        run: kicad-cli sch export bom --output bom.csv project.kicad_sch
      - name: Archive reports
        uses: actions/upload-artifact@v4
        with:
          name: pcb-ci-reports
          path: |
            erc_report.txt
            drc_report.txt
            bom.csv
```

The artifacts are downloaded by the reviewer and committed to the project's `reports/` folder at gate time. The CI gate is a safety net; it does not replace the reviewer's checklist walk-through.

---

## 11. Post-fabrication bring-up

After the boards arrive from the fab and assembly house. Compressed bring-up checklist. Findings feed back into the next revision.

**Checklist (post-fab bring-up):**

| # | Item | P/F | Notes |
|---|---|---|---|
| **Visual** | | | |
| 11.1 | Board outline matches spec | | |
| 11.2 | Silkscreen readable, revision letter matches release | | |
| 11.3 | Surface finish clean, no obvious fab defects | | |
| 11.4 | Component count matches BOM, orientations correct | | |
| 11.5 | Solder joints look good (no cold joints, bridges, tombstones) | | |
| **Initial power-on (current limited)** | | | |
| 11.6 | Bench supply set with current limit (start at 100 mA) | | |
| 11.7 | Apply power, monitor current — within expected range | | |
| 11.8 | No smoke, no hot components, no smell | | |
| 11.9 | Power LED illuminates | | |
| **Power rails** | | | |
| 11.10 | Each rail measured: voltage and ripple within spec | | |
| 11.11 | Sequencing correct, all rails stable before MCU reset releases | | |
| 11.12 | Scope shots of each rail captured in `bring_up/` | | |
| **Clock and reset** | | | |
| 11.13 | Main crystal starts and runs at correct frequency | | |
| 11.14 | Reset signal correct at power-on | | |
| **Programming** | | | |
| 11.15 | Debug probe connects, MCU ID reads correctly | | |
| 11.16 | Can program flash and verify | | |
| **Communication** | | | |
| 11.17 | UART debug console echoes correctly | | |
| 11.18 | SPI / I2C / CAN / USB / Ethernet / wireless interfaces work as required | | |
| **Peripherals** | | | |
| 11.19 | GPIO, ADC, DAC, timers, PWM, sensors return plausible values | | |
| **Thermal** | | | |
| 11.20 | No components exceed datasheet temperature under load | | |
| 11.21 | No unexpected hot spots on thermal camera | | |
| **Functional** | | | |
| 11.22 | Application-level functions work as specified | | |

**Issues found:** Every issue gets a Jira HW- ticket and a category: Design (should have been caught at G2/G3/G4), Assembly (assembly house responsibility), Component (supplier defect), or Spec (should have been caught at G1).

**Learning loop:** For every Design or Spec issue, ask: which checklist item could have caught this? Was the item present? If not, add it to the relevant gate checklist in this document. Every project makes the SOP a little better.

**Bring-up evidence:** Scope shots, thermal images, photos of any issue, all committed under `bring_up/`. Bring-up log written in `bring_up_log.md` with date, revision, tester, and outcomes.

---

## 12. Quick reference: pre-fab evidence pack

Single list. Every item must exist on disk and be committed to git before the QA holder approves the merge from `qa` to `main`. The Gate 5 checklist is the long-form version of this list; this is the at-a-glance for the QA holder.

```
projects/<client>-<project>/design/pcb/
├── reports/
│   ├── erc_report.txt              clean
│   ├── drc_report.txt              clean
│   └── bom_validation_report.md    complete
├── reviews/
│   ├── g1_spec_lock/                signed
│   ├── g2_schematic/                signed
│   ├── g3_layout/                   signed
│   ├── g4_pre_fab/
│   │   ├── dfm_checklist.md         signed
│   │   └── bom_validation.md        signed
│   └── g5_fab_release/              signed
├── waivers/                          founder-approved if any gate item was skipped
├── outputs/<release>/
│   ├── gerbers/                     all layers
│   ├── drill/                       Excellon, plated and non-plated
│   ├── bom.csv
│   ├── pick_and_place.csv
│   ├── assembly_drawing.pdf
│   ├── fabrication_drawing.pdf
│   ├── schematic.pdf
│   └── 3d_render.png
└── deliverables/<release>/           final fab pack
    ├── (everything from outputs/<release>/)
    └── release_notes.md              with residual risks and compliance statement
```

If any item on this list is missing, the QA holder closes the PR. The release does not proceed until the gap is filled or the founder approves a waiver.

---

## 13. What this mini SOP does NOT cover

The mini SOP is intentionally narrow. The following topics live in the bigger reference SOP (`Fastbit_PCB_Design_SOP_v1.0.md`) and should be consulted there when needed:

- Service tier classification (Professional / Validated / Assured) for commercial offerings
- Internal complexity classes (A / B / C) and the escalation matrix
- Full EMI / EMC policy including the prohibited language list and the future capability path
- The seven-category revision philosophy
- Add-on specialist services (SI / PI simulation, FMEA, compliance matrix, pre-compliance EMC)
- Altium-specific manual workflow
- KPIs and benchmarking
- Standard stackup library
- Glossary

When the mini SOP and the bigger SOP appear to disagree on a process detail, the bigger SOP wins. The mini SOP exists to make the everyday work fast and clear. The bigger SOP exists to handle the edges.

---

## Document history

| Version | Date | Author | Notes |
|---|---|---|---|
| 1.0 | 2026-04-12 | Fastbit Embedded Technologies | Initial mini SOP. Distilled from `Fastbit_PCB_Design_SOP_v1.0.md` v1.0 with the goal of making one process every PCB designer can follow on every project, with founder-approved waivers for any gap. |
