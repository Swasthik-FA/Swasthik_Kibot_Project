# design/pcb/

This is the main working area for the PCB. Everything related to the circuit board lives under this directory.

See `../../FAQ.md` for the file-location lookup table and detailed Q&A.

## What's pre-created

Only two subdirectories are created by the template:

| Folder | Why it's pre-created |
|---|---|
| `kicad/` | KiCad project files go here. The shell scripts default to `design/pcb/kicad/Swasthik_KiBot_Project.kicad_pro` and related paths. |
| `outputs/` | Scripts write generated reports (ERC, DRC, BOM, schematic PDF) here. CI reads from here. |
| `reviews/` | Completed gate checklists land here as the project progresses through the 5 quality gates. |

## What to create when you need it

Everything else is created on demand. The template deliberately does not pre-materialize empty folders, because most projects will not use all of them. Create these as the work reaches that stage:

| Folder | When to create |
|---|---|
| `kicad/libraries/symbols/` | When you draw your first project-local schematic symbol |
| `kicad/libraries/footprints.pretty/` | When you create your first project-local footprint (note: `.pretty` suffix is mandatory — KiCad convention) |
| `kicad/libraries/3d/` | When you add your first project-local 3D model (STEP, WRL) |
| `datasheets/` | When you add your first component datasheet |
| `notes/` | When you start writing design notes (power tree calc, placement rationale, etc.) |
| `ecos/` | When the first Engineering Change Order happens (after prototype fabrication) |
| `outputs/review_pack/` | When you run `../../scripts/export_review_pack.sh` for the first time |
| `reviews/g1_specification_lock/`, `g2_schematic_review/`, etc. | When each gate is passed and the completed checklist is archived |
| `../mechanical/` | If the project has mechanical constraints (enclosure STEP, DXF) |
| `simulation/` | If you run simulation (LTspice, ngspice) |
| `references/` | If you collect app notes, reference designs, or competitor teardowns |

## The rule

**If a file describes the PCB, it lives under `design/pcb/`.** Source files, libraries, datasheets, generated outputs, review evidence, change orders — all here. The only exceptions are: (1) per-revision release packs at `release/`, and (2) project-level config at the repo root (`project_config.md`, etc.).

## Related files

- `../../README.md` — overall template guide
- `../../FAQ.md` — file-location lookup and Q&A (creating folders on demand is covered in section 2)
- `../../CLAUDE.md` — AI context for this repo
