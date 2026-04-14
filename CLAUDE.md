# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

KiCad 8/9 PCB project using [KiBot](https://github.com/INTI-CMNB/KiBot) for automated documentation generation via CI/CD. Based on the [KDT_Hierarchical_KiBot](https://github.com/nguyen-v/KDT_Hierarchical_KiBot) template. Follows a five-gate review workflow for PCB design (see `Fastbit_PCB_Design_Mini_SOP_v1.0.md`).

## Directory structure

```
(repo root)
├── kibot_yaml/                   KiBot YAML configs (entry: kibot_main.yaml)
├── kibot_resources/              Fonts, colors, scripts, templates
│   ├── scripts/                  validate_netlist.py, docker helpers, changelog parsers
│   └── templates/                Assembly/fabrication notes, impedance table, readme
├── kibot_launch.sh               Local KiBot launcher (run from repo root)
├── CHANGELOG.md                  Semantic versioning changelog
├── Fastbit_PCB_Design_Mini_SOP_v1.0.md  PCB design SOP (five-gate process)
│
├── design/pcb/
│   ├── kicad/                    KiCad source files
│   │   ├── *.kicad_pro/sch/pcb   Project, schematic, PCB layout
│   │   ├── *.kicad_dru           Design rules (PCBWay 6-layer, 2oz outer / 1oz inner)
│   │   ├── Templates/            KiCad worksheet templates
│   │   ├── Logos/                Project logos
│   │   └── Computations/         Misc calculations
│   ├── outputs/                  CI-generated outputs
│   │   ├── Manufacturing/        Gerbers, BOM, assembly docs
│   │   ├── Schematic/            Schematic PDFs
│   │   ├── 3D/                   STEP files
│   │   ├── Images/               3D render PNGs
│   │   ├── Testing/              Testpoint CSVs
│   │   ├── HTML/                 Results navigation webpage
│   │   └── KiRI/                 PCB diff viewer
│   ├── reports/                  ERC, DRC, validation reports
│   ├── reviews/                  Gate review checklists (g1–g5 subfolders)
│   ├── waivers/                  Approved waiver notes
│   ├── ecos/                     ECO documents
│   ├── bring_up/                 Post-fab evidence (scope shots, photos)
│   ├── gate_log.md               Gate execution log
│   ├── stackup.md                Stackup decision and fab confirmation
│   ├── bring_up_plan.md          Bring-up plan (drafted at G4)
│   └── release_notes.md          Release notes (drafted at G5)
│
└── .github/workflows/ci.yaml    CI pipeline
```

## Architecture

### KiBot configuration (modular YAML)

Entry point: `kibot_yaml/kibot_main.yaml` (at repo root). It:
- Defines **variants** (DRAFT, PRELIMINARY, CHECKED, RELEASED) that control which outputs are generated
- Defines **output groups** (`all_group`, `all_group_k9`, `draft_group`, `fab`, `fab_k9`, etc.)
- Contains all **definitions** (metadata, paths, layer names) referenced by `@VARIABLE@` syntax in sub-YAML files
- Includes other YAML files via `import:` blocks, prefixed `kibot_filt_`, `kibot_pre_`, or `kibot_out_`

Output paths in definitions use `design/pcb/outputs/` and `design/pcb/reports/` relative to the repo root.

### KiCad project files

All in `design/pcb/kicad/`:
- `Swasthik_KiBot_Project.kicad_sch` — Root schematic (hierarchical, includes sub-sheets)
- `Swasthik_KiBot_Project.kicad_pcb` — PCB layout
- `Swasthik_KiBot_Project.kicad_dru` — Design rules
- Sub-sheets: `Block Diagram`, `Power - Sequencing`, `Project Architecture`, `Revision History`, `LCD`, `stlinkv3`, `Section A - Title A`, `Section B - TItle B`, `untitled`

### PCB layer naming convention

Custom user-layer names that KiBot depends on (must match `kibot_main.yaml` definitions):
- `TitlePage` — Assembly document first page (3D images)
- `F.DNP` / `B.DNP` — Do Not Populate crosses (keep empty)
- `DrillMap` — Drill map drawings and tables
- `F.TestPointList` / `B.TestPointList` — Test point tables
- `F.AssemblyText` / `B.AssemblyText` — Assembly info and component counts
- `F.Dimensions` — Stackup, impedance table, fabrication notes

### Netlist validation

`kibot_resources/scripts/validate_netlist.py` validates component connections against datasheet rules:
- Generic category rules auto-detect regulators, MCUs, ICs, crystals, connectors by KiCad library
- Part-specific rules for known components (NCP1117) add cap value and bridge checks
- Outputs `.txt` and `.html` reports to `design/pcb/reports/`
- Runs automatically in CI for PRELIMINARY/CHECKED/RELEASED variants

Usage: `python validate_netlist.py -n <netlist_file> [-o <output_dir>]`

## Branching and workflow

Three protected branches:

| Branch | Purpose | Reaches via |
|--------|---------|-------------|
| `main` | Released, fab-ready designs only. Every commit tagged. | PR from `qa` only |
| `qa` | Pre-release validation. G4/G5 gates run here. | PR from `dev` only |
| `dev` | Active design work. | PR from feature branches |

- Feature/bugfix branches come from `dev`. Hotfixes come from `main`.
- Branch naming: `feature/HW-123-description`, `bugfix/HW-456-description`, `hotfix/HW-789-description`
- After merging a hotfix to `main`, cherry-pick it to `dev` immediately.
- CI triggers on push to `main`, `qa`, or `dev`, on PRs targeting these branches, and on tags matching `hw-v*`.
- After CI runs, pull before making further changes (CI commits output files).
- To release: merge `dev` → `qa` → `main`, then tag on `main`.

## Five-gate review process

Every PCB passes five gates in order. Gate checklists live in `Fastbit_PCB_Design_Mini_SOP_v1.0.md`. Evidence goes in `design/pcb/reviews/g<N>_*/`. Update `design/pcb/gate_log.md` after each gate.

```
Requirements → [G1 Spec Lock] → Schematic → [G2 Schematic Review] → 
Placement+Routing → [G3 Layout Review] → Pre-fab → [G4 Pre-Fab] → [G5 Fab Release] → Fab
```

- **G1 Spec Lock** — Lock requirements, block diagram, power budget before schematic work
- **G2 Schematic Review** — ERC clean, all components have MPN/footprint, power architecture verified
- **G3 Layout Review** — Routing >90%, stackup matches G1 assumptions, DRC addressed
- **G4 Pre-Fab Review** — Final DRC/DFM clean, fab pack complete, bring-up plan drafted
- **G5 Fab Release** — Merge to `main`, tag, release notes finalized

Severity: Critical = blocks gate. Major = fix or waive in writing. Minor = log and move on.

## CI/CD configuration

Two workflow files in `.github/workflows/`:

### `pcb-checks.yaml` — PR gate (SOP Section 10)

Runs on every PR targeting `dev`, `qa`, or `main` and on pushes to those branches. Uses `kicad-cli` in the `ghcr.io/inti-cmnb/kicad_auto:ki9` container. Three blocking checks:

1. **ERC** — Fails on errors. Warnings reported but don't block.
2. **DRC** — Fails on errors, unconnected pads, or footprint errors. Warnings don't block.
3. **BOM export** — Must produce a non-empty CSV.

This is the required status check for branch protection on all three branches.

### `ci.yaml` — Output generation and release (dev + tags only)

Triggers on push to `dev` and on tags matching `hw-v*`. Does NOT run on `qa` or `main` pushes, and does NOT run on PRs.

Job pipeline: `pcb-gate` → `generate_outputs` → `release`

1. **`pcb-gate`** — Same ERC/DRC/BOM checks as pcb-checks.yaml. Must pass before outputs are generated.
2. **`generate_outputs`** — KiBot output generation (Gerbers, BOM, PDFs, 3D renders). Auto-commits outputs back to `dev`.
3. **`release`** — Only on tag push. Updates CHANGELOG.md, creates GitHub release with fab artifacts.

Key env vars:
- `kibot_config`: `kibot_yaml/kibot_main.yaml`
- `kibot_schema`: `design/pcb/kicad/Swasthik_KiBot_Project.kicad_sch`
- `kibot_board`: `design/pcb/kicad/Swasthik_KiBot_Project.kicad_pcb`
- `kibot_variant`: `CHECKED` (default) or `RELEASED` (auto on tag)
- `kicad_version`: `9`

Tag format: `hw-vX.Y.Z-rev<L>` (e.g., `hw-v1.0.0-revA`). See SOP Section 5.

### CI flow summary

| Event | `pcb-checks.yaml` | `ci.yaml` |
|-------|-------------------|-----------|
| PR to `dev`/`qa`/`main` | Runs (blocking gate) | Does not run |
| Push to `dev` | Runs | `pcb-gate` → `generate_outputs` |
| Push to `qa`/`main` | Runs | Does not run |
| Tag push (`hw-v*`) | Runs | `pcb-gate` → `generate_outputs` → `release` |

### Branch protection rules (configure in GitHub UI)

| Branch | Require PR review | Required status check | Force push |
|--------|-------------------|----------------------|------------|
| `main` | Yes (1 reviewer)  | `pcb-checks`         | Blocked    |
| `qa`   | Yes (1 reviewer)  | `pcb-checks`         | Blocked    |
| `dev`  | Yes (1 reviewer)  | `pcb-checks`         | Blocked    |

## Running KiBot locally

Run from repo root inside a Docker container:

```bash
./kibot_launch.sh                    # CHECKED variant, all outputs
./kibot_launch.sh -v DRAFT           # Schematic PDF, netlist, BoM only
./kibot_launch.sh -v PRELIMINARY     # Full outputs, no ERC/DRC
./kibot_launch.sh --costs            # KiCost XLSX spreadsheet
./kibot_launch.sh --server           # HTTP server for output viewer
./kibot_launch.sh --stop-server      # Stop the HTTP server
```

The script auto-detects KiCad version (8 vs 9) and selects the appropriate output group. Version is read from `CHANGELOG.md` unless overridden with `--version`.

## Important notes for editing KiBot YAML

- Sub-YAML files use `@VARIABLE@` references resolved from `kibot_main.yaml` definitions section.
- Output paths in definitions use `design/pcb/outputs/` and `design/pcb/reports/` relative to repo root.
- Adding a new output requires: (1) create/import the output YAML, (2) add it to the appropriate group(s) in `kibot_main.yaml`.
- KiCad 9 uses separate groups (`all_group_k9`, `fab_k9`) because KiCad 9 supports ODB++ output.
- Layer name definitions in `kibot_main.yaml` must match the user-defined layer names in the `.kicad_pcb` file.

## Project customisation checklist

1. `kibot_yaml/kibot_main.yaml` definitions: PROJECT_NAME, BOARD_NAME, COMPANY, DESIGNER, LOGO, GIT_URL
2. `kibot_resources/templates/` — assembly/fabrication notes, impedance table, readme
3. `design/pcb/kicad/*.kicad_dru` — design rules for your manufacturer
4. BoM YAML files — component field names (MPN_FIELD, MAN_FIELD)
5. `.github/workflows/ci.yaml` — variant and KiCad version
6. `CHANGELOG.md` — update with real entries
