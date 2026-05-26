"""
joinery.py — Boolean-cut shapes for confirmat screws and European hinge cups.

All bore shapes are built at the origin with the bore axis along +Z:
  - Z = 0         : entry face (screw-head / cup opening)
  - Z = bore_depth: blind end (inside the material)

Callers rotate the shape to the desired bore axis, then translate to world
position before calling shape.cut(bore).

Confirmat orientation helpers:
  bore_along_pos_x  →  rotate 90° around Y   (Z → +X)
  bore_along_neg_x  →  rotate -90° around Y  (Z → -X)
  bore_along_neg_y  →  rotate 90° around X   (Z → -Y)   ← hinge cups
  bore_along_neg_z  →  rotate 180° around X  (Z → -Z)   ← top/bottom joints
"""

import math

import FreeCAD as App
import Part

import config as C


# ---------------------------------------------------------------------------
# Position helpers
# ---------------------------------------------------------------------------

def confirmat_positions(length: float) -> list:
    """
    Return screw-centre positions (mm from one edge) along an edge of *length*.

    Respects CONFIRMAT_EDGE_OFFSET and CONFIRMAT_MAX_SPACING.
    Returns an empty list when the panel is too short for any screw.
    """
    start = C.CONFIRMAT_EDGE_OFFSET
    end   = length - C.CONFIRMAT_EDGE_OFFSET
    if end < start:
        return []
    span = end - start
    if span < 1e-3:
        return [start]
    n_gaps = max(1, math.ceil(span / C.CONFIRMAT_MAX_SPACING))
    return [start + i * span / n_gaps for i in range(n_gaps + 1)]


# ---------------------------------------------------------------------------
# Bore shapes (at origin, entry face at Z=0, blind end at Z=depth)
# ---------------------------------------------------------------------------

def make_confirmat_bore() -> Part.Shape:
    """
    Confirmat screw bore compound shape, axis along +Z.

    Layout (from entry face inward):
      Z = 0 … HEAD_DEPTH          : head pocket  (CONFIRMAT_HEAD_DIAMETER)
      Z = 0 … CONFIRMAT_HOLE_DEPTH: shaft         (CONFIRMAT_DIAMETER)

    The wider head pocket sits at the entry face (Z=0) so when the bore is
    placed with Z=0 flush with the panel surface, the countersink is correct.
    """
    shaft = Part.makeCylinder(
        C.CONFIRMAT_DIAMETER / 2,
        C.CONFIRMAT_HOLE_DEPTH,
    )
    head = Part.makeCylinder(
        C.CONFIRMAT_HEAD_DIAMETER / 2,
        C.CONFIRMAT_HEAD_DEPTH,
    )
    return shaft.fuse(head)


def make_hinge_cup() -> Part.Shape:
    """
    European cup hinge bore, axis along +Z.
    Flat-bottomed cylinder: radius = HINGE_CUP_DIAMETER/2, depth = HINGE_CUP_DEPTH.
    Entry face at Z=0, blind end at Z=HINGE_CUP_DEPTH.
    """
    return Part.makeCylinder(C.HINGE_CUP_DIAMETER / 2, C.HINGE_CUP_DEPTH)


# ---------------------------------------------------------------------------
# Rotation helpers
# ---------------------------------------------------------------------------

def _rotated(shape: Part.Shape, axis: App.Vector, deg: float) -> Part.Shape:
    s = shape.copy()
    s.rotate(App.Vector(0, 0, 0), axis, deg)
    return s


def _bore_along_pos_x(bore: Part.Shape) -> Part.Shape:
    """Rotate bore so its axis points in +X (entry face at X=0)."""
    return _rotated(bore, App.Vector(0, 1, 0), 90)


def _bore_along_neg_x(bore: Part.Shape) -> Part.Shape:
    """Rotate bore so its axis points in -X (entry face at X=0)."""
    return _rotated(bore, App.Vector(0, 1, 0), -90)


def _bore_along_neg_y(bore: Part.Shape) -> Part.Shape:
    """Rotate bore so its axis points in -Y (entry face at Y=0)."""
    return _rotated(bore, App.Vector(1, 0, 0), 90)


def _bore_along_neg_z(bore: Part.Shape) -> Part.Shape:
    """Rotate bore so its axis points in -Z (entry face at Z=0, blind at Z=-depth)."""
    return _rotated(bore, App.Vector(1, 0, 0), 180)


# ---------------------------------------------------------------------------
# Joint cutters
# ---------------------------------------------------------------------------

def cut_side_to_horizontal(
    side_shape: Part.Shape,
    outer_depth: float,
    entry_x: float,
    bore_dir: str,      # "pos_x" | "neg_x"
    z_centre: float,
) -> Part.Shape:
    """
    Cut confirmat bores into *side_shape* for the joint between a side panel
    (or divider) and a horizontal panel (top / bottom).

    Bores enter from the side panel's outer face at *entry_x* along X,
    travel in *bore_dir* toward the cabinet interior, positioned at *z_centre*.
    Screw row runs along Y (depth axis) at confirmat_positions(outer_depth).
    """
    proto = make_confirmat_bore()
    if bore_dir == "pos_x":
        proto = _bore_along_pos_x(proto)
    else:
        proto = _bore_along_neg_x(proto)

    result = side_shape
    for y in confirmat_positions(outer_depth):
        bore = proto.copy()
        bore.translate(App.Vector(entry_x, y, z_centre))
        result = result.cut(bore)
    return result


def cut_top_to_vertical(
    top_shape: Part.Shape,
    outer_depth: float,
    entry_z: float,
    x_centre: float,
) -> Part.Shape:
    """
    Cut confirmat bores into *top_shape* (top or bottom panel) for the joint
    with a divider.  Bores enter from the panel's face at *entry_z*, travel
    in -Z, centred at *x_centre* along X.
    Row runs along Y at confirmat_positions(outer_depth).
    """
    proto  = _bore_along_neg_z(make_confirmat_bore())
    result = top_shape
    for y in confirmat_positions(outer_depth):
        bore = proto.copy()
        bore.translate(App.Vector(x_centre, y, entry_z))
        result = result.cut(bore)
    return result


def cut_hinge_cups(
    door_shape: Part.Shape,
    hinges: list,
    door_pos_x: float,
    door_pos_y: float,
    door_pos_z: float,
) -> Part.Shape:
    """
    Cut European hinge cup bores into *door_shape*.

    Cups bore from the door's back face (Y = door_pos_y + door_depth = 0,
    since doors sit at pos_y = -thickness with depth = thickness) in the -Y
    direction, toward the viewer.

    cup_x in each ResolvedHinge is relative to the door's left edge (pos_x).
    cup_z is relative to the door's bottom edge (pos_z).
    """
    proto  = _bore_along_neg_y(make_hinge_cup())
    result = door_shape
    # Door back face in world coords: Y = door_pos_y + door_depth = 0 (always for doors)
    back_y = door_pos_y + C.THICKNESS

    for h in hinges:
        bore = proto.copy()
        abs_x = door_pos_x + h.cup_x
        abs_z = door_pos_z + h.cup_z
        bore.translate(App.Vector(abs_x, back_y, abs_z))
        result = result.cut(bore)
    return result
