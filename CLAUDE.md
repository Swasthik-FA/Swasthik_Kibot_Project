# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

This is a KiCad 8/9 PCB project using [KiBot](https://github.com/INTI-CMNB/KiBot) for automated documentation generation via CI/CD. It is based on the [KDT_Hierarchical_KiBot](https://github.com/nguyen-v/KDT_Hierarchical_KiBot) template. The project produces fabrication documents, assembly documents, BoMs, gerbers, 3D renders, and a results webpage automatically from KiCad source files.

## Architecture

### KiBot configuration (modular YAML)

All KiBot config lives in `kibot_yaml/`. The entry point is `kibot_main.yaml`, which:
- Defines **variants** (DRAFT, PRELIMINARY, CHECKED, RELEASED) that control which outputs are generated
- Defines **output groups** (`all_group`, `all_group_k9`, `draft_group`, `fab`, `fab_k9`, etc.) that bundle outputs
- Contains all **definitions** (metadata, paths, layer names, filter names, output names) referenced by `@VARIABLE@` syntax throughout other YAML files
- Includes other YAML files via `import:` blocks, each prefixed `kibot_filt_`, `kibot_pre_`, or `kibot_out_` for filters, preflights, and outputs respectively

The `@VARIABLE@` references in sub-YAML files are resolved from the `definitions:` block in `kibot_main.yaml`. When editing any YAML file, check `kibot_main.yaml` definitions for the variable values.

### KiCad project files

- `Swasthik_KiBot_Project.kicad_sch` - Root schematic (hierarchical, includes sub-sheets)
- `Swasthik_KiBot_Project.kicad_pcb` - PCB layout
- `Swasthik_KiBot_Project.kicad_dru` - Design rules (PCBWay 6-layer, 2oz outer / 1oz inner)
- Sub-sheets: `Block Diagram.kicad_sch`, `Power - Sequencing.kicad_sch`, `Project Architecture.kicad_sch`, `Revision History.kicad_sch`, `Section A - Title A.kicad_sch`, `Section B - TItle B.kicad_sch`

### PCB layer naming convention

The PCB uses custom user-layer names that KiBot depends on. These must match the values in `kibot_main.yaml` definitions:
- `TitlePage` - Assembly document first page (3D images)
- `F.DNP` / `B.DNP` - Do Not Populate crosses (keep empty)
- `DrillMap` - Drill map drawings and tables
- `F.TestPointList` / `B.TestPointList` - Test point tables
- `F.AssemblyText` / `B.AssemblyText` - Assembly info and component counts
- `F.Dimensions` - Stackup, impedance table, fabrication notes

### Text variables and automation

KiBot replaces text variables in schematics/PCB during runs:
- `${REVISION}`, `${COMPANY}`, `${VARIANT}`, `${RELEASE_DATE}` - set via preflight
- `${SHEET_NAME_X}` - auto table of contents (up to 40 pages)
- `${ASSEMBLY_NOTES}`, `${FABRICATION_NOTES}` - from templates in `kibot_resources/templates/`
- Named groups like `kibot_image_<output_name>` and `kibot_table_<output_name>` in PCB are replaced with generated images/tables

### Changelog-driven versioning

`CHANGELOG.md` follows [Keep a Changelog](https://keepachangelog.com/) format. The `[Unreleased]` section is synced to the schematic Revision History page via text variables defined in `kibot_yaml/kibot_pre_set_text_variables.yaml`. CI automatically renames `[Unreleased]` to the tag version on release.

## Branching and workflow

- **`dev`** is the working branch. **`main`** is for releases only.
- CI triggers on push to `main` or `dev`, and on semantic version tags.
- After CI runs, it commits generated outputs back to the branch. Pull after CI completes before making further changes.
- Avoid modifying `.kicad_pro` locally before pulling CI results (causes merge conflicts).
- To release: merge `dev` into `main`, then tag on `main` (`git tag x.x.x && git push origin x.x.x`).
- After release, rebase `dev` onto `main`.

## Running KiBot locally

Requires Docker Desktop running. From the project root inside a Docker container:

```bash
# Start Docker container (from host)
# Windows:
.\kibot_resources\scripts\docker_kibot_windows.bat      # KiCad 8
.\kibot_resources\scripts\docker_kibot_windows.bat -v 9  # KiCad 9
# Linux:
./kibot_resources/scripts/docker_kibot_linux.sh          # KiCad 8
./kibot_resources/scripts/docker_kibot_linux.sh -v 9     # KiCad 9

# Inside Docker container:
./kibot_launch.sh                        # Default: CHECKED variant, all outputs
./kibot_launch.sh -v DRAFT               # Schematic PDF, netlist, BoM only
./kibot_launch.sh -v PRELIMINARY         # All outputs, no ERC/DRC
./kibot_launch.sh -v CHECKED             # All outputs with ERC/DRC
./kibot_launch.sh --costs                # Generate KiCost XLSX spreadsheet
./kibot_launch.sh --server               # Start HTTP server on port 8000 for output viewer
./kibot_launch.sh --stop-server          # Stop the HTTP server
```

## CI/CD configuration

In `.github/workflows/ci.yaml`, the two key variables to update per project phase:
- `kibot_variant`: Set to `DRAFT`, `PRELIMINARY`, `CHECKED`, or `RELEASED`
- `kicad_version`: Set to `8` or `9`

## Project customisation checklist

When adapting this template for a new project, edit:
1. `kibot_yaml/kibot_main.yaml` definitions block (~line 556): PROJECT_NAME, BOARD_NAME, COMPANY, DESIGNER, LOGO, GIT_URL
2. `kibot_resources/templates/` - assembly_notes.txt, fabrication_notes.txt, impedance_table.txt, readme.txt
3. `*.kicad_dru` - design rules for your PCB manufacturer
4. BoM YAML files (`kibot_out_csv_bom.yaml`, `kibot_out_html_bom.yaml`, `kibot_out_xlsx_bom.yaml`) - component field names
5. `.github/workflows/ci.yaml` - variant and KiCad version
6. `CHANGELOG.md` - update with real entries

## KiCost (component pricing)

Create `kibot_yaml/kicost_config_local.yaml` from `kicost_config_local_template.yaml` with your distributor API keys. Never commit the local config (contains secrets). Run with `./kibot_launch.sh --costs`.

## Important notes for editing KiBot YAML

- Sub-YAML files use `@VARIABLE@` references resolved from `kibot_main.yaml` definitions. Do not hardcode values that should come from definitions.
- Output groups control what gets generated per variant. Adding a new output requires adding it to the appropriate group(s) in `kibot_main.yaml`.
- KiCad 9 uses separate groups (`all_group_k9`, `fab_k9`) because some outputs differ between versions (e.g., ODB++ instead of certain gerber formats).
