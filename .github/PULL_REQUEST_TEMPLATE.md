<!--
  Fastbit PCB Project Pull Request Template
  See SOP-HW-001 Section 7.7.1 for the full spec.
  Fill in EVERY field. CI will reject PRs missing required content.
-->

## Stage

<!--
  REQUIRED. Pick one. CI reads this line and runs stage-appropriate checks.
  Valid values: specification, schematic, placement, routing, pre-fab, release, eco, documentation
  See SOP §7.7.3 for what each stage requires.
-->

Stage: <!-- schematic | placement | routing | pre-fab | release | eco | documentation | specification -->

## Summary

<!--
  One or two paragraphs in plain English. What changed and why.
  No jargon-only descriptions. Imagine a reviewer reading this six months from now.
-->



## Jira key

<!-- e.g., HW-123. Leave blank only if there is no associated ticket. -->



## Board revision

<!-- e.g., Rev A first prototype, Rev B ECO-002 fix, Rev C production release -->



## ERC status

<!--
  Pass / Fail / Warnings only / Not applicable
  If Pass: reference the report file, e.g., design/pcb/outputs/erc_report.txt
  If Warnings: list what was reviewed and waived with rationale
-->



## DRC status

<!--
  Pass / Fail / Warnings only / Not applicable
  If Pass: reference the report file, e.g., design/pcb/outputs/drc_report.txt
  If Warnings: list what was reviewed and waived with rationale
-->



## Screenshots

<!--
  MANDATORY for any layout change. Text diffs of .kicad_pcb files are not human-readable.
  Attach screenshots of the affected area before and after.
  Minimum one screenshot per functional area that changed.
-->



## Schematic PDF

<!--
  MANDATORY for any schematic change. Attach or link the updated schematic PDF.
  File should be under design/pcb/outputs/<stage>/schematic.pdf
-->



## BOM impact

<!--
  If components were added, removed, or substituted, list the BOM delta.
  Include manufacturer part numbers for new parts and justification for substitutions.
  If no BOM impact, write "None".
-->



## Design risk note

<!--
  Short paragraph describing the risks this change introduces or mitigates.
  Examples: "Added common-mode choke on USB lines; reduces EMI risk at the cost of 0.6mm board area."
  This is not a replacement for the review — it is context for the reviewer.
-->



## Known issues

<!--
  Anything not yet resolved that the reviewer should know about.
  If none, write "None".
-->



## Reviewer focus areas

<!--
  Point the reviewer at the parts of this change that most need their attention.
  Examples: "Please verify the new protection network on U4; I'm not confident the TVS rating is correct."
-->



## Linked checklists

<!--
  Pointers to the in-progress checklists that this PR contributes evidence to.
  Use relative paths, e.g., checklists/pcb_schematic_review_checklist.md
  Not every PR advances a checklist, but most do.
-->



## Pre-MR checklist (engineer self-verification)

<!-- Tick every box before opening this PR. See SOP §7.7.2 -->

- [ ] Branch is synced with the latest base branch
- [ ] ERC has been run for the current state (if applicable to the stage)
- [ ] DRC has been run for the current state (if applicable to the stage)
- [ ] BOM export succeeds and matches the schematic (if applicable)
- [ ] Native source files are committed (.kicad_sch / .kicad_pcb / .kicad_pro)
- [ ] Screenshots are attached for any layout change
- [ ] Schematic PDF is updated for any schematic change
- [ ] Stage-specific checklist in `checklists/` is up to date
- [ ] Revision letter on silkscreen is updated if a revision bump is involved
- [ ] Jira context and issue links are present above
- [ ] Commit messages follow the convention (HW-NNN: descriptive subject)

---

*This PR template is enforced by CI. A PR that does not follow this template may be closed without review per SOP §7.7.1.*
