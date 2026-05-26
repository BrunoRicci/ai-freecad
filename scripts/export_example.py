"""
export_example.py — parametric L-bracket demo using boolean operations.

Usage:
    python3 scripts/export_example.py               # uses defaults: width=10 height=20
    python3 scripts/export_example.py 15 30
    python3 scripts/export_example.py --width 15 --height 30

Exports output/bracket.step and output/bracket.stl.
"""

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import FreeCAD as App
import Part
import Mesh

import argparse

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")


def parse_args():
    p = argparse.ArgumentParser(description="Generate a parametric L-bracket")
    p.add_argument("width",  nargs="?", type=float, default=10.0,
                   help="Overall width in mm (default: 10.0)")
    p.add_argument("height", nargs="?", type=float, default=20.0,
                   help="Overall height in mm (default: 20.0)")
    p.add_argument("--width",  dest="width",  type=float)
    p.add_argument("--height", dest="height", type=float)
    args = p.parse_args()
    return args.width, args.height


def make_bracket(width: float, height: float) -> Part.Shape:
    """
    L-shaped bracket: a full rectangle with a rectangular notch cut from
    the top-right corner, leaving an L cross-section.

    Dimensions are proportional to width × height.
    Depth (Z) is fixed at width / 2 for a sensible aspect ratio.
    Wall thickness is 25 % of the smaller dimension.
    """
    depth     = width / 2
    thickness = min(width, height) * 0.25

    # Outer box
    outer = Part.makeBox(width, depth, height)

    # Notch: removed from the top-right corner (x > thickness, z > thickness)
    notch_w = width  - thickness
    notch_h = height - thickness
    notch = Part.makeBox(notch_w, depth, notch_h)
    notch.translate(App.Vector(thickness, 0, thickness))

    bracket = outer.cut(notch)
    return bracket


def export_step(shape, path):
    shape.exportStep(path)
    print(f"  Exported STEP → {path}")


def export_stl(shape, path):
    mesh = Mesh.Mesh(shape.tessellate(0.1))
    mesh.write(path)
    print(f"  Exported STL  → {path}")


def main():
    width, height = parse_args()

    print(f"Generating L-bracket: width={width} mm, height={height} mm")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    bracket = make_bracket(width, height)

    bb  = bracket.BoundBox
    vol = bracket.Volume

    print(f"  Bounding box: {bb.XLength:.3f} × {bb.YLength:.3f} × {bb.ZLength:.3f} mm")
    print(f"  Volume:       {vol:.3f} mm³")

    step_path = os.path.join(OUTPUT_DIR, "bracket.step")
    stl_path  = os.path.join(OUTPUT_DIR, "bracket.stl")

    print("\nExporting...")
    export_step(bracket, step_path)
    export_stl( bracket, stl_path)

    print("\nDone. Files are in output/")


if __name__ == "__main__":
    main()
