"""
main.py — Entry point for the furniture tool.

Recommended run method (FreeCAD macro):
    Macro menu → Execute → select this file

Also works from the command line:
    FreeCAD main.py
    python main.py   (exports only — skips FreeCAD GUI/3D build)

Pipeline:
    FurnitureSpec → solve() → cabinet.build() → export.(dxf/svg/bom)
"""

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# ---------------------------------------------------------------------------
# Ensure furniture_tool is importable when run from repo root
# ---------------------------------------------------------------------------

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from solver import (
    FurnitureSpec, ColumnSpec, DrawerSpec, DoorSpec, solve,
)
import export as E

OUTPUT_DIR = os.path.join(os.path.dirname(_HERE), "output")


# ---------------------------------------------------------------------------
# Furniture definition — edit here to change the model
# ---------------------------------------------------------------------------

SPEC = FurnitureSpec(
    label="Demo Cabinet",
    max_width=1200,
    max_height=800,
    max_depth=580,
    toe_kick_height=100,
    columns=[
        ColumnSpec(
            label="Left",
            has_door=True,
            door=DoorSpec(style="single", hinge_side="left"),
        ),
        ColumnSpec(
            label="Middle",
            drawers=[DrawerSpec("D1"), DrawerSpec("D2"), DrawerSpec("D3")],
        ),
        ColumnSpec(
            label="Right",
            shelf_count=3,
            has_door=True,
            door=DoorSpec(style="single", hinge_side="right"),
        ),
    ],
)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"\nFurniture tool — {SPEC.label}")
    print("=" * 50)

    # ── 1. Solve ─────────────────────────────────────────────────────────────
    print("\n[1/3] Solving constraints …")
    try:
        resolved = solve(SPEC)
    except Exception as e:
        print(f"  ERROR: {e}")
        return

    print(f"  OK — {len(resolved.panels)} panels resolved")
    print(f"  Outer: {resolved.outer_width:.0f} × "
          f"{resolved.outer_height:.0f} × {resolved.outer_depth:.0f} mm")
    for w in resolved.warnings:
        print(f"  ⚠  {w}")

    # ── 2. Build FreeCAD geometry (skipped if FreeCAD not available) ──────────
    print("\n[2/3] Building 3-D geometry …")
    try:
        import FreeCAD as App
        import cabinet as CAB

        doc = App.newDocument(SPEC.label.replace(" ", "_"))
        feat_map = CAB.build(doc, resolved)
        doc.recompute()

        fcstd_path = os.path.join(OUTPUT_DIR, f"{SPEC.label}.FCStd")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        doc.saveAs(fcstd_path)
        print(f"  Saved FreeCAD model → {fcstd_path}")

        # Open 3-D view if running inside FreeCAD GUI
        try:
            import FreeCADGui
            FreeCADGui.SendMsgToActiveView("ViewFit")
            FreeCADGui.ActiveDocument = App.ActiveDocument
        except Exception:
            pass

    except ImportError:
        print("  FreeCAD not found — skipping 3-D build (exports still run).")

    # ── 3. Export ─────────────────────────────────────────────────────────────
    print("\n[3/3] Exporting …")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    dxf_paths = E.export_dxf(resolved, OUTPUT_DIR)
    print(f"  DXF  — {len(dxf_paths)} panel drawings → {OUTPUT_DIR}/")

    svg_paths = E.export_svg(resolved, OUTPUT_DIR)
    print(f"  SVG  — {len(svg_paths)} cut sheet(s)   → {OUTPUT_DIR}/")

    bom_path  = E.export_bom(resolved, OUTPUT_DIR)
    print(f"  BOM  — {bom_path}")

    print(f"\nDone.  All output in: {OUTPUT_DIR}/\n")


if __name__ == "__main__":
    main()
