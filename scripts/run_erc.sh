#!/usr/bin/env bash
# Fastbit PCB — Run ERC via kicad-cli
#
# Usage:
#   ./scripts/run_erc.sh                          # Uses default schematic
#   ./scripts/run_erc.sh path/to/schematic.kicad_sch
#
# Exit codes:
#   0  ERC passed (zero errors)
#   1  ERC found errors OR kicad-cli failed
#   2  Input file not found or not a .kicad_sch
#
# Produces:
#   design/pcb/outputs/erc_report.txt
#
# Per SOP-HW-001 §7.7 (PCB CI gate).

set -euo pipefail

SCHEMATIC="${1:-design/pcb/kicad/Swasthik_KiBot_Project.kicad_sch}"
OUTPUTS_DIR="design/pcb/outputs"
REPORT="$OUTPUTS_DIR/erc_report.txt"

if [ ! -f "$SCHEMATIC" ]; then
  echo "ERROR: Schematic file not found: $SCHEMATIC" >&2
  echo "       Usage: $0 [path/to/schematic.kicad_sch]" >&2
  exit 2
fi

if [[ "$SCHEMATIC" != *.kicad_sch ]]; then
  echo "ERROR: Expected a .kicad_sch file, got: $SCHEMATIC" >&2
  exit 2
fi

mkdir -p "$OUTPUTS_DIR"

echo "Running ERC on: $SCHEMATIC"
echo "Report will be written to: $REPORT"
echo ""

# --exit-code-violations makes kicad-cli return non-zero if there are errors
if kicad-cli sch erc \
    --output "$REPORT" \
    --severity-error \
    --severity-warning \
    --exit-code-violations \
    "$SCHEMATIC"; then
  echo ""
  echo "PASS: ERC clean (zero errors, zero warnings)"
  exit 0
else
  RC=$?
  echo ""
  echo "FAIL: ERC found issues. See $REPORT"
  echo ""
  echo "--- Report summary ---"
  head -n 50 "$REPORT" 2>/dev/null || echo "(report file empty or unreadable)"
  exit $RC
fi
