#!/usr/bin/env bash
# Fastbit PCB — Run DRC via kicad-cli
#
# Usage:
#   ./scripts/run_drc.sh                          # Uses default PCB
#   ./scripts/run_drc.sh path/to/board.kicad_pcb
#   ./scripts/run_drc.sh path/to/board.kicad_pcb --allow-warnings
#
# Exit codes:
#   0  DRC passed (zero errors; warnings allowed only with --allow-warnings)
#   1  DRC found errors OR kicad-cli failed
#   2  Input file not found or not a .kicad_pcb
#
# Produces:
#   design/pcb/outputs/drc_report.txt
#
# Per SOP-HW-001 §7.7 (PCB CI gate).
#
# Note on --allow-warnings:
#   At placement stage, routing is not yet complete so some DRC warnings
#   (unrouted nets, unfilled zones) are expected. Use --allow-warnings for
#   stage: placement PRs. At routing, pre-fab, and release stages, warnings
#   must be cleaned up or explicitly dispositioned.

set -euo pipefail

PCB="${1:-design/pcb/kicad/Swasthik_KiBot_Project.kicad_pcb}"
ALLOW_WARNINGS=false
if [ "${2:-}" = "--allow-warnings" ]; then
  ALLOW_WARNINGS=true
fi

OUTPUTS_DIR="design/pcb/outputs"
REPORT="$OUTPUTS_DIR/drc_report.txt"

if [ ! -f "$PCB" ]; then
  echo "ERROR: PCB file not found: $PCB" >&2
  echo "       Usage: $0 [path/to/board.kicad_pcb] [--allow-warnings]" >&2
  exit 2
fi

if [[ "$PCB" != *.kicad_pcb ]]; then
  echo "ERROR: Expected a .kicad_pcb file, got: $PCB" >&2
  exit 2
fi

mkdir -p "$OUTPUTS_DIR"

echo "Running DRC on: $PCB"
echo "Allow warnings: $ALLOW_WARNINGS"
echo "Report will be written to: $REPORT"
echo ""

if [ "$ALLOW_WARNINGS" = "true" ]; then
  # Errors fail the script; warnings are reported but not fatal.
  if kicad-cli pcb drc \
      --output "$REPORT" \
      --severity-error \
      --exit-code-violations \
      "$PCB"; then
    echo ""
    echo "PASS: DRC has no errors (warnings may still be present — review the report)."
    exit 0
  else
    RC=$?
    echo ""
    echo "FAIL: DRC found errors. See $REPORT"
    head -n 50 "$REPORT" 2>/dev/null || echo "(report file empty or unreadable)"
    exit $RC
  fi
else
  # Both errors and warnings fail the script.
  if kicad-cli pcb drc \
      --output "$REPORT" \
      --severity-error \
      --severity-warning \
      --exit-code-violations \
      "$PCB"; then
    echo ""
    echo "PASS: DRC clean (zero errors, zero warnings)"
    exit 0
  else
    RC=$?
    echo ""
    echo "FAIL: DRC found issues. See $REPORT"
    echo ""
    echo "--- Report summary ---"
    head -n 50 "$REPORT" 2>/dev/null || echo "(report file empty or unreadable)"
    echo ""
    echo "If this is a placement-stage PR, re-run with: $0 $PCB --allow-warnings"
    exit $RC
  fi
fi
