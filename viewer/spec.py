"""
viewer/spec.py — Edit this file to change what's rendered.
The viewer auto-reloads within 2 seconds of saving.

furniture_tool/ is already on sys.path when this runs (set by geometry_exporter.py).
"""
from solver import FurnitureSpec, ColumnSpec, DrawerSpec, DoorSpec

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
