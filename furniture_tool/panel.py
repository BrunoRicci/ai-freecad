"""
panel.py — FreeCAD part builder for individual panels.

Turns a ResolvedPanel into a Part::Feature (box) inside a FreeCAD document,
sets placement, display colour, and label.

FreeCAD/solver coordinate system:
    X = cabinet width axis
    Y = cabinet depth axis (front = 0, back = positive Y)
    Z = cabinet height axis (bottom = 0, top = positive Z)
"""

import FreeCAD as App
import Part

import config as C


ROLE_COLOR = {
    "side_left":    C.COLOR_CARCASS,
    "side_right":   C.COLOR_CARCASS,
    "top":          C.COLOR_CARCASS,
    "bottom":       C.COLOR_CARCASS,
    "divider":      C.COLOR_CARCASS,
    "shelf":        C.COLOR_CARCASS,
    "back":         C.COLOR_BACK,
    "door":         C.COLOR_DOOR,
    "drawer_front": C.COLOR_DRAWER,
    "drawer_side":  C.COLOR_DRAWER,
    "drawer_back":  C.COLOR_DRAWER,
    "drawer_bottom":C.COLOR_BACK,
}


def build_panel(doc, panel, group=None):
    """
    Create a Part::Feature box for *panel* in *doc*.
    Returns the FreeCAD feature object.

    Part.makeBox(length, width, height, pnt) maps to (X, Y, Z, origin)
    which matches the solver's width/depth/height convention directly.

    Optionally inserts the feature into *group* (DocumentObjectGroup).
    """
    shape = Part.makeBox(
        panel.width,
        panel.depth,
        panel.height,
        App.Vector(panel.pos_x, panel.pos_y, panel.pos_z),
    )

    feat       = doc.addObject("Part::Feature", panel.label)
    feat.Shape = shape
    feat.Label = panel.label

    vo = getattr(feat, "ViewObject", None)
    if vo is not None:
        vo.ShapeColor   = ROLE_COLOR.get(panel.role, C.COLOR_CARCASS)
        vo.Transparency = C.TRANSPARENCY

    if group is not None:
        group.addObject(feat)

    return feat
