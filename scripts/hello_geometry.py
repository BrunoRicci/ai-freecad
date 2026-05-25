"""
hello_geometry.py — basic FreeCAD headless demo.

Creates a Box and a Cylinder, then exports them to output/ as STEP and STL.
Run from repo root: python3 scripts/hello_geometry.py
"""

import os
import sys

# Suppress any Qt / display warnings that leak from the headless libs
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import FreeCAD as App
import Part
import Mesh

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")


def ensure_output():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def make_box(doc):
    box = doc.addObject("Part::Box", "Box")
    box.Length = 20.0   # mm
    box.Width  = 10.0
    box.Height = 5.0
    return box


def make_cylinder(doc):
    cyl = doc.addObject("Part::Cylinder", "Cylinder")
    cyl.Radius = 4.0    # mm
    cyl.Height = 15.0
    # Offset along X so the two shapes don't overlap
    cyl.Placement = App.Placement(
        App.Vector(30, 0, 0),
        App.Rotation(App.Vector(0, 0, 1), 0)
    )
    return cyl


def report(label, shape):
    print(f"  {label}: type={shape.Shape.ShapeType}, volume={shape.Shape.Volume:.3f} mm³")


def export_step(shape_obj, path):
    Part.export([shape_obj], path)
    print(f"  Exported STEP → {path}")


def export_stl(shape_obj, path):
    mesh = App.ActiveDocument.addObject("Mesh::Feature", shape_obj.Name + "_mesh")
    mesh.Mesh = Mesh.Mesh(shape_obj.Shape.tessellate(0.1))
    Mesh.export([mesh], path)
    print(f"  Exported STL  → {path}")


def main():
    ensure_output()

    doc = App.newDocument("HelloGeometry")

    box = make_box(doc)
    cyl = make_cylinder(doc)

    doc.recompute()

    print("Shapes created:")
    report("Box",      box)
    report("Cylinder", cyl)

    print("\nExporting...")
    export_step(box, os.path.join(OUTPUT_DIR, "box.step"))
    export_stl( cyl, os.path.join(OUTPUT_DIR, "cylinder.stl"))

    print("\nDone. Files are in output/")


if __name__ == "__main__":
    main()
