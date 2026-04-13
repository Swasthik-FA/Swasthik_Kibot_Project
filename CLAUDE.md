# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

This is a KiCad 8/9 PCB project using [KiBot](https://github.com/INTI-CMNB/KiBot) for automated documentation generation via CI/CD. It is based on the [KDT_Hierarchical_KiBot](https://github.com/nguyen-v/KDT_Hierarchical_KiBot) template. The project follows a gate-review workflow for PCB design.

## Directory structure

```
design/
  pcb/
    kicad/                    KiCad source + KiBot config
      *.kicad_pro/sch/pcb     KiCad project files
      kibot_yaml/             KiBot YAML configs (entry: kibot_main.yaml)
      kibot_resources/        Fonts, colors, scripts, templates
      Templates/              KiCad worksheet templates
      Logos/                  Project logos
      CHANGELOG.md            Semantic versioning changelog
      kibot_launch.sh         Local KiBot launcher
    outputs/                  CI-generated outputs
      Manufacturing/          Gerbers, BOM, assembly docs
      Schematic/              Schematic PDFs
      3D/                     STEP files
      Images/                 3D render PNGs
      Testing/                Testpoint CSVs
      HTML/                   Results navigation webpage
      KiRI/                   PCB diff viewer
    reports/                  ERC, DRC, validation reports
    reviews/                  Gate review checklists
      g1_spec_lock/
      g2_schematic/
      g3_layout/
      g4_pre_fab/
      g5_fab_release/
    waivers/                  Approved waiver notes
    ecos/                     ECO documents
    bring_up/                 Post-fab evidence (scope shots, photos)
    gate_log.md               Gate execution log
    stackup.md                Stackup decision and fab confirmation
    bring_up_plan.md          Bring-up plan (drafted at G4)
    release_notes.md          Release notes (drafted at G5)
```

## Architecture

### KiBot configuration (modular YAML)

All KiBot config lives in `design/pcb/kicad/kibot_yaml/`. The entry point is `kibot_main.yaml`, which:
- Defines **variants** (DRAFT, PRELIMINARY, CHECKED, RELEASED) that control which outputs are generated
- Defines **output groups** (`all_group`, `all_group_k9`, `draft_group`, `fab`, `fab_k9`, etc.)
- Contains all **definitions** (metadata, paths, layer names) referenced by `@VARIABLE@` syntax
- Includes other YAML files via `import:` blocks, prefixed `kibot_filt_`, `kibot_pre_`, or `kibot_out_`

Output directories in `kibot_main.yaml` use `../outputs/` and `../reports/` relative paths (relative to `design/pcb/kicad/`).

### KiCad project files

All in `design/pcb/kicad/`:
- `Swasthik_KiBot_Project.kicad_sch` - Root schematic (hierarchical, includes sub-sheets)
- `Swasthik_KiBot_Project.kicad_pcb` - PCB layout
- `Swasthik_KiBot_Project.kicad_dru` - Design rules (PCBWay 6-layer, 2oz outer / 1oz inner)
- Sub-sheets: `Block Diagram.kicad_sch`, `Power - Sequencing.kicad_sch`, `Project Architecture.kicad_sch`, `Revision History.kicad_sch`, `Section A - Title A.kicad_sch`, `Section B - TItle B.kicad_sch`

### PCB layer naming convention

Custom user-layer names that KiBot depends on (must match `kibot_main.yaml` definitions):
- `TitlePage` - Assembly document first page (3D images)
- `F.DNP` / `B.DNP` - Do Not Populate crosses (keep empty)
- `DrillMap` - Drill map drawings and tables
- `F.TestPointList` / `B.TestPointList` - Test point tables
- `F.AssemblyText` / `B.AssemblyText` - Assembly info and component counts
- `F.Dimensions` - Stackup, impedance table, fabrication notes

### Netlist validation

`design/pcb/kicad/kibot_resources/scripts/validate_netlist.py` validates component connections against datasheet rules:
- Generic category rules auto-detect regulators, MCUs, ICs, crystals, connectors by KiCad library
- Part-specific rules for known components (NCP1117) add cap value and bridge checks
- Outputs `.txt` and `.html` reports to `design/pcb/reports/`
- Runs automatically in CI for PRELIMINARY/CHECKED/RELEASED variants

## Branching and workflow

- **`dev`** is the working branch. **`main`** is for releases only.
- CI triggers on push to `main` or `dev`, and on semantic version tags.
- CI runs KiBot from `design/pcb/kicad/` directory with `dir` parameter.
- After CI runs, pull before making further changes.
- To release: merge `dev` into `main`, then tag on `main`.

## CI/CD configuration

In `.github/workflows/ci.yaml`:
- `kicad_dir`: Points to `design/pcb/kicad`
- `kibot_config`: Points to `design/pcb/kicad/kibot_yaml/kibot_main.yaml`
- `kibot_variant`: Set to `DRAFT`, `PRELIMINARY`, `CHECKED`, or `RELEASED`
- `kicad_version`: Set to `8` or `9`

## Running KiBot locally

From inside a Docker container, run from `design/pcb/kicad/`:

```bash
cd design/pcb/kicad
./kibot_launch.sh                    # CHECKED variant, all outputs
./kibot_launch.sh -v DRAFT           # Schematic PDF, netlist, BoM only
./kibot_launch.sh --costs            # KiCost XLSX spreadsheet
./kibot_launch.sh --server           # HTTP server for output viewer
```

## Project customisation checklist

Edit in `design/pcb/kicad/`:
1. `kibot_yaml/kibot_main.yaml` definitions: PROJECT_NAME, BOARD_NAME, COMPANY, DESIGNER, LOGO, GIT_URL
2. `kibot_resources/templates/` - assembly/fabrication notes, impedance table, readme
3. `*.kicad_dru` - design rules for your manufacturer
4. BoM YAML files - component field names
5. `.github/workflows/ci.yaml` - variant and KiCad version
6. `CHANGELOG.md` - update with real entries

## Important notes for editing KiBot YAML

- Sub-YAML files use `@VARIABLE@` references resolved from `kibot_main.yaml` definitions.
- Output paths use `../outputs/` and `../reports/` relative to `design/pcb/kicad/`.
- Adding a new output requires adding it to the appropriate group(s) in `kibot_main.yaml`.
- KiCad 9 uses separate groups (`all_group_k9`, `fab_k9`) for version-specific outputs.
