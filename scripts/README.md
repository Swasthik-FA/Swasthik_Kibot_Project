# scripts/

Shell scripts wrapping `kicad-cli` for the local workflow and the CI pipeline. Every script is POSIX bash, self-contained, and safe to run from the repository root.

These scripts complement the KiBot automation in `kibot_yaml/` and `kibot_launch.sh`. Use these for quick local checks (ERC/DRC) and release pack management. Use KiBot (`./kibot_launch.sh`) for full output generation (Gerbers, PDFs, 3D renders, etc.).

See `../FAQ.md` section 3 for usage in common situations.

## Reference

| Script | What it does | When to run | Produces | Exit codes |
|---|---|---|---|---|
| `run_erc.sh` | Runs KiCad ERC on the schematic | Before committing any schematic change (pre-commit hook catches this automatically) | `design/pcb/outputs/erc_report.txt` | 0 = clean, 1 = issues, 2 = usage error |
| `run_drc.sh` | Runs KiCad DRC on the layout | Before committing layout changes; manually when debugging routing | `design/pcb/outputs/drc_report.txt` | 0 = clean, 1 = issues, 2 = usage error |
| `export_review_pack.sh` | Generates schematic PDF, BOM, ERC, and DRC reports for a PR | Before opening a PR; CI reproduces this in the cloud | `design/pcb/outputs/review_pack/` | 0 = success |
| `export_release_pack.sh` | Generates the full fabrication release pack (Gerbers, drill, BOM, centroid, schematic PDF) for a revision | When preparing a Gate 5 Fabrication Release | `release/rev_<letter>/` | 0 = success |
| `check_release_pack.sh` | Validates that a release pack contains all mandatory files | Before tagging a release; CI runs this for `stage: release` PRs | Prints pass/fail summary | 0 = complete, 1 = missing artifacts |

## Usage details

### `run_erc.sh`

```bash
./scripts/run_erc.sh                                                              # default: Swasthik_KiBot_Project.kicad_sch
./scripts/run_erc.sh design/pcb/kicad/Swasthik_KiBot_Project.kicad_sch           # explicit path
```

Zero errors and zero warnings -> exit 0. Any issue -> exit non-zero and the report is printed to stderr (first 50 lines).

Also runs automatically as a pre-commit hook on any `.kicad_sch` or `.kicad_pro` change.

### `run_drc.sh`

```bash
./scripts/run_drc.sh                                                                              # default, strict
./scripts/run_drc.sh design/pcb/kicad/Swasthik_KiBot_Project.kicad_pcb                           # explicit path
./scripts/run_drc.sh design/pcb/kicad/Swasthik_KiBot_Project.kicad_pcb --allow-warnings          # placement stage
```

**`--allow-warnings` is only for placement-stage work.** At routing, pre-fab, and release stages, DRC must be fully clean (zero warnings). Pre-commit uses `--allow-warnings` by default so work-in-progress commits are not blocked; CI enforces the strict mode at the appropriate stage.

### `export_review_pack.sh`

```bash
./scripts/export_review_pack.sh
```

No arguments. Uses the default KiCad project paths. Generates the automatically-producible artifacts only. **Layout screenshots must still be manually generated** from pcbnew's screenshot feature and saved into `design/pcb/outputs/review_pack/` with descriptive names (e.g., `placement_power.png`, `routing_usb.png`, `plane_L2.png`).

Run this before opening a PR so the reviewer has everything they need in one folder.

### `export_release_pack.sh`

```bash
./scripts/export_release_pack.sh rev_a1     # first prototype of Rev A
./scripts/export_release_pack.sh rev_b      # first fab of Rev B
./scripts/export_release_pack.sh rev_a2     # second prototype spin of Rev A (ECO)
```

The revision argument is mandatory. Creates `release/<revision>/` and populates it with scripted artifacts. **Manual artifacts must still be added:**

- `fab_drawing.pdf` — stackup, material, tolerances, impedance targets
- `assembly_drawing.pdf` — pin 1 markers, DNP, orientation notes
- `release_notes.md` — revision summary, known issues, residual risks
- `residual_risks.md` — explicit risk disclosure
- `emc_disclosure.md` — required for Validated and Assured tiers (see SOP §9.5)

After adding the manual artifacts, run `check_release_pack.sh` to verify completeness.

### `check_release_pack.sh`

```bash
./scripts/check_release_pack.sh release/rev_a1
```

Checks that the release pack directory has all mandatory files. Tier-aware for optional artifacts (release manifest, SHA256SUMS.txt, production readiness signoff — Assured only). Prints `WARN` for missing Assured-tier artifacts that are fine to skip at Professional/Validated tier; prints `ERROR` for any missing mandatory artifact.

Exit 0 -> complete (warnings may still be present, review them). Exit 1 -> mandatory artifact missing, fix before release.

## Environment and dependencies

All scripts require `kicad-cli` in the PATH. The CI workflows use the `ghcr.io/inti-cmnb/kicad_auto:ki9` Docker image which provides this automatically.

**Local development:**
- Install KiCad 9.x — get it from https://www.kicad.org/download/
- Verify `kicad-cli --version` returns 9.0 or later
- Pre-commit hooks: `pip install pre-commit && pre-commit install`

**Windows users:** scripts run under Git Bash, WSL, or MSYS2. Native PowerShell is not supported; use Git Bash which ships with Git for Windows.

## Relationship to KiBot

This project also uses **KiBot** for comprehensive output generation (Gerbers, assembly PDFs, 3D renders, interactive BOM, etc.). KiBot is configured via `kibot_yaml/` and run with `./kibot_launch.sh`. The scripts in this folder are lighter-weight kicad-cli wrappers for quick local checks and the release pack workflow. Both systems coexist:

- **Quick local check** (ERC/DRC): use `scripts/run_erc.sh` / `scripts/run_drc.sh`
- **Full output generation**: use `./kibot_launch.sh` (or let CI do it on push to `dev`)
- **Release pack**: use `scripts/export_release_pack.sh` + `scripts/check_release_pack.sh`
