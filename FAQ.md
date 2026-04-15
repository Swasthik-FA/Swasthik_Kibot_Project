# Fastbit PCB Project — FAQ

Practical answers for engineers working on this project. If you can't find your question here, check the main `README.md` or the authoritative SOP at `D:/Fastbit-embedded-pvt-ltd/ops/Projects/fastbit-docs/SOP/Fastbit_PCB_Design_SOP_v1.0.md`.

This FAQ is KiCad-oriented. For Altium projects, the **file locations are the same**, only the tool-specific commands differ. The quality floor (5 gates, 7 mandatory checklists) applies identically — see SOP §10.8.2 for the Altium manual path.

---

## Quick lookup — "where does X go"

Scan this table first. Most "where do I keep X" questions are answered here. Detailed Q&A follows below.

| What I have | Where it goes | Notes |
|---|---|---|
| KiCad project file | `design/pcb/kicad/Swasthik_KiBot_Project.kicad_pro` | One per project. |
| Schematic | `design/pcb/kicad/Swasthik_KiBot_Project.kicad_sch` | Same basename as the .kicad_pro file. |
| PCB layout | `design/pcb/kicad/Swasthik_KiBot_Project.kicad_pcb` | Same basename. KiCad enforces this. |
| Project-local schematic symbols | `design/pcb/kicad/libraries/symbols/` | Symbols you create for THIS project. Don't edit the global KiCad library. |
| Project-local footprints | `design/pcb/kicad/libraries/footprints.pretty/` | Must use the `.pretty` suffix on the directory. KiCad convention. |
| Project-local 3D models | `design/pcb/kicad/libraries/3d/` | STEP or WRL. Referenced from footprints. |
| Component datasheets | `design/pcb/datasheets/` | PDF files. Name them after the manufacturer part number, e.g., `STM32F407VGT6.pdf`. |
| Design notes, rationale, power tree calcs | `design/pcb/notes/` | Markdown, spreadsheets, or plain text. Your working thinking. |
| ERC / DRC reports (auto-generated) | `design/pcb/outputs/` | Created by `scripts/run_erc.sh` and `scripts/run_drc.sh`. |
| Review pack for a PR | `design/pcb/outputs/review_pack/` | Created by `scripts/export_review_pack.sh`. Screenshots go here too. |
| Completed checklists (filled-in for this project) | `design/pcb/reviews/g<N>_<gate>/` | One folder per gate, G1-G5. |
| ECO documents and impact checklists | `design/pcb/ecos/eco_<NNN>.md` | One file per ECO, numbered sequentially. |
| Fabrication release pack (per revision) | `release/rev_<letter>[<digit>]/` | e.g., `release/rev_a1/`, `release/rev_b/`. One folder per revision tag. |
| Project-level config (tier, complexity, team) | `project_config.md` | Root of the repo. Fill in at kickoff. |
| Mechanical / enclosure STEP files | `design/mechanical/` | Create this folder if the project has mechanical constraints. Not pre-created. |
| Simulation files (LTspice, ngspice) | `design/pcb/simulation/` | Create this folder if you run simulation. Not pre-created. |
| Reference material (app notes, example designs) | `design/pcb/references/` | Create this folder as needed. Not pre-created. |

---

## Section 1 — Getting started

### Q1.1: I just cloned this project. What do I do first?

1. Read `README.md` for the overview (5 minutes).
2. Open `project_config.md` and fill in the project identity: name, client, service tier (Professional / Validated / Assured per MSA Schedule A), internal complexity class (A / B / C per SOP §5.4), and the team section.
3. Copy the mandatory checklists from the SOP into `checklists/`. See `checklists/README.md` for the exact `cp` commands.
4. Install pre-commit hooks: `pip install pre-commit && pre-commit install`.
5. The KiCad project already exists in `design/pcb/kicad/Swasthik_KiBot_Project.kicad_pro`.
6. Commit the filled-in `project_config.md` and the copied checklists. This is your "project initialized" baseline.

### Q1.2: How do I know my service tier?

The tier is in the SOW signed with the client, referenced in `project_config.md`. If you don't know it, ask the Project Manager or Tech Lead. Do NOT guess — the tier determines which checklists, reviewers, and artifacts are mandatory.

- **Professional** — default tier, 4 hours bring-up support, single-pass layout review, no EMI/EMC specialist review
- **Validated** — adds EMI/EMC design review, independent peer review, full DFA, 8 hours bring-up support
- **Assured** — adds DFT, two reviewers at every gate, formal Spec Lock signoff, release manifest, 16 hours bring-up, dedicated engineer

See MSA Schedule A for the contractual definitions.

### Q1.3: How are the scripts and automation configured for this project?

This project has **two automation layers**:

1. **kicad-cli scripts** (`scripts/`): Quick local ERC/DRC checks and release pack management. These default to `design/pcb/kicad/Swasthik_KiBot_Project.kicad_sch` / `.kicad_pcb`.

2. **KiBot** (`kibot_yaml/` + `kibot_launch.sh`): Full output generation — Gerbers, assembly PDFs, 3D renders, interactive BOM, schematic PDFs, etc. Run with `./kibot_launch.sh` from the repo root.

CI workflows:
- `.github/workflows/pcb-checks.yaml` — PR gate (ERC, DRC, BOM, netlist validation)
- `.github/workflows/ci.yaml` — Output generation on push to `dev` and release on tag

---

## Section 2 — File locations

### Q2.1: Where is the KiCad project?

`design/pcb/kicad/Swasthik_KiBot_Project.kicad_pro`. The project, schematic (`.kicad_sch`), and PCB layout (`.kicad_pcb`) all share the same basename and live in this directory.

If your schematic has multiple sheets (hierarchical design), the sub-sheet files (`.kicad_sch` for each sheet) also live in `design/pcb/kicad/`. Don't move them.

### Q2.2: Where do I keep custom schematic symbols?

`design/pcb/kicad/libraries/symbols/`. Create one or more `.kicad_sym` library files here for symbols you draw for this project.

**Do NOT edit the global KiCad library.** Project-local symbols stay in the project repo so they travel with the design.

In KiCad: Preferences > Manage Symbol Libraries > Project Specific Libraries > Add, then point at your `.kicad_sym` file in `libraries/symbols/`.

### Q2.3: Where do I keep custom footprints?

`design/pcb/kicad/libraries/footprints.pretty/`. **The `.pretty` suffix on the directory is a KiCad convention — do not rename it.** Footprint files inside are `.kicad_mod`.

In KiCad: Preferences > Manage Footprint Libraries > Project Specific Libraries > Add, point at `libraries/footprints.pretty/`.

### Q2.4: Where do I keep 3D models for components?

`design/pcb/kicad/libraries/3d/`. STEP files (`.step` or `.stp`) and WRL files (`.wrl`) go here. Reference them from the footprint's 3D model field using `${KIPRJMOD}/libraries/3d/MyConnector.step`.

### Q2.5: Where do I keep component datasheets?

`design/pcb/datasheets/`. PDF files. Name them by manufacturer part number: `STM32F407VGT6.pdf`, `SN74LVC245A.pdf`, etc.

### Q2.6: Where do I keep mechanical / enclosure STEP files?

`design/mechanical/` — **this folder is not pre-created.** Create it if your project has mechanical constraints.

### Q2.7: Where do I keep simulation files (LTspice, ngspice)?

`design/pcb/simulation/` — **not pre-created.** Create the folder if you run simulation.

### Q2.8: Where do I keep reference material (app notes, example designs)?

`design/pcb/references/` — **not pre-created.** Create it if you have app notes or manufacturer reference designs.

### Q2.9: Where do I keep generated Gerbers?

**Two places depending on intent:**

- **Intermediate / working Gerbers** (for sanity-checking in a Gerber viewer during design) -> `design/pcb/outputs/`. These get regenerated by KiBot.
- **Release Gerbers** (the files you send to the fab house) -> `release/rev_<letter>/gerbers/`. Created by `scripts/export_release_pack.sh rev_<letter>`. These ARE committed — the release pack is the authoritative snapshot.

Never send fab the working copies from `design/pcb/outputs/`. Always run the release pack script and send from `release/rev_<letter>/`.

### Q2.10: Where do I keep design notes and rationale?

`design/pcb/notes/`. Markdown is recommended; spreadsheets for calculations are fine.

Suggested files:
- `design/pcb/notes/power_tree.md` — voltage rails, currents, sequencing, regulator choices
- `design/pcb/notes/placement_rationale.md` — why components are placed where
- `design/pcb/notes/stackup.md` — layer stackup decision with impedance targets
- `design/pcb/notes/decisions.md` — log of architectural decisions and their reasoning
- `design/pcb/notes/bringup_plan.md` — what to measure first when the prototype arrives

---

## Section 3 — Scripts and automation

### Q3.1: How do I run ERC locally?

```bash
./scripts/run_erc.sh
```

Defaults to `design/pcb/kicad/Swasthik_KiBot_Project.kicad_sch`. Writes `design/pcb/outputs/erc_report.txt`. Exit code 0 if clean, non-zero if errors.

Also runs automatically as a pre-commit hook on any `.kicad_sch` change.

### Q3.2: How do I run DRC locally?

```bash
./scripts/run_drc.sh
```

Defaults to `design/pcb/kicad/Swasthik_KiBot_Project.kicad_pcb`. Writes `design/pcb/outputs/drc_report.txt`.

For placement-stage work (routing not yet complete), use `--allow-warnings`:

```bash
./scripts/run_drc.sh design/pcb/kicad/Swasthik_KiBot_Project.kicad_pcb --allow-warnings
```

### Q3.3: How do I generate a review pack before opening a PR?

```bash
./scripts/export_review_pack.sh
```

Generates schematic PDF, BOM, ERC, and DRC reports into `design/pcb/outputs/review_pack/`.

**It does NOT generate screenshots.** You must manually open KiCad's pcbnew, take screenshots, and save them into `design/pcb/outputs/review_pack/` with descriptive names like `placement_power_section.png`, `routing_usb_differential.png`.

Screenshots are mandatory for any layout-change PR per SOP §7.7.1.

### Q3.4: How do I generate a release pack for fabrication?

```bash
./scripts/export_release_pack.sh rev_a1
```

Pass the revision as the first argument. Creates `release/rev_a1/` with Gerbers, drill files, BOM, schematic PDF, and centroid.

**You still need to manually add:** `fab_drawing.pdf`, `assembly_drawing.pdf`, `release_notes.md`, `residual_risks.md`, and `emc_disclosure.md` (Validated/Assured tiers).

### Q3.5: How do I check if my release pack is complete?

```bash
./scripts/check_release_pack.sh release/rev_a1
```

Verifies all mandatory files are present. Exits non-zero if anything is missing.

### Q3.6: How do I run KiBot for full output generation?

```bash
./kibot_launch.sh                    # CHECKED variant, all outputs
./kibot_launch.sh -v DRAFT           # Schematic PDF, netlist, BoM only
./kibot_launch.sh -v PRELIMINARY     # Full outputs, no ERC/DRC
./kibot_launch.sh --costs            # KiCost XLSX spreadsheet
./kibot_launch.sh --server           # HTTP server for output viewer
```

KiBot is configured via `kibot_yaml/kibot_main.yaml`. See `CLAUDE.md` for details.

---

## Section 4 — Git and branches

### Q4.1: What branch should I work on?

Per SOP §7 (branching model):

- `main` — released designs only. Protected. Direct pushes forbidden.
- `dev` — integration branch. Active design work merges here via PR.
- `qa` — pre-release validation branch. Triggers Gate 4 review.

Feature work happens on short-lived branches off `dev`:

```
feature/HW-123-power-section-schematic
feature/HW-124-layout-placement
bugfix/HW-456-fix-uart-pinout
hotfix/HW-789-eco-reverse-polarity-fix
```

### Q4.2: How should I name branches and commits?

**Branch naming:** `<type>/HW-<ticket>-<short-description>`. Use `feature/` for new work, `bugfix/` for fixes on `dev`, `hotfix/` for ECOs on `main`.

**Commit messages:**
- First line: `HW-NNN: <what changed>` (short, imperative mood)
- Blank line
- Body: explain WHY (not just what — the diff shows what)

### Q4.3: What should NOT be committed?

The `.pre-commit-config.yaml` blocks KiCad backup files (`.bak`, `.lck`, `-backups/`, `~` suffixed files). Also do not commit:
- `design/pcb/outputs/` working files (intermediate Gerbers) — only commit the release pack under `release/`
- Personal IDE settings
- Secrets of any kind

---

## Section 5 — Pull requests

### Q5.1: How do I open a PR?

1. Push your feature branch to origin
2. Open GitHub and create a PR against `dev` (or `qa` for release candidates, `main` for hotfixes)
3. GitHub auto-populates the PR body from `.github/PULL_REQUEST_TEMPLATE.md`
4. **Fill in every field.** Set the `Stage:` label.
5. Attach screenshots if this is a layout change
6. Wait for CI to pass and for the reviewer to approve

### Q5.2: What stage label should I use?

| Stage label | When to use |
|---|---|
| `specification` | Requirements and constraints work (Gate 1) |
| `schematic` | Schematic capture or schematic edits |
| `placement` | Component placement in PCB layout, routing not yet complete |
| `routing` | PCB routing — full or partial |
| `pre-fab` | Gate 4 reviews (DFM, EMI/EMC, DFA, DFT, BOM validation) |
| `release` | Generating and validating the fabrication release pack |
| `eco` | Engineering change order |
| `documentation` | Docs-only changes (no design file changes allowed) |

### Q5.3: What happens if CI fails?

Read the CI log. Common causes:

- **ERC errors** — run `./scripts/run_erc.sh` locally, fix, push
- **DRC errors** — run `./scripts/run_drc.sh` locally, fix, push
- **BOM export failed** — check schematic for missing fields
- **Netlist validation failed** — check `design/pcb/reports/validation_report.txt`

---

## Section 6 — Reviews and gates

### Q6.1: What are the 5 gates and which checklists run at each?

| Gate | Name | Checklists |
|---|---|---|
| **G1** | Specification Lock | `pcb_design_input_checklist.md` |
| **G2** | Schematic Review | `pcb_schematic_review_checklist.md` |
| **G3** | Layout Review | `pcb_layout_review_checklist.md` |
| **G4** | Pre-Fabrication Review | `pcb_dfm_review_checklist.md`, `pcb_bom_validation_checklist.md` (all tiers); + EMI/EMC + DFA (Validated/Assured); + DFT (Assured) |
| **G5** | Fabrication Release | `pcb_fabrication_release_checklist.md` |
| Post-fab | Bring-up and learning loop | `pcb_post_fabrication_review_checklist.md` |

### Q6.2: Which checklists apply to my tier?

See `checklists/README.md` for the exact `cp` commands per tier.

### Q6.3: What if I'm the only hardware engineer on the project?

Solo-engineer exception applies only at **Professional tier** (SOP §5.6). Self-review at G2 and G5 is permitted with explicit documentation.

---

## Section 7 — AI assistance

### Q7.1: Can I ask Claude to draw my schematic or route my layout?

**No.** AI tools cannot draw correct schematics, route PCBs, judge signal integrity, or verify physical fit.

What AI can do: suggest circuit patterns, review reports, analyze BOMs, draft documentation, cross-reference datasheets.

### Q7.2: Can Claude review my design?

Yes — Claude can produce a review summary at any gate. Per SOP §5.7.8, Claude's output goes into `design/pcb/reviews/g<N>_<gate>/ai_review_notes_g<N>.md`. The reviewer signs the checklist; Claude signs nothing.

---

## Section 8 — Troubleshooting

### Q8.1: My component isn't in the KiCad library. What do I do?

1. Check manufacturer-supplied KiCad libraries (TI, ADI, Microchip all ship them)
2. Check SnapEDA or Ultra Librarian
3. Draw the symbol/footprint yourself in `design/pcb/kicad/libraries/`
4. Add a 3D model to `design/pcb/kicad/libraries/3d/`
5. Peer-review the footprint before use

### Q8.2: DRC has warnings I can't resolve. What do I do?

**Path A — fix them.** Most DRC warnings are legitimate.

**Path B — waive them with documented rationale** in the PR description. The Tech Lead reviews waivers at Gate 4.

### Q8.3: I need to do an ECO after prototype fabrication. Where do I start?

1. Create a hotfix branch from `main`
2. Create the ECO document: `design/pcb/ecos/eco_<NNN>.md`
3. Copy and fill in the ECO impact checklist before touching design files
4. Get Tech Lead approval on the impact checklist
5. Make the change, open a PR with `Stage: eco`
6. Merge to `main`, tag, and cherry-pick to `dev`

Full details in SOP §7.5 and §11.11.

---

## Still can't find your answer?

1. Check the main `README.md` for the overall workflow
2. Check `CLAUDE.md` if you're working with an AI assistant
3. Check the authoritative SOP at `D:/Fastbit-embedded-pvt-ltd/ops/Projects/fastbit-docs/SOP/Fastbit_PCB_Design_SOP_v1.0.md`
4. Ask the Tech Lead
