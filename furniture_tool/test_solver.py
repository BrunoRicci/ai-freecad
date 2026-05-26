"""
test_solver.py — Unit tests for the constraint solver.
Run with: python test_solver.py

Zero FreeCAD dependency — tests run anywhere.
"""

import sys
import traceback
from solver import (
    FurnitureSpec, ColumnSpec, DrawerSpec, DoorSpec,
    solve, ConstraintError
)
import config as C

PASS = "  ✓"
FAIL = "  ✗"
results = []

def check(name, fn):
    try:
        fn()
        print(f"{PASS} {name}")
        results.append(True)
    except AssertionError as e:
        print(f"{FAIL} {name}")
        print(f"       AssertionError: {e}")
        results.append(False)
    except Exception as e:
        print(f"{FAIL} {name}")
        traceback.print_exc()
        results.append(False)

def expect_error(name, fn, msg_fragment=""):
    try:
        fn()
        print(f"{FAIL} {name}  — expected ConstraintError, got none")
        results.append(False)
    except ConstraintError as e:
        if msg_fragment and msg_fragment not in str(e):
            print(f"{FAIL} {name}  — wrong error: {e}")
            results.append(False)
        else:
            print(f"{PASS} {name}")
            results.append(True)
    except Exception as e:
        print(f"{FAIL} {name}  — unexpected exception: {e}")
        results.append(False)


# ============================================================
print("\n── Basic carcass ──")
# ============================================================

def test_simple_carcass():
    spec = FurnitureSpec(max_width=800, max_height=720, max_depth=580)
    r = solve(spec)

    # Outer dims match target
    assert r.outer_width  == 800, f"width {r.outer_width}"
    assert r.outer_height == 720, f"height {r.outer_height}"
    assert r.outer_depth  == 580, f"depth {r.outer_depth}"

    # Inner dims account for panels
    T = C.THICKNESS
    assert r.inner_width  == 800 - 2*T,          f"inner_w {r.inner_width}"
    assert r.inner_height == 720 - 2*T,           f"inner_h {r.inner_height}"
    assert r.inner_depth  == 580 - T - C.BACK_THICKNESS, f"inner_d {r.inner_depth}"

    # Must have 4 carcass panels + 1 back
    roles = [p.role for p in r.panels]
    assert "side_left"  in roles
    assert "side_right" in roles
    assert "top"        in roles
    assert "bottom"     in roles
    assert "back"       in roles

check("simple carcass resolves correctly", test_simple_carcass)


def test_panel_positions_non_negative():
    spec = FurnitureSpec(max_width=800, max_height=720, max_depth=580)
    r = solve(spec)
    for p in r.panels:
        assert p.pos_x >= 0, f"{p.label} pos_x={p.pos_x}"
        assert p.pos_y >= 0, f"{p.label} pos_y={p.pos_y}"
        assert p.pos_z >= 0, f"{p.label} pos_z={p.pos_z}"

check("all panel positions are non-negative", test_panel_positions_non_negative)


def test_no_back():
    spec = FurnitureSpec(max_width=600, max_height=720, max_depth=400, has_back=False)
    r = solve(spec)
    roles = [p.role for p in r.panels]
    assert "back" not in roles
    assert r.inner_depth == 400 - C.THICKNESS

check("no-back cabinet omits back panel", test_no_back)


def test_custom_thickness():
    spec = FurnitureSpec(max_width=800, max_height=720, max_depth=580, thickness=15)
    r = solve(spec)
    assert r.thickness == 15
    assert r.inner_width == 800 - 2*15

check("custom thickness propagates", test_custom_thickness)


# ============================================================
print("\n── Columns & dividers ──")
# ============================================================

def test_two_columns_auto():
    spec = FurnitureSpec(
        max_width=900, max_height=720, max_depth=580,
        columns=[ColumnSpec(label="A"), ColumnSpec(label="B")]
    )
    r = solve(spec)
    T = C.THICKNESS
    inner_w = 900 - 2*T
    # One divider = T wide, two equal columns
    expected_col_w = (inner_w - T) / 2
    col_panels = [p for p in r.panels if p.role == "divider"]
    assert len(col_panels) == 1, f"expected 1 divider, got {len(col_panels)}"
    divider = col_panels[0]
    assert abs(divider.width - T) < 0.01

check("two auto-width columns create one divider", test_two_columns_auto)


def test_mixed_column_widths():
    spec = FurnitureSpec(
        max_width=1000, max_height=720, max_depth=580,
        columns=[
            ColumnSpec(label="Fixed", width=300),
            ColumnSpec(label="Auto"),
        ]
    )
    r = solve(spec)
    T = C.THICKNESS
    inner_w = 1000 - 2*T
    # auto col = inner_w - divider - fixed
    expected_auto = inner_w - T - 300
    # Check no ConstraintError and panels resolved
    assert len(r.panels) > 4

check("mixed fixed+auto column widths resolve", test_mixed_column_widths)


def test_three_columns():
    spec = FurnitureSpec(
        max_width=1500, max_height=720, max_depth=580,
        columns=[ColumnSpec(f"Col{i}") for i in range(3)]
    )
    r = solve(spec)
    dividers = [p for p in r.panels if p.role == "divider"]
    assert len(dividers) == 2

check("three columns create two dividers", test_three_columns)


# ============================================================
print("\n── Shelves ──")
# ============================================================

def test_shelves():
    spec = FurnitureSpec(
        max_width=800, max_height=720, max_depth=580,
        columns=[ColumnSpec(label="Main", shelf_count=2)]
    )
    r = solve(spec)
    shelves = [p for p in r.panels if p.role == "shelf"]
    assert len(shelves) == 2, f"expected 2 shelves, got {len(shelves)}"
    # Shelves must be inside the carcass horizontally
    T = C.THICKNESS
    for sh in shelves:
        assert sh.pos_z > T, f"shelf below bottom panel: {sh.pos_z}"
        assert sh.pos_z < 720 - T, f"shelf above top panel: {sh.pos_z}"

check("2 shelves created inside carcass", test_shelves)


# ============================================================
print("\n── Drawers ──")
# ============================================================

def test_single_drawer():
    spec = FurnitureSpec(
        max_width=600, max_height=720, max_depth=580,
        columns=[ColumnSpec(label="D", drawers=[DrawerSpec(label="Drw1")])]
    )
    r = solve(spec)
    fronts = [p for p in r.panels if p.role == "drawer_front"]
    assert len(fronts) == 1
    sides  = [p for p in r.panels if p.role == "drawer_side"]
    assert len(sides) == 2
    backs  = [p for p in r.panels if p.role == "drawer_back"]
    assert len(backs) == 1
    slides = r.slides
    assert len(slides) == 2  # left + right

check("single drawer produces correct panels + slides", test_single_drawer)


def test_three_drawers_auto_height():
    spec = FurnitureSpec(
        max_width=600, max_height=720, max_depth=580,
        columns=[ColumnSpec(
            label="D",
            drawers=[DrawerSpec(f"Drw{i}") for i in range(3)]
        )]
    )
    r = solve(spec)
    fronts = [p for p in r.panels if p.role == "drawer_front"]
    assert len(fronts) == 3
    # All fronts should have the same auto height
    heights = set(round(p.height, 2) for p in fronts)
    assert len(heights) == 1, f"unequal auto heights: {heights}"

check("3 auto-height drawers are equal", test_three_drawers_auto_height)


def test_mixed_drawer_heights():
    spec = FurnitureSpec(
        max_width=600, max_height=720, max_depth=580,
        columns=[ColumnSpec(
            label="D",
            drawers=[
                DrawerSpec("Fixed", height=200),
                DrawerSpec("Auto"),
            ]
        )]
    )
    r = solve(spec)
    fronts = {p.label: p for p in r.panels if p.role == "drawer_front"}
    assert abs(fronts["Fixed_Front"].height - 200) < 0.01

check("mixed fixed+auto drawer heights resolve", test_mixed_drawer_heights)


# ============================================================
print("\n── Doors & hinges ──")
# ============================================================

def test_single_door():
    spec = FurnitureSpec(
        max_width=600, max_height=720, max_depth=580,
        toe_kick_height=100,
        columns=[ColumnSpec(
            label="C",
            has_door=True,
            door=DoorSpec(style="single", hinge_side="left")
        )]
    )
    r = solve(spec)
    doors = [p for p in r.panels if p.role == "door"]
    assert len(doors) == 1
    door = doors[0]
    expected_h = 720 - 100 - C.GAP_DOOR * 2
    assert abs(door.height - expected_h) < 0.01, f"door height {door.height}"

    # Hinges
    assert len(r.hinges) >= 2   # at least top + bottom
    for h in r.hinges:
        assert h.hinge_side == "left"

check("single door with correct height and hinges", test_single_door)


def test_double_door():
    spec = FurnitureSpec(
        max_width=900, max_height=720, max_depth=580,
        toe_kick_height=100,
        columns=[ColumnSpec(
            label="Wide",
            has_door=True,
            door=DoorSpec(style="double")
        )]
    )
    r = solve(spec)
    doors = [p for p in r.panels if p.role == "door"]
    assert len(doors) == 2

check("double door produces 2 door panels", test_double_door)


def test_tall_door_gets_third_hinge():
    spec = FurnitureSpec(
        max_width=600, max_height=1400, max_depth=580,
        toe_kick_height=100,
        columns=[ColumnSpec(
            label="Tall",
            has_door=True,
            door=DoorSpec(style="single")
        )]
    )
    r = solve(spec)
    assert len(r.hinges) == 3, f"expected 3 hinges for tall door, got {len(r.hinges)}"

check("door > 1200mm tall gets 3rd hinge", test_tall_door_gets_third_hinge)


# ============================================================
print("\n── Constraint violations (must raise ConstraintError) ──")
# ============================================================

expect_error(
    "cabinet too narrow for panels",
    lambda: solve(FurnitureSpec(max_width=30, max_height=720, max_depth=580)),
    "Inner width"
)

expect_error(
    "column widths exceed inner width",
    lambda: solve(FurnitureSpec(
        max_width=600, max_height=720, max_depth=580,
        columns=[
            ColumnSpec("A", width=400),
            ColumnSpec("B", width=400),
        ]
    )),
    "exceed inner width"
)

expect_error(
    "target_width exceeds max_width",
    lambda: solve(FurnitureSpec(max_width=800, target_width=900, max_height=720, max_depth=580)),
    "exceeds max_width"
)

expect_error(
    "too many drawers for cabinet height",
    lambda: solve(FurnitureSpec(
        max_width=600, max_height=300, max_depth=580,
        columns=[ColumnSpec(
            label="D",
            drawers=[DrawerSpec(f"D{i}") for i in range(8)]
        )]
    )),
)


# ============================================================
print("\n── Board size warnings ──")
# ============================================================

def test_oversized_warns():
    spec = FurnitureSpec(max_width=3000, max_height=720, max_depth=580)
    r = solve(spec)
    assert any("3000" in w or "width" in w for w in r.warnings), \
        f"expected board width warning, got: {r.warnings}"

check("oversized panel generates warning", test_oversized_warns)


# ============================================================
print("\n── Summary ──")
# ============================================================
passed = sum(results)
total  = len(results)
print(f"\n  {passed}/{total} tests passed", "✓" if passed == total else "✗ — see failures above")
sys.exit(0 if passed == total else 1)
