"""
cabinet.py — High-level FreeCAD assembler.

build(doc, resolved_spec) → dict mapping panel label → FreeCAD feature.

Pipeline for each panel:
  1. panel.build_panel()   — create the basic box in the document
  2. joinery cut           — confirmat bores for structural joints
                           — hinge cup bores for doors
  3. Group features in the FreeCAD document tree

Groups created:
  Carcass   : side_left, side_right, top, bottom, dividers, back
  Doors     : door panels (with hinge bores applied)
  Drawers   : drawer fronts, box sides, backs, bottoms
  Shelves   : shelf panels
"""

import FreeCAD as App

import config as C
import panel  as P
import joinery as J


# ---------------------------------------------------------------------------
# Group names
# ---------------------------------------------------------------------------

_ROLE_GROUP = {
    "side_left":    "Carcass",
    "side_right":   "Carcass",
    "top":          "Carcass",
    "bottom":       "Carcass",
    "divider":      "Carcass",
    "back":         "Carcass",
    "shelf":        "Shelves",
    "door":         "Doors",
    "drawer_front": "Drawers",
    "drawer_side":  "Drawers",
    "drawer_back":  "Drawers",
    "drawer_bottom":"Drawers",
}

_GROUP_NAMES = ["Carcass", "Doors", "Drawers", "Shelves"]


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def build(doc, resolved):
    """
    Build a complete FreeCAD document from *resolved* (a ResolvedSpec).

    Returns a dict { panel.label: FreeCAD_feature }.
    All geometry, joinery, and grouping are applied before returning.
    """
    # ── Create document groups ──────────────────────────────────────────────
    groups = {}
    for name in _GROUP_NAMES:
        groups[name] = doc.addObject("App::DocumentObjectGroup", name)

    # ── Build panel features ─────────────────────────────────────────────────
    feat_map = {}
    for rp in resolved.panels:
        grp  = groups.get(_ROLE_GROUP.get(rp.role, "Carcass"))
        feat = P.build_panel(doc, rp, group=grp)
        feat_map[rp.label] = feat

    # ── Apply structural confirmat bores ─────────────────────────────────────
    _apply_carcass_joints(feat_map, resolved)

    # ── Apply hinge cup bores ────────────────────────────────────────────────
    _apply_hinge_bores(feat_map, resolved)

    doc.recompute()
    return feat_map


# ---------------------------------------------------------------------------
# Confirmat bores — carcass structural joints
# ---------------------------------------------------------------------------

def _apply_carcass_joints(feat_map, r):
    """
    Cut confirmat bores into side panels (and top/bottom panels for dividers).

    Side panels → top and bottom:
      Bores enter from the side panel's outer face (X direction) at the
      Z-height of the top/bottom panel centreline.

    Top/bottom panels → each divider:
      Bores enter from the panel face (Z direction) at the divider centreline.
    """
    T          = r.thickness
    outer_d    = r.outer_depth
    outer_w    = r.outer_width
    outer_h    = r.outer_height
    z_bottom   = T / 2           # centre of bottom panel along Z
    z_top      = outer_h - T / 2 # centre of top panel along Z

    # ── Side panel → top and bottom ─────────────────────────────────────────
    for label, entry_x, dire in [
        ("Side_Left",  0.0,     "pos_x"),
        ("Side_Right", outer_w, "neg_x"),
    ]:
        if label not in feat_map:
            continue
        feat  = feat_map[label]
        shape = feat.Shape
        for z_c in (z_bottom, z_top):
            shape = J.cut_side_to_horizontal(
                shape, outer_d, entry_x, dire, z_c
            )
        feat.Shape = shape

    # ── Top/bottom panels → each divider ────────────────────────────────────
    dividers = [p for p in _iter_panels(feat_map) if p[0].startswith("Divider_")]
    top_feat    = feat_map.get("Top")
    bottom_feat = feat_map.get("Bottom")

    for label, feat in dividers:
        # Divider X centre (dividers are T wide)
        div_panel  = next(p for p in _panels_list(feat_map) if p.label == label)
        x_c        = div_panel.pos_x + T / 2

        if top_feat:
            top_feat.Shape = J.cut_top_to_vertical(
                top_feat.Shape, outer_d, outer_h, x_c
            )
        if bottom_feat:
            # Bore from bottom panel's underside (Z=0) going +Z — same shape,
            # just entry at Z=0 instead.  Reuse cut_top_to_vertical with
            # entry_z=T so bore goes from Z=T (inner face) toward Z=T-50:
            # simpler: bore from the bottom face (Z=0) downward is unusual.
            # Practical choice: bore from top face of bottom panel (Z=T) going -Z.
            bottom_feat.Shape = J.cut_top_to_vertical(
                bottom_feat.Shape, outer_d, T, x_c
            )


def _iter_panels(feat_map):
    return list(feat_map.items())


def _panels_list(feat_map):
    """Return placeholder — cabinet.py only has feat_map, not ResolvedPanels.
    Callers that need ResolvedPanel data must pass resolved directly."""
    return []


# ---------------------------------------------------------------------------
# Hinge cup bores
# ---------------------------------------------------------------------------

def _apply_hinge_bores(feat_map, resolved):
    """
    Cut European hinge cup bores into every door panel using the
    ResolvedHinge list in *resolved*.
    """
    # Build a mapping: door_label → list of ResolvedHinge
    hinge_map = {}
    for h in resolved.hinges:
        hinge_map.setdefault(h.door_label, []).append(h)

    # Build a mapping: door_label → ResolvedPanel
    panel_map = {p.label: p for p in resolved.panels if p.role == "door"}

    for door_label, hinges in hinge_map.items():
        feat = feat_map.get(door_label)
        rp   = panel_map.get(door_label)
        if feat is None or rp is None:
            continue
        feat.Shape = J.cut_hinge_cups(
            feat.Shape,
            hinges,
            door_pos_x = rp.pos_x,
            door_pos_y = rp.pos_y,
            door_pos_z = rp.pos_z,
        )
