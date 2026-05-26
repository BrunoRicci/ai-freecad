"""
hardware.py — Drawer slide and handle positioning.

Returns placement data dicts — no FreeCAD geometry is created here so that
the data can also be consumed by export.py (BOM, drilling files) without a
FreeCAD session.

All positions are in world coordinates matching the solver output.
"""

import config as C


# ---------------------------------------------------------------------------
# Drawer slides
# ---------------------------------------------------------------------------

def slide_placements(slide) -> list:
    """
    Return a list of one dict per slide rail (always two: left + right).

    Each dict:
        side     : "left" | "right"
        pos_x    : world X of the slide's inner face
        pos_y    : world Y of the slide front edge (flush with carcass front)
        pos_z    : world Z of the slide bottom
        length   : slide body length (= drawer box depth)
        height   : SLIDE_HEIGHT (from config)
        thickness: SLIDE_THICKNESS (from config)
    """
    # slide.pos_x is already the X of the slide inner face (set by solver)
    return [
        dict(
            side      = slide.side,
            pos_x     = slide.pos_x,
            pos_y     = C.SLIDE_SETBACK_FRONT,
            pos_z     = slide.pos_z,
            length    = slide.length,
            height    = C.SLIDE_HEIGHT,
            thickness = C.SLIDE_THICKNESS,
        )
    ]


# ---------------------------------------------------------------------------
# Handles
# ---------------------------------------------------------------------------

def handle_hole_positions(panel) -> list:
    """
    Return a list of two (x, z) tuples for the handle fixing holes on *panel*.

    Works for both door and drawer_front roles.

    Door  : holes are HANDLE_OFFSET_FROM_EDGE from the latch side (opposite
            to hinge side).  Latch side is deduced from pos_x: if the panel
            is in the left half of the cabinet we assume it's right-latched,
            otherwise left-latched.  Centred in height.
    Drawer: holes centred horizontally and vertically.
    """
    cx = panel.pos_x + panel.width  / 2   # horizontal centre of panel
    cz = panel.pos_z + panel.height / 2   # vertical centre of panel
    half = C.HANDLE_HOLE_SPACING / 2

    if panel.role == "door":
        # Holes stacked vertically, centred in panel height,
        # offset from the latch (non-hinge) edge horizontally.
        # We place them HANDLE_OFFSET_FROM_EDGE from the right edge by default.
        offset_x = panel.pos_x + panel.width - C.HANDLE_OFFSET_FROM_EDGE
        return [
            (offset_x, cz - half),
            (offset_x, cz + half),
        ]

    # drawer_front: holes centred horizontally, stacked horizontally
    return [
        (cx - half, cz),
        (cx + half, cz),
    ]


def handle_drill_data(panel) -> dict:
    """
    Return a dict describing the handle drilling for *panel*.

    Keys:
        holes      : list of (x, z) world-coord hole centres
        diameter   : HANDLE_HOLE_DIAMETER
        depth      : panel depth (through-hole)
    """
    return dict(
        holes    = handle_hole_positions(panel),
        diameter = C.HANDLE_HOLE_DIAMETER,
        depth    = panel.depth,
    )
