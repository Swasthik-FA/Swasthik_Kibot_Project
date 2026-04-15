# design/pcb/reviews/

Completed quality gate checklists for this project, organized by gate. **Every PCB project runs all 5 gates regardless of service tier.** See SOP §6 for the full gate definitions.

Gate subfolders are **created on demand** — when you pass a gate, create the subfolder and move the completed checklist into it. The template does not pre-create the five empty gate subfolders; they would just be empty rooms until the project actually reaches each gate.

Suggested subfolder names (use these to stay consistent across projects):

- `g1_specification_lock/`
- `g2_schematic_review/`
- `g3_layout_review/`
- `g4_pre_fab_review/`
- `g5_fab_release/`

The checklist templates themselves live in the SOP at `D:/Fastbit-embedded-pvt-ltd/ops/Projects/fastbit-docs/SOP/checklists/`. Copy them into your project's `checklists/` folder at kickoff (see `../../../checklists/README.md`), fill them in as you reach each gate, and move the completed versions into the appropriate gate subfolder here.

## The 5 gates

### `g1_specification_lock/`

**Gate 1 — Specification Lock.** At the end of factory Phase 3 (Architect), before Phase 4 (Build) begins. Confirms the design requirements, interfaces, power budget, mechanical envelope, and compliance targets are stable before schematic work starts.

- Checklist: `pcb_design_input_checklist.md`
- Signoff: Tech Lead (all tiers); formal document for Assured tier
- Exit criteria: SOP §6.2
- Blocks progress to: G2 Schematic Review

### `g2_schematic_review/`

**Gate 2 — Schematic Review.** After schematic capture is complete, before layout starts. Verifies electrical correctness, completeness, and robustness.

- Checklist: `pcb_schematic_review_checklist.md`
- AI review notes (if used): `ai_review_notes_g2.md` (per SOP §5.7.8)
- Signoff: Peer reviewer (Professional), independent peer (Validated), two reviewers (Assured)
- Exit criteria: SOP §6.3
- Blocks progress to: G3 Layout Review

### `g3_layout_review/`

**Gate 3 — Layout Review.** After routing is >90% complete, before final DRC cleanup. Two-pass review (placement, then routing) for Validated and Assured; single-pass for Professional.

- Checklist: `pcb_layout_review_checklist.md`
- AI review notes (if used): `ai_review_notes_g3.md`
- Signoff: Tech Lead (all tiers); two reviewers + Tech Lead for Assured
- Exit criteria: SOP §6.4
- Blocks progress to: G4 Pre-Fabrication Review

### `g4_pre_fab_review/`

**Gate 4 — Pre-Fabrication Review.** After layout is finalized and DRC is clean. Multiple sub-reviews converge here.

Mandatory sub-checklists for all tiers:
- `pcb_dfm_review_checklist.md` — Design for Manufacturability
- `pcb_bom_validation_checklist.md` — BOM completeness, alternates, lifecycle

Tier-gated sub-checklists:
- `pcb_emi_emc_design_checklist.md` — preventive EMC design review (Validated, Assured)
- `pcb_dfa_review_checklist.md` — full Design for Assembly (Validated, Assured)
- `pcb_dft_review_checklist.md` — Design for Test (Assured only)

- Signoff: Tech Lead (all tiers)
- Exit criteria: SOP §6.5
- Blocks progress to: G5 Fabrication Release

### `g5_fab_release/`

**Gate 5 — Fabrication Release.** Governance review of the complete release pack. Authorizes sending files to the fab house.

- Checklist: `pcb_fabrication_release_checklist.md`
- Signoff: Tech Lead (all tiers); additional production readiness signoff for Assured
- Exit criteria: SOP §6.6
- Blocks progress to: fabrication and prototype bring-up

## Post-fabrication review (not a gate)

After prototype boards arrive from the fab/assembly house, run `pcb_post_fabrication_review_checklist.md` to document the bring-up and feed findings back into the learning loop. This checklist is typically filed at the top level of `design/pcb/reviews/` or under a dedicated `post_fab/` subfolder; it does not belong to any single gate.

## How to file a completed checklist

1. At project kickoff, copy the checklist templates from the SOP into this project's `checklists/` folder (see `../../../checklists/README.md`).
2. As you approach each gate, fill in the checklist in `checklists/` (your working copy).
3. When the gate is passed, **copy or move the completed checklist into the appropriate `g<N>_<gate>/` folder here**, with the reviewer's name and signoff date filled in.
4. Commit the completed checklist. It becomes the evidence for that gate.
5. If AI was used to produce a review summary, file it as `ai_review_notes_g<N>.md` in the same folder with the header required by SOP §5.7.8.

## Related files

- `../../../FAQ.md` Section 6 — gate and review Q&A
- `../../../checklists/README.md` — how to copy checklists from the SOP
- `../../../CLAUDE.md` — AI review rules (§5.7.8 in the SOP)
- SOP §6 — full gate definitions, entry/exit criteria, signoff authority
