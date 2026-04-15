# Checklists folder

This folder holds the **project-specific copies** of the Fastbit PCB SOP checklists. The **source of truth** for the checklists themselves lives at:

```
D:/Fastbit-embedded-pvt-ltd/ops/Projects/fastbit-docs/SOP/checklists/
```

**Do not edit the source checklists.** They are maintained centrally and evolve as the learning loop finds gaps. When a new project starts, copy the relevant checklists into this folder and fill them in for this specific project.

## What to copy

### Mandatory for all tiers (quality floor — SOP §12.1)

Copy these seven at project start:

```bash
SOP_DIR="D:/Fastbit-embedded-pvt-ltd/ops/Projects/fastbit-docs/SOP/checklists"

cp "$SOP_DIR/pcb_design_input_checklist.md"          checklists/
cp "$SOP_DIR/pcb_schematic_review_checklist.md"      checklists/
cp "$SOP_DIR/pcb_layout_review_checklist.md"         checklists/
cp "$SOP_DIR/pcb_dfm_review_checklist.md"            checklists/
cp "$SOP_DIR/pcb_bom_validation_checklist.md"        checklists/
cp "$SOP_DIR/pcb_fabrication_release_checklist.md"   checklists/
cp "$SOP_DIR/pcb_post_fabrication_review_checklist.md" checklists/
```

### Tier-gated (SOP §12.2)

For **Validated and Assured** tiers, also copy:

```bash
cp "$SOP_DIR/pcb_emi_emc_design_checklist.md"  checklists/
cp "$SOP_DIR/pcb_dfa_review_checklist.md"      checklists/
```

For **Assured** tier only, also copy:

```bash
cp "$SOP_DIR/pcb_dft_review_checklist.md"      checklists/
```

### Process checklists (SOP §12.2.1)

Copy on demand when the event occurs:

```bash
cp "$SOP_DIR/pcb_eco_impact_checklist.md"      checklists/
```

## How to fill them in

1. **At project start (G1):** Copy and fill in `pcb_design_input_checklist.md`. This is the Specification Lock gate.
2. **After schematic capture (G2):** Fill in `pcb_schematic_review_checklist.md` and route it to the peer reviewer.
3. **After layout (G3):** Fill in `pcb_layout_review_checklist.md`.
4. **Before fabrication (G4):** Fill in `pcb_dfm_review_checklist.md`, `pcb_bom_validation_checklist.md`, and the tier-gated checklists if applicable.
5. **At release (G5):** Fill in `pcb_fabrication_release_checklist.md` as the final governance check.
6. **After prototype arrives:** Fill in `pcb_post_fabrication_review_checklist.md` to capture bring-up findings and feed the learning loop.
7. **On any ECO event:** Copy and fill in `pcb_eco_impact_checklist.md` before modifying any design files.

## Where to file them when complete

Completed checklists are moved or referenced from:

```
design/pcb/reviews/g1_specification_lock/pcb_design_input_checklist.md
design/pcb/reviews/g2_schematic_review/pcb_schematic_review_checklist.md
design/pcb/reviews/g3_layout_review/pcb_layout_review_checklist.md
design/pcb/reviews/g4_pre_fab_review/
  ├── pcb_dfm_review_checklist.md
  ├── pcb_bom_validation_checklist.md
  ├── pcb_emi_emc_design_checklist.md   (Validated/Assured)
  ├── pcb_dfa_review_checklist.md       (Validated/Assured)
  └── pcb_dft_review_checklist.md       (Assured)
design/pcb/reviews/g5_fab_release/pcb_fabrication_release_checklist.md
```

This folder (`checklists/`) holds the working copies during the design phase; the final signed-off versions are archived under `design/pcb/reviews/<gate>/` and committed with the release pack.

## Why not just symlink or submodule?

Two reasons:
1. **Client project repos are typically separate from the factory repo.** The SOP checklists live in the Fastbit internal docs repo; client project repos must be self-contained so the client can clone them and review them without access to internal Fastbit repos.
2. **Checklists are filled in per project.** They are working documents, not library files. Each project has its own completed checklist with reviewer names, dates, and findings. Symlinking would prevent per-project completion.

Copy, fill in, and commit. That's the model.
