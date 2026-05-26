"""
solver.py — Constraint solver for wooden furniture.

Pure Python — zero FreeCAD imports.
Input : a furniture spec dict (see FurnitureSpec dataclass).
Output: a ResolvedSpec dataclass with every panel dimension computed.

Raises ConstraintError with a human-readable explanation if any
dimension conflict is detected, before any geometry is created.

All dimensions in millimetres.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional

import config as C


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class ConstraintError(Exception):
    """Raised when the solver detects a dimensional conflict."""
    pass


# ---------------------------------------------------------------------------
# Input spec dataclasses
# ---------------------------------------------------------------------------

@dataclass
class DrawerSpec:
    """Describes one drawer opening within a column."""
    label: str = "Drawer"
    height: Optional[float] = None   # None → solver distributes evenly


@dataclass
class DoorSpec:
    """Describes one door (or door pair) for a cabinet zone."""
    label: str = "Door"
    style: str = "single"            # "single" | "double" (pair meeting in middle)
    hinge_side: str = "left"         # "left" | "right" (ignored for double)


@dataclass
class ColumnSpec:
    """
    A vertical column inside the carcass.
    A cabinet can have 1..N columns side by side.
    Each column can have shelves, drawers, doors, or a mix.
    """
    label: str = "Column"
    width: Optional[float] = None    # None → solver distributes remaining width evenly
    has_door: bool = False
    door: Optional[DoorSpec] = None
    drawers: List[DrawerSpec] = field(default_factory=list)
    shelf_count: int = 0             # Fixed shelves (not counting top/bottom)
    # If both drawers and shelf_count > 0, drawers occupy the bottom zone.


@dataclass
class FurnitureSpec:
    """
    Top-level furniture specification.
    Provide the maximum envelope; the solver fills it optimally.
    """
    label: str = "Cabinet"

    # Outer envelope constraints (maximum allowed, not necessarily final size)
    max_width:  float = 800.0
    max_height: float = 720.0
    max_depth:  float = 580.0

    # Leave these None to let the solver use the full envelope
    target_width:  Optional[float] = None
    target_height: Optional[float] = None
    target_depth:  Optional[float] = None

    # Toe kick (plinth) at the bottom — set to 0 if flush-to-floor
    toe_kick_height: float = 100.0   # mm
    toe_kick_depth:  float = 60.0    # mm (how far it's set back from front face)

    # Back panel — True = full back, False = no back
    has_back: bool = True

    # Columns that make up this cabinet
    columns: List[ColumnSpec] = field(default_factory=lambda: [ColumnSpec()])

    # Material overrides (None → use config.py defaults)
    thickness: Optional[float] = None
    back_thickness: Optional[float] = None


# ---------------------------------------------------------------------------
# Resolved output dataclasses
# ---------------------------------------------------------------------------

@dataclass
class ResolvedPanel:
    label: str
    role: str          # "side_left" | "side_right" | "top" | "bottom" |
                       # "shelf" | "back" | "door" | "drawer_front" |
                       # "drawer_side" | "drawer_back" | "drawer_bottom"
    width: float       # mm — dimension along X (cabinet width axis)
    height: float      # mm — dimension along Z (cabinet height axis)
    depth: float       # mm — dimension along Y (cabinet depth axis)
    # Position of panel's front-bottom-left corner relative to cabinet origin
    pos_x: float = 0.0
    pos_y: float = 0.0
    pos_z: float = 0.0
    grain_dir: str = "vertical"   # "vertical" | "horizontal" — for CNC grain
    column_index: int = 0
    quantity: int = 1


@dataclass
class ResolvedHinge:
    label: str
    door_label: str
    cup_x: float       # from door left edge
    cup_z: float       # from door bottom edge
    hinge_side: str    # "left" | "right"


@dataclass
class ResolvedSlide:
    label: str
    drawer_label: str
    side: str          # "left" | "right"
    length: float      # slide length = drawer depth
    pos_x: float       # x position relative to cabinet
    pos_z: float       # z (height) of slide bottom


@dataclass
class ResolvedSpec:
    label: str
    outer_width: float
    outer_height: float
    outer_depth: float
    inner_width: float
    inner_height: float
    inner_depth: float
    thickness: float
    back_thickness: float
    toe_kick_height: float
    panels: List[ResolvedPanel] = field(default_factory=list)
    hinges: List[ResolvedHinge] = field(default_factory=list)
    slides: List[ResolvedSlide] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Solver
# ---------------------------------------------------------------------------

class FurnitureSolver:
    """
    Resolves a FurnitureSpec into a ResolvedSpec.
    All validation happens here — geometry builders trust the output blindly.
    """

    def __init__(self, spec: FurnitureSpec):
        self.spec = spec
        self.T  = spec.thickness      if spec.thickness      else C.THICKNESS
        self.BT = spec.back_thickness if spec.back_thickness else C.BACK_THICKNESS
        self.warnings: List[str] = []

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def solve(self) -> ResolvedSpec:
        s = self.spec

        outer_w, outer_h, outer_d = self._resolve_outer_dims()
        self._validate_board_size(outer_w, outer_h, outer_d)

        inner_w = outer_w - 2 * self.T
        inner_h = outer_h - self.T - self.T  # top and bottom panels
        if s.has_back:
            inner_d = outer_d - self.T - self.BT  # front open + back panel
        else:
            inner_d = outer_d - self.T

        if inner_w <= 0:
            raise ConstraintError(
                f"Inner width {inner_w:.1f}mm ≤ 0. "
                f"Outer width {outer_w:.1f}mm is too narrow for two side panels "
                f"of {self.T}mm each."
            )
        if inner_h <= 0:
            raise ConstraintError(
                f"Inner height {inner_h:.1f}mm ≤ 0. "
                f"Outer height {outer_h:.1f}mm is too short for top+bottom panels."
            )

        col_widths = self._resolve_column_widths(inner_w)

        panels: List[ResolvedPanel] = []
        hinges: List[ResolvedHinge] = []
        slides: List[ResolvedSlide] = []

        # --- Carcass panels ---
        panels += self._make_carcass(outer_w, outer_h, outer_d, inner_d)

        # --- Column internals ---
        x_cursor = self.T  # start after left side panel
        for i, (col, col_w) in enumerate(zip(s.columns, col_widths)):
            col_panels, col_hinges, col_slides = self._solve_column(
                col, i, col_w, inner_h, inner_d, outer_h, outer_d,
                x_cursor, s.toe_kick_height
            )
            panels += col_panels
            hinges += col_hinges
            slides += col_slides

            x_cursor += col_w
            # Add a divider panel between columns (but not after the last one)
            if i < len(s.columns) - 1:
                divider = ResolvedPanel(
                    label=f"Divider_{i+1}",
                    role="divider",
                    width=self.T,
                    height=inner_h,
                    depth=inner_d,
                    pos_x=x_cursor,
                    pos_y=self.T,           # behind front face
                    pos_z=self.T,           # above bottom panel
                    grain_dir="vertical",
                    column_index=i,
                )
                panels.append(divider)
                x_cursor += self.T

        # --- Back panel ---
        if s.has_back:
            panels.append(ResolvedPanel(
                label="Back",
                role="back",
                width=inner_w,
                height=inner_h,
                depth=self.BT,
                pos_x=self.T,
                pos_y=outer_d - self.BT,
                pos_z=self.T,
                grain_dir="vertical",
            ))

        resolved = ResolvedSpec(
            label=s.label,
            outer_width=outer_w,
            outer_height=outer_h,
            outer_depth=outer_d,
            inner_width=inner_w,
            inner_height=inner_h,
            inner_depth=inner_d,
            thickness=self.T,
            back_thickness=self.BT,
            toe_kick_height=s.toe_kick_height,
            panels=panels,
            hinges=hinges,
            slides=slides,
            warnings=self.warnings,
        )

        self._validate_final(resolved)
        return resolved

    # ------------------------------------------------------------------
    # Outer dimension resolution
    # ------------------------------------------------------------------

    def _resolve_outer_dims(self):
        s = self.spec
        w = s.target_width  if s.target_width  else s.max_width
        h = s.target_height if s.target_height else s.max_height
        d = s.target_depth  if s.target_depth  else s.max_depth

        if w > s.max_width:
            raise ConstraintError(
                f"target_width {w}mm exceeds max_width {s.max_width}mm."
            )
        if h > s.max_height:
            raise ConstraintError(
                f"target_height {h}mm exceeds max_height {s.max_height}mm."
            )
        if d > s.max_depth:
            raise ConstraintError(
                f"target_depth {d}mm exceeds max_depth {s.max_depth}mm."
            )
        return w, h, d

    # ------------------------------------------------------------------
    # Board size validation
    # ------------------------------------------------------------------

    def _validate_board_size(self, w, h, d):
        if w > C.BOARD_MAX_WIDTH:
            self.warnings.append(
                f"Cabinet width {w:.0f}mm exceeds board max width "
                f"{C.BOARD_MAX_WIDTH}mm. Top/bottom panels will need joining."
            )
        if h > C.BOARD_MAX_HEIGHT:
            self.warnings.append(
                f"Cabinet height {h:.0f}mm exceeds board max height "
                f"{C.BOARD_MAX_HEIGHT}mm. Side panels will need joining."
            )

    # ------------------------------------------------------------------
    # Column width distribution
    # ------------------------------------------------------------------

    def _resolve_column_widths(self, inner_w: float) -> List[float]:
        cols = self.spec.columns
        n = len(cols)

        # Total width consumed by dividers between columns
        divider_total = (n - 1) * self.T

        # Fixed-width columns
        fixed_total = sum(c.width for c in cols if c.width is not None)
        auto_count  = sum(1       for c in cols if c.width is None)

        available = inner_w - divider_total - fixed_total
        if available < 0:
            raise ConstraintError(
                f"Column widths ({fixed_total:.1f}mm fixed) + dividers "
                f"({divider_total:.1f}mm) exceed inner width {inner_w:.1f}mm."
            )

        auto_w = (available / auto_count) if auto_count > 0 else 0.0

        widths = []
        for c in cols:
            w = c.width if c.width is not None else auto_w
            if w < 100:
                raise ConstraintError(
                    f"Column '{c.label}' resolved width {w:.1f}mm is below "
                    f"100mm minimum. Reduce column count or increase cabinet width."
                )
            widths.append(w)

        return widths

    # ------------------------------------------------------------------
    # Main carcass panels (sides, top, bottom)
    # ------------------------------------------------------------------

    def _make_carcass(self, outer_w, outer_h, outer_d, inner_d):
        T  = self.T
        panels = []

        # Left side
        panels.append(ResolvedPanel(
            label="Side_Left",
            role="side_left",
            width=T, height=outer_h, depth=outer_d,
            pos_x=0, pos_y=0, pos_z=0,
            grain_dir="vertical",
        ))
        # Right side
        panels.append(ResolvedPanel(
            label="Side_Right",
            role="side_right",
            width=T, height=outer_h, depth=outer_d,
            pos_x=outer_w - T, pos_y=0, pos_z=0,
            grain_dir="vertical",
        ))
        # Top (sits on top of sides — outside dimension)
        panels.append(ResolvedPanel(
            label="Top",
            role="top",
            width=outer_w, height=T, depth=outer_d,
            pos_x=0, pos_y=0, pos_z=outer_h - T,
            grain_dir="horizontal",
        ))
        # Bottom (sits between sides)
        panels.append(ResolvedPanel(
            label="Bottom",
            role="bottom",
            width=outer_w, height=T, depth=outer_d,
            pos_x=0, pos_y=0, pos_z=0,
            grain_dir="horizontal",
        ))

        return panels

    # ------------------------------------------------------------------
    # Column internals: shelves, drawers, doors
    # ------------------------------------------------------------------

    def _solve_column(
        self,
        col: ColumnSpec,
        col_idx: int,
        col_w: float,
        inner_h: float,
        inner_d: float,
        outer_h: float,
        outer_d: float,
        x_start: float,
        toe_kick_h: float,
    ):
        T = self.T
        panels = []
        hinges = []
        slides = []

        # --- Shelves ---
        if col.shelf_count > 0:
            n = col.shelf_count
            # Distribute evenly in inner height
            slot_h = inner_h / (n + 1)
            for i in range(n):
                z = T + slot_h * (i + 1) - T / 2
                panels.append(ResolvedPanel(
                    label=f"{col.label}_Shelf_{i+1}",
                    role="shelf",
                    width=col_w,
                    height=T,
                    depth=inner_d - C.GAP_SHELF,
                    pos_x=x_start,
                    pos_y=T,
                    pos_z=z,
                    grain_dir="horizontal",
                    column_index=col_idx,
                ))

        # --- Drawers ---
        if col.drawers:
            drawer_panels, drawer_slides = self._solve_drawers(
                col, col_idx, col_w, inner_h, inner_d, outer_h, x_start
            )
            panels += drawer_panels
            slides += drawer_slides

        # --- Door ---
        if col.has_door:
            door_spec = col.door or DoorSpec()
            door_panels, door_hinges = self._solve_door(
                door_spec, col, col_idx, col_w, outer_h, outer_d,
                x_start, toe_kick_h
            )
            panels += door_panels
            hinges += door_hinges

        return panels, hinges, slides

    # ------------------------------------------------------------------
    # Drawer geometry
    # ------------------------------------------------------------------

    def _solve_drawers(self, col, col_idx, col_w, inner_h, inner_d, outer_h, x_start):
        T   = self.T
        panels = []
        slides = []

        n_drawers = len(col.drawers)
        total_gaps = (C.GAP_DRAWER_TOP + C.GAP_DRAWER_BOTTOM) * n_drawers
        available_h = inner_h - total_gaps

        # Resolve each drawer height
        fixed_h = sum(d.height for d in col.drawers if d.height is not None)
        auto_count = sum(1 for d in col.drawers if d.height is None)
        auto_h = (available_h - fixed_h) / auto_count if auto_count > 0 else 0.0

        if auto_h < 60:
            raise ConstraintError(
                f"Column '{col.label}': auto drawer height {auto_h:.1f}mm < 60mm. "
                f"Too many drawers or cabinet too short."
            )

        drawer_box_w = col_w - 2 * C.GAP_DRAWER_SIDE
        drawer_box_d = inner_d - T     # drawer depth = inner depth minus front clearance

        if drawer_box_w < 100:
            raise ConstraintError(
                f"Column '{col.label}': drawer box width {drawer_box_w:.1f}mm < 100mm "
                f"after subtracting slide gaps ({C.GAP_DRAWER_SIDE}mm each side)."
            )

        z_cursor = T + C.GAP_DRAWER_BOTTOM  # start from above bottom panel

        for i, drw in enumerate(col.drawers):
            drw_h = drw.height if drw.height is not None else auto_h
            label = drw.label

            # Drawer front (visible face, full opening width)
            front_w = col_w - 2 * C.GAP_DOOR
            panels.append(ResolvedPanel(
                label=f"{label}_Front",
                role="drawer_front",
                width=front_w,
                height=drw_h,
                depth=T,
                pos_x=x_start + C.GAP_DOOR,
                pos_y=0,
                pos_z=z_cursor,
                grain_dir="horizontal",
                column_index=col_idx,
            ))

            # Drawer box sides (2×)
            side_h = drw_h - C.GAP_DRAWER_TOP - C.GAP_DRAWER_BOTTOM - T
            for side, sx in [("Left",  x_start + C.GAP_DRAWER_SIDE),
                              ("Right", x_start + col_w - C.GAP_DRAWER_SIDE - T)]:
                panels.append(ResolvedPanel(
                    label=f"{label}_Box_{side}",
                    role="drawer_side",
                    width=T,
                    height=side_h,
                    depth=drawer_box_d,
                    pos_x=sx,
                    pos_y=T,
                    pos_z=z_cursor + T,
                    grain_dir="horizontal",
                    column_index=col_idx,
                ))

            # Drawer box back
            panels.append(ResolvedPanel(
                label=f"{label}_Box_Back",
                role="drawer_back",
                width=drawer_box_w - 2 * T,
                height=side_h,
                depth=T,
                pos_x=x_start + C.GAP_DRAWER_SIDE + T,
                pos_y=T + drawer_box_d - T,
                pos_z=z_cursor + T,
                grain_dir="horizontal",
                column_index=col_idx,
            ))

            # Drawer bottom (HDF / thin sheet)
            panels.append(ResolvedPanel(
                label=f"{label}_Box_Bottom",
                role="drawer_bottom",
                width=drawer_box_w,
                height=self.BT,
                depth=drawer_box_d,
                pos_x=x_start + C.GAP_DRAWER_SIDE,
                pos_y=T,
                pos_z=z_cursor,
                grain_dir="horizontal",
                column_index=col_idx,
            ))

            # Slides
            for side, sx in [("Left",  x_start + C.GAP_DRAWER_SIDE - C.SLIDE_THICKNESS),
                              ("Right", x_start + col_w - C.GAP_DRAWER_SIDE)]:
                slides.append(ResolvedSlide(
                    label=f"{label}_Slide_{side}",
                    drawer_label=label,
                    side=side.lower(),
                    length=drawer_box_d,
                    pos_x=sx,
                    pos_z=z_cursor + C.SLIDE_VERTICAL_OFFSET,
                ))

            z_cursor += drw_h + C.GAP_DRAWER_TOP + C.GAP_DRAWER_BOTTOM

        return panels, slides

    # ------------------------------------------------------------------
    # Door geometry + hinge layout
    # ------------------------------------------------------------------

    def _solve_door(self, door_spec, col, col_idx, col_w, outer_h, outer_d, x_start, toe_kick_h):
        T = self.T
        panels = []
        hinges = []

        door_h = outer_h - toe_kick_h - C.GAP_DOOR * 2

        if door_spec.style == "double":
            door_w = (col_w - C.GAP_DOOR * 3) / 2   # gap left + middle + right
            door_configs = [
                (f"{col.label}_Door_Left",  x_start + C.GAP_DOOR, "left"),
                (f"{col.label}_Door_Right", x_start + C.GAP_DOOR * 2 + door_w, "right"),
            ]
        else:
            door_w = col_w - C.GAP_DOOR * 2
            door_configs = [
                (f"{col.label}_Door", x_start + C.GAP_DOOR, door_spec.hinge_side),
            ]

        for label, dx, hinge_side in door_configs:
            if door_w < 80:
                raise ConstraintError(
                    f"Door '{label}' width {door_w:.1f}mm < 80mm. "
                    f"Column too narrow for a door with gaps."
                )
            if door_h < 200:
                raise ConstraintError(
                    f"Door '{label}' height {door_h:.1f}mm < 200mm. "
                    f"Cabinet too short for a door with toe kick and gaps."
                )

            panels.append(ResolvedPanel(
                label=label,
                role="door",
                width=door_w,
                height=door_h,
                depth=T,
                pos_x=dx,
                pos_y=-T,           # door sits proud of carcass front face
                pos_z=toe_kick_h + C.GAP_DOOR,
                grain_dir="vertical",
                column_index=col_idx,
            ))

            # Hinge layout
            hinge_positions = self._hinge_positions(door_h)
            for j, hz in enumerate(hinge_positions):
                cup_x = C.HINGE_BACKSET if hinge_side == "left" else door_w - C.HINGE_BACKSET
                hinges.append(ResolvedHinge(
                    label=f"{label}_Hinge_{j+1}",
                    door_label=label,
                    cup_x=cup_x,
                    cup_z=hz,
                    hinge_side=hinge_side,
                ))

        return panels, hinges

    def _hinge_positions(self, door_h: float) -> List[float]:
        """Return Z positions (from door bottom) of hinge cup centres."""
        positions = [C.HINGE_FROM_BOTTOM, door_h - C.HINGE_FROM_TOP]
        if door_h > C.HINGE_MAX_SPAN:
            positions.append(door_h / 2)   # middle hinge
        return sorted(positions)

    # ------------------------------------------------------------------
    # Final cross-validation
    # ------------------------------------------------------------------

    def _validate_final(self, resolved: ResolvedSpec):
        for p in resolved.panels:
            for dim_name, dim_val in [("width", p.width), ("height", p.height), ("depth", p.depth)]:
                if dim_val <= 0:
                    raise ConstraintError(
                        f"Panel '{p.label}' has non-positive {dim_name}: {dim_val:.2f}mm."
                    )
            if p.width > C.BOARD_MAX_WIDTH or p.height > C.BOARD_MAX_HEIGHT:
                self.warnings.append(
                    f"Panel '{p.label}' ({p.width:.0f}×{p.height:.0f}mm) "
                    f"exceeds board stock. Will need to be cut from multiple boards."
                )


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def solve(spec: FurnitureSpec) -> ResolvedSpec:
    """Shorthand: solve(spec) → ResolvedSpec or raises ConstraintError."""
    return FurnitureSolver(spec).solve()
