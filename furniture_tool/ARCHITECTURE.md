# Furniture Tool — Architecture & Design Reference

## Overview

A Python scripting tool that generates parametric wooden furniture models in FreeCAD 1.x,
validates dimensions mathematically before creating any geometry, and exports CNC-ready
files and a bill of materials.

---

## Material & Construction

- **Material:** Melamine board (sheet goods)
- **Default thickness:** 18mm (variable, set in `config.py`)
- **Back panel:** 8mm HDF/thin board
- **Joinery:** Confirmat screws (pocket + countersink bores)
- **Max board size:** 2750 × 1830mm (configurable — varies by supplier)

---

## Hardware

| Item | Spec |
|---|---|
| Drawer slides | Side-mount, soft-close, ball bearing |
| Hinges | European cup hinges, 35mm boring, standard backset |
| Handles | Surface-mounted, standard hole spacing (default 128mm centres) |

---

## Input

- Sketch as photo or hand-drawn image
- Maximum or obligatory dimensions (text)
- Melamine board thickness
- Drawer placement and distribution
- Door placement and distribution

---

## Processing Pipeline

```
Input spec
    │
    ▼
1. Constraint solver (pure math, no FreeCAD)
   - Validates all dimensions
   - Computes every panel size
   - Raises ConstraintError with human-readable message if conflict detected
   - Only proceeds if all checks pass
    │
    ├── FAIL → print error report, stop
    │
    ▼
2. Layout engine
   - Distributes columns, shelves, drawers, doors
   - Resolves auto widths/heights from available space
   - Applies gaps, tolerances, hardware clearances
    │
    ▼
3. Part builder (FreeCAD geometry)
   - Part.makeBox + Placement for each panel
   - Boolean cuts for confirmat holes, hinge bores
   - Named objects, organized in document groups
    │
    ▼
4. FreeCAD assembly
   - Groups: carcass, doors, drawers, hardware
   - Opens/refreshes 3D view for visual review
   - User inspects, adjusts variables in config, re-runs
    │
    ▼
Output (all four generated together)
```

**Key rule:** Validate first → layout → geometry. Never create geometry before the math is clean.

---

## Output Files

| File | Format | Purpose |
|---|---|---|
| FreeCAD model | `.FCStd` | Parametric 3D model, managed by FreeCAD export |
| Panel drawings | `.DXF` (R14) | One file per panel, flat 2D projection for CNC |
| Cut sheet | `.SVG` | All panels labeled with dimensions, one page per board |
| Bill of materials | `.CSV` | Panel dims + quantities + hardware list |

**CNC output:** Generic controller (no specific CAM software targeted). DXF R14 + separate
drilling file for confirmat holes and hinge borings. Panel nesting (fitting pieces on board
sheets) is handled by the CAM software, not this tool (deferred to future release).

---

## Parametric Design Rules

- **No hardcoded numbers anywhere** except `config.py`
- All dimensions derive from ~15 top-level variables in `config.py`
- Edit `config.py` → re-run → entire model updates
- Variables are reused across modules; no duplication

---

## File Structure

```
furniture_tool/
│
├── config.py         # Single source of truth — all variables (thickness, gaps,
│                     # board size, hardware dims, tolerances, colors)
│
├── solver.py         # Constraint solver — pure math, no FreeCAD imports
│                     # Input: FurnitureSpec → Output: ResolvedSpec
│                     # Raises ConstraintError with explanation on conflict
│
├── panel.py          # Panel class
│                     # ResolvedPanel → Part.makeBox + Placement + label + color
│                     # Knows its role: side, top, bottom, shelf, back, door, drawer
│
├── joinery.py        # Confirmat hole geometry (pocket + countersink)
│                     # Applied as boolean cuts on panels
│                     # Hinge cup bore (35mm cylinder cut into door)
│
├── hardware.py       # Drawer slide positioning rules
│                     # Handle hole pairs
│                     # Positions derived from config, never hardcoded
│
├── cabinet.py        # High-level assembler
│                     # Calls panel.py for each ResolvedPanel
│                     # Calls joinery.py for joints
│                     # Groups everything in FreeCAD document tree
│
├── export.py         # DXF flat projection per panel
│                     # SVG labeled cut sheet
│                     # BOM as CSV
│
├── main.py           # Entry point
│                     # Define FurnitureSpec → solve() → build → export
│                     # Run as FreeCAD macro (recommended) or via console
│
├── test_solver.py    # Unit tests for solver (19/19 passing)
│                     # Zero FreeCAD dependency — runs anywhere
│
└── ARCHITECTURE.md   # This file
```

---

## Key Data Structures

### Input: `FurnitureSpec`
```python
FurnitureSpec(
    label         = "Cabinet",
    max_width     = 800,      # mm — hard constraint
    max_height    = 720,
    max_depth     = 580,
    target_width  = None,     # None → use full max
    target_height = None,
    target_depth  = None,
    toe_kick_height = 100,    # mm — 0 if flush to floor
    has_back      = True,
    columns       = [ColumnSpec(...)],
    thickness     = None,     # None → use config.THICKNESS
)
```

### Column definition: `ColumnSpec`
```python
ColumnSpec(
    label       = "Column",
    width       = None,       # None → auto-distributed evenly
    has_door    = False,
    door        = DoorSpec(style="single", hinge_side="left"),
    drawers     = [DrawerSpec(label="D1", height=None), ...],
    shelf_count = 2,
)
```

### Output: `ResolvedSpec`
Contains lists of:
- `ResolvedPanel` — label, role, width, height, depth, pos_x/y/z, grain_dir
- `ResolvedHinge` — door label, cup_x, cup_z, hinge_side
- `ResolvedSlide` — drawer label, side, length, pos_x, pos_z
- `warnings` — list of non-fatal issues (e.g. panel exceeds board size)

---

## Gaps & Tolerances (defaults in `config.py`)

| Variable | Value | Meaning |
|---|---|---|
| `GAP_DOOR` | 2.0mm | Each side between door edge and carcass |
| `GAP_DRAWER_SIDE` | 12.5mm | Each side for slide hardware |
| `GAP_DRAWER_TOP` | 3.0mm | Above drawer front |
| `GAP_DRAWER_BOTTOM` | 3.0mm | Below drawer front |
| `GAP_SHELF` | 0.5mm | Shelf-to-side clearance |
| `TOLERANCE_SAW` | 0.5mm | CNC kerf tolerance |
| `TOLERANCE_ASSEMBLY` | 0.2mm | Drill/bore fit tolerance |

---

## Confirmat Screw Geometry

| Variable | Value |
|---|---|
| `CONFIRMAT_DIAMETER` | 7.0mm |
| `CONFIRMAT_HEAD_DIAMETER` | 10.0mm |
| `CONFIRMAT_HEAD_DEPTH` | 7.0mm |
| `CONFIRMAT_HOLE_DEPTH` | 50.0mm |
| `CONFIRMAT_EDGE_OFFSET` | 37.0mm from panel edge |
| `CONFIRMAT_MIN_SPACING` | 150.0mm between screws |
| `CONFIRMAT_MAX_SPACING` | 400.0mm between screws |

---

## Hinge Geometry (European Cup)

| Variable | Value |
|---|---|
| `HINGE_CUP_DIAMETER` | 35.0mm |
| `HINGE_CUP_DEPTH` | 13.5mm |
| `HINGE_BACKSET` | 37.0mm from door edge |
| `HINGE_FROM_TOP` | 100.0mm from door top |
| `HINGE_FROM_BOTTOM` | 100.0mm from door bottom |
| `HINGE_MAX_SPAN` | 1200mm → adds 3rd hinge above this |

---

## FreeCAD Version & Run Method

- **Version:** FreeCAD 1.x series
- **Recommended run method:** Macro (Macro menu → one-click run)
- Scripts are also compatible with FreeCAD's built-in Python console and
  command-line execution (`FreeCAD main.py`)

---

## Build Status

| Module | Status |
|---|---|
| `config.py` | ✅ Done |
| `solver.py` | ✅ Done — 19/19 tests passing |
| `test_solver.py` | ✅ Done |
| `panel.py` | 🔲 Next |
| `joinery.py` | 🔲 Pending |
| `hardware.py` | 🔲 Pending |
| `cabinet.py` | 🔲 Pending |
| `export.py` | 🔲 Pending |
| `main.py` | 🔲 Pending |
| Input parser (image/text) | 🔲 Future release |
| Panel nesting (CNC sheet optimizer) | 🔲 Future release |
