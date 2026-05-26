#!/usr/bin/env python3
"""
Runs the furniture solver and prints a JSON geometry description to stdout.
Called as a subprocess by viewer/server.py on every file change.
"""
import sys
import os
import json
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "furniture_tool"))
sys.path.insert(0, os.path.join(ROOT, "viewer"))

from solver import (
    solve, ConstraintError,
    FurnitureSpec, ColumnSpec, DrawerSpec, DoorSpec,
)

# Load user spec, fall back to built-in demo
try:
    import spec as _spec_mod
    furniture_spec = _spec_mod.SPEC
except (ImportError, AttributeError):
    furniture_spec = FurnitureSpec(
        label="Demo Cabinet",
        max_width=1200,
        max_height=800,
        max_depth=580,
        toe_kick_height=100,
        columns=[
            ColumnSpec(label="Left",
                       has_door=True,
                       door=DoorSpec(style="single", hinge_side="left")),
            ColumnSpec(label="Middle",
                       drawers=[DrawerSpec("D1"), DrawerSpec("D2"), DrawerSpec("D3")]),
            ColumnSpec(label="Right",
                       shelf_count=3,
                       has_door=True,
                       door=DoorSpec(style="single", hinge_side="right")),
        ],
    )

try:
    resolved = solve(furniture_spec)

    panels = [
        dict(
            label=p.label, role=p.role,
            width=p.width, height=p.height, depth=p.depth,
            pos_x=p.pos_x, pos_y=p.pos_y, pos_z=p.pos_z,
        )
        for p in resolved.panels
    ]

    output = dict(
        ok=True,
        label=resolved.label,
        outer=dict(
            width=resolved.outer_width,
            height=resolved.outer_height,
            depth=resolved.outer_depth,
        ),
        panels=panels,
        warnings=resolved.warnings,
    )

except ConstraintError as e:
    output = dict(ok=False, error=str(e))
except Exception:
    output = dict(ok=False, error=traceback.format_exc())

print(json.dumps(output))
