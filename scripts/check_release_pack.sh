#!/usr/bin/env bash
# Fastbit PCB — Check release pack completeness
#
# Validates that a release pack directory contains all mandatory artifacts
# required by SOP-HW-001 §11.8 (Fabrication release package).
#
# Usage:
#   ./scripts/check_release_pack.sh release/rev_a1
#
# Exit codes:
#   0  Release pack complete and valid
#   1  Release pack missing required artifacts or validation failed
#   2  Usage error
#
# This script is called by GitHub Actions for stage: release PRs and
# should also be run locally before raising a release PR.
#
# Note on tiered requirements:
#   SHA256 checksums and release manifest JSON are required for Assured tier
#   only. Professional and Validated tiers can skip those checks. The script
#   warns but does not fail on missing Assured-only artifacts; the Tech Lead
#   is responsible for knowing the tier and verifying the right set.

set -euo pipefail

RELEASE_DIR="${1:-}"
if [ -z "$RELEASE_DIR" ]; then
  echo "ERROR: Release directory required." >&2
  echo "Usage: $0 <release/rev_xx>" >&2
  exit 2
fi

if [ ! -d "$RELEASE_DIR" ]; then
  echo "ERROR: Release directory not found: $RELEASE_DIR" >&2
  exit 2
fi

echo "=============================="
echo "Fastbit PCB — Release pack check"
echo "=============================="
echo "Checking: $RELEASE_DIR"
echo ""

ERRORS=0
WARNINGS=0

check_file() {
  local path="$1"
  local description="$2"
  local severity="$3"  # error | warning

  if [ -f "$path" ]; then
    echo "  OK    $description"
    return 0
  else
    if [ "$severity" = "error" ]; then
      echo "  MISS  $description   ($path)"
      ERRORS=$((ERRORS + 1))
    else
      echo "  WARN  $description   ($path)"
      WARNINGS=$((WARNINGS + 1))
    fi
    return 1
  fi
}

check_dir_nonempty() {
  local path="$1"
  local description="$2"

  if [ -d "$path" ] && [ -n "$(ls -A "$path" 2>/dev/null)" ]; then
    local count
    count=$(find "$path" -type f | wc -l)
    echo "  OK    $description ($count files)"
    return 0
  else
    echo "  MISS  $description   ($path empty or missing)"
    ERRORS=$((ERRORS + 1))
    return 1
  fi
}

# -----------------------------------------------------------------------------
# Production files (mandatory for all tiers)
# -----------------------------------------------------------------------------
echo "Production files:"
check_dir_nonempty "$RELEASE_DIR/gerbers" "Gerber files"
check_dir_nonempty "$RELEASE_DIR/drill" "Drill files"
check_file "$RELEASE_DIR/bom.csv" "BOM (CSV)" error
check_file "$RELEASE_DIR/schematic.pdf" "Schematic PDF" error
check_file "$RELEASE_DIR/centroid.csv" "Pick-and-place centroid file" error
echo ""

# -----------------------------------------------------------------------------
# Drawings (mandatory for all tiers)
# -----------------------------------------------------------------------------
echo "Drawings:"
check_file "$RELEASE_DIR/fab_drawing.pdf" "Fabrication drawing" error
check_file "$RELEASE_DIR/assembly_drawing.pdf" "Assembly drawing" error
echo ""

# -----------------------------------------------------------------------------
# Release documentation (mandatory for all tiers)
# -----------------------------------------------------------------------------
echo "Release documentation:"
check_file "$RELEASE_DIR/release_notes.md" "Release notes" error
check_file "$RELEASE_DIR/residual_risks.md" "Residual risks" error
echo ""

# -----------------------------------------------------------------------------
# Tier-dependent artifacts (warnings only — tier is in project_config.md)
# -----------------------------------------------------------------------------
echo "Tier-dependent artifacts (Validated and Assured):"
if [ -f "$RELEASE_DIR/emc_disclosure.md" ]; then
  echo "  OK    EMC disclosure (Validated/Assured)"
else
  echo "  WARN  EMC disclosure (required for Validated and Assured tiers — see SOP §9.5)"
  WARNINGS=$((WARNINGS + 1))
fi
echo ""

echo "Assured-tier artifacts:"
if [ -f "$RELEASE_DIR/release_manifest.json" ]; then
  echo "  OK    Release manifest JSON"
else
  echo "  WARN  Release manifest JSON (required for Assured tier only — see SOP §7.6)"
  WARNINGS=$((WARNINGS + 1))
fi

if [ -f "$RELEASE_DIR/SHA256SUMS.txt" ]; then
  echo "  OK    SHA256SUMS.txt"
else
  echo "  WARN  SHA256SUMS.txt (required for Assured tier only)"
  WARNINGS=$((WARNINGS + 1))
fi

if [ -f "$RELEASE_DIR/production_readiness_signoff.md" ]; then
  echo "  OK    Production readiness signoff"
else
  echo "  WARN  Production readiness signoff (required for Assured tier only — see SOP §6.6)"
  WARNINGS=$((WARNINGS + 1))
fi
echo ""

# -----------------------------------------------------------------------------
# Basic sanity checks on BOM
# -----------------------------------------------------------------------------
if [ -f "$RELEASE_DIR/bom.csv" ]; then
  echo "BOM sanity:"
  BOM_LINES=$(wc -l < "$RELEASE_DIR/bom.csv")
  if [ "$BOM_LINES" -lt 5 ]; then
    echo "  WARN  BOM has only $BOM_LINES line(s) — unusually sparse, verify content"
    WARNINGS=$((WARNINGS + 1))
  else
    echo "  OK    BOM has $BOM_LINES line(s)"
  fi
fi
echo ""

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo "=============================="
echo "Check complete."
echo "  Errors:   $ERRORS"
echo "  Warnings: $WARNINGS"
echo "=============================="

if [ "$ERRORS" -gt 0 ]; then
  echo ""
  echo "FAIL: Release pack is incomplete. Resolve the errors above before release."
  exit 1
fi

if [ "$WARNINGS" -gt 0 ]; then
  echo ""
  echo "PASS with warnings. Review the warnings above."
  echo "If this project is Professional tier, the warnings about Assured-only artifacts can be ignored."
  echo "If this project is Validated or Assured tier, the warnings must be addressed per SOP."
fi

exit 0
