#!/usr/bin/env bash
# Fastbit PCB — Export fabrication release pack
#
# Generates the complete release pack for a given revision, per SOP §11.8:
#   - Gerber files (all layers)
#   - Drill files
#   - BOM CSV
#   - Schematic PDF
#   - Pick-and-place / centroid file
#   - 3D render (if supported)
#
# Manual artifacts still required (engineer must add before release):
#   - Fabrication drawing (stackup, notes, tolerances, impedance targets)
#   - Assembly drawing (pin 1 markers, DNP, notes)
#   - Release notes
#   - Residual risks document
#   - EMC disclosure document (Validated and Assured tiers)
#
# Usage:
#   ./scripts/export_release_pack.sh <revision>
#   e.g.,
#   ./scripts/export_release_pack.sh rev_a1
#
# Per SOP-HW-001 §11.8 (Fabrication release package).

set -euo pipefail

REVISION="${1:-}"
if [ -z "$REVISION" ]; then
  echo "ERROR: Revision argument required." >&2
  echo "Usage: $0 <revision>    (e.g., rev_a1, rev_b, rev_c)" >&2
  exit 1
fi

# Sanitize revision: lowercase, alphanumeric + underscore only
if ! [[ "$REVISION" =~ ^rev_[a-z0-9_]+$ ]]; then
  echo "ERROR: Revision must match pattern 'rev_<letter>[<digit>]' (e.g., rev_a, rev_a1, rev_b)" >&2
  exit 1
fi

KICAD_PROJECT_DIR="design/pcb/kicad"
SCHEMATIC="$KICAD_PROJECT_DIR/Swasthik_KiBot_Project.kicad_sch"
PCB="$KICAD_PROJECT_DIR/Swasthik_KiBot_Project.kicad_pcb"
RELEASE_DIR="release/$REVISION"

mkdir -p "$RELEASE_DIR"

echo "=============================="
echo "Fastbit PCB — Release pack export"
echo "=============================="
echo "Revision: $REVISION"
echo "Output directory: $RELEASE_DIR"
echo ""

# -----------------------------------------------------------------------------
# Sanity checks
# -----------------------------------------------------------------------------
if [ ! -f "$SCHEMATIC" ]; then
  echo "ERROR: Schematic not found at $SCHEMATIC" >&2
  exit 1
fi
if [ ! -f "$PCB" ]; then
  echo "ERROR: PCB not found at $PCB" >&2
  exit 1
fi

# -----------------------------------------------------------------------------
# 1. Gerbers
# -----------------------------------------------------------------------------
echo "[1/6] Exporting Gerbers..."
GERBER_DIR="$RELEASE_DIR/gerbers"
mkdir -p "$GERBER_DIR"
kicad-cli pcb export gerbers \
  --output "$GERBER_DIR/" \
  "$PCB"
echo "      OK: $GERBER_DIR"

# -----------------------------------------------------------------------------
# 2. Drill files
# -----------------------------------------------------------------------------
echo "[2/6] Exporting drill files..."
DRILL_DIR="$RELEASE_DIR/drill"
mkdir -p "$DRILL_DIR"
kicad-cli pcb export drill \
  --output "$DRILL_DIR/" \
  --format excellon \
  --drill-origin absolute \
  --excellon-separate-th \
  "$PCB"
echo "      OK: $DRILL_DIR"

# -----------------------------------------------------------------------------
# 3. BOM
# -----------------------------------------------------------------------------
echo "[3/6] Exporting BOM..."
kicad-cli sch export bom \
  --output "$RELEASE_DIR/bom.csv" \
  "$SCHEMATIC"
echo "      OK: $RELEASE_DIR/bom.csv"

# -----------------------------------------------------------------------------
# 4. Schematic PDF
# -----------------------------------------------------------------------------
echo "[4/6] Exporting schematic PDF..."
kicad-cli sch export pdf \
  --output "$RELEASE_DIR/schematic.pdf" \
  "$SCHEMATIC"
echo "      OK: $RELEASE_DIR/schematic.pdf"

# -----------------------------------------------------------------------------
# 5. Pick-and-place (centroid)
# -----------------------------------------------------------------------------
echo "[5/6] Exporting pick-and-place file..."
kicad-cli pcb export pos \
  --output "$RELEASE_DIR/centroid.csv" \
  --format csv \
  --units mm \
  "$PCB"
echo "      OK: $RELEASE_DIR/centroid.csv"

# -----------------------------------------------------------------------------
# 6. Manual artifacts reminder
# -----------------------------------------------------------------------------
echo "[6/6] Manual artifacts still required:"
echo ""

MANUAL_ARTIFACTS=(
  "fab_drawing.pdf"
  "assembly_drawing.pdf"
  "release_notes.md"
  "residual_risks.md"
)

MISSING=0
for f in "${MANUAL_ARTIFACTS[@]}"; do
  if [ -f "$RELEASE_DIR/$f" ]; then
    echo "      OK   $f"
  else
    echo "      MISS $f"
    MISSING=$((MISSING + 1))
  fi
done

if [ -f "$RELEASE_DIR/emc_disclosure.md" ]; then
  echo "      OK   emc_disclosure.md (Validated/Assured)"
else
  echo "      NOTE emc_disclosure.md (required for Validated and Assured tiers — check SOP §9.5)"
fi

echo ""
echo "=============================="
if [ "$MISSING" -gt 0 ]; then
  echo "Release pack scripted artifacts exported. $MISSING manual artifact(s) still missing."
  echo "The release pack is NOT complete until all manual artifacts are added."
  echo "After adding them, run: ./scripts/check_release_pack.sh $RELEASE_DIR"
else
  echo "All automatic and manual artifacts present."
  echo "Run: ./scripts/check_release_pack.sh $RELEASE_DIR"
fi
echo "=============================="
