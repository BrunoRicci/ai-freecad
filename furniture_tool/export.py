"""
export.py — Output generators: DXF panel drawings, SVG cut sheet, BOM CSV.

All three functions take a ResolvedSpec and an output directory path.
No FreeCAD session required — operates purely on the resolved data.
The DXF writer targets R14 (2D, flat projection of each panel face).
"""

import csv
import math
import os
from pathlib import Path

import config as C


# ---------------------------------------------------------------------------
# DXF (R14) — one file per panel, flat 2D face projection
# ---------------------------------------------------------------------------

def export_dxf(resolved, output_dir: str) -> list:
    """
    Write one DXF R14 file per panel in *resolved* to *output_dir*.
    Each file shows the panel's largest face (width × height) with:
      - outer rectangle (LWPOLYLINE, layer "OUTLINE")
      - grain direction annotation (LINE, layer "GRAIN")

    Returns a list of written file paths.
    """
    out   = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = []

    for p in resolved.panels:
        fname = out / f"{p.label}.dxf"
        _write_panel_dxf(fname, p)
        paths.append(str(fname))

    return paths


def _write_panel_dxf(path: Path, panel):
    w = panel.width     # X extent of face shown
    h = panel.height    # Z extent

    lines = [
        "0", "SECTION", "2", "HEADER",
        "9", "$ACADVER", "1", "AC1014",
        "9", "$INSUNITS", "70", "4",   # 4 = millimetres
        "0", "ENDSEC",
        "0", "SECTION", "2", "ENTITIES",
    ]

    # Outer rectangle (closed LWPOLYLINE)
    lines += _lwpolyline(
        [(0, 0), (w, 0), (w, h), (0, h)],
        layer="OUTLINE", closed=True,
    )

    # Grain direction: single line down the centre
    if panel.grain_dir == "vertical":
        lines += _line(w / 2, 0, w / 2, h, layer="GRAIN")
    else:
        lines += _line(0, h / 2, w, h / 2, layer="GRAIN")

    # Dimension text centred on face
    lines += _text(
        f"{w:.0f} x {h:.0f}",
        x=w / 2, y=h / 2,
        height=min(w, h) * 0.06,
        layer="DIMS",
    )

    lines += ["0", "ENDSEC", "0", "EOF"]
    path.write_text("\n".join(lines))


def _lwpolyline(points, layer="0", closed=False):
    flag = 1 if closed else 0
    out  = [
        "0", "LWPOLYLINE",
        "8", layer,
        "90", str(len(points)),
        "70", str(flag),
    ]
    for x, y in points:
        out += ["10", f"{x:.4f}", "20", f"{y:.4f}"]
    return out


def _line(x1, y1, x2, y2, layer="0"):
    return [
        "0", "LINE",
        "8", layer,
        "10", f"{x1:.4f}", "20", f"{y1:.4f}", "30", "0.0",
        "11", f"{x2:.4f}", "21", f"{y2:.4f}", "31", "0.0",
    ]


def _text(text, x, y, height=5.0, layer="0"):
    return [
        "0", "TEXT",
        "8", layer,
        "10", f"{x:.4f}", "20", f"{y:.4f}", "30", "0.0",
        "40", f"{height:.4f}",
        "1", text,
        "72", "1",   # horizontal centre
        "11", f"{x:.4f}", "21", f"{y:.4f}", "31", "0.0",
    ]


# ---------------------------------------------------------------------------
# SVG cut sheet — all panels nested onto 2750×1830mm board pages
# ---------------------------------------------------------------------------

# Simple strip-packing: sort panels by height descending, fill rows left→right.

def export_svg(resolved, output_dir: str) -> list:
    """
    Pack all panels onto standard board sheets and write one SVG per sheet.
    Returns a list of written file paths.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    panels   = list(resolved.panels)
    sheets   = _pack_sheets(panels, C.BOARD_MAX_WIDTH, C.BOARD_MAX_HEIGHT)
    paths    = []
    scale    = 0.25   # px per mm — keeps SVG viewport manageable

    for i, sheet in enumerate(sheets):
        fname = out / f"cutsheet_{i+1:02d}.svg"
        _write_sheet_svg(fname, sheet, C.BOARD_MAX_WIDTH, C.BOARD_MAX_HEIGHT, scale)
        paths.append(str(fname))

    return paths


def _pack_sheets(panels, board_w, board_h):
    """
    Greedy strip packer.  Returns list-of-lists; each inner list is
    [(panel, placed_x, placed_y), ...] for one board sheet.
    """
    # Sort largest first (by area)
    remaining = sorted(panels, key=lambda p: p.width * p.height, reverse=True)
    sheets    = []

    while remaining:
        sheet    = []
        cur_x    = 0.0
        cur_y    = 0.0
        row_h    = 0.0
        leftover = []

        for p in remaining:
            pw, ph = p.width, p.height
            # Try rotating if it fits better (horizontal grain panels)
            if ph > pw and pw <= board_h and ph <= board_w:
                pw, ph = ph, pw   # rotate 90°

            if pw > board_w or ph > board_h:
                leftover.append(p)   # panel too big for any sheet
                continue

            if cur_x + pw > board_w:   # next row
                cur_x = 0.0
                cur_y += row_h + 2     # 2mm gap between rows
                row_h = 0.0

            if cur_y + ph > board_h:   # doesn't fit on this sheet
                leftover.append(p)
                continue

            sheet.append((p, cur_x, cur_y, pw, ph))
            cur_x += pw + 2            # 2mm gap between panels
            row_h  = max(row_h, ph)

        sheets.append(sheet)
        remaining = leftover
        if not sheet:
            break   # nothing fit (all panels too large) — stop to avoid infinite loop

    return sheets


def _write_sheet_svg(path: Path, sheet, board_w, board_h, scale):
    W = board_w * scale
    H = board_h * scale

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{W:.1f}" height="{H:.1f}" '
        f'viewBox="0 0 {W:.1f} {H:.1f}">',
        f'<rect width="{W:.1f}" height="{H:.1f}" '
        f'fill="#f5f0e8" stroke="#ccc" stroke-width="1"/>',
    ]

    for p, px, py, pw, ph in sheet:
        sx, sy = px * scale, py * scale
        sw, sh = pw * scale, ph * scale
        label  = p.label.replace("_", " ")
        dims   = f"{pw:.0f}×{ph:.0f}"
        fs     = max(5, min(sw, sh) * 0.12)

        svg.append(
            f'<rect x="{sx:.2f}" y="{sy:.2f}" width="{sw:.2f}" height="{sh:.2f}" '
            f'fill="#e8dcc8" stroke="#6b4e1a" stroke-width="0.8"/>'
        )
        # Label
        svg.append(
            f'<text x="{sx + sw/2:.2f}" y="{sy + sh/2 - fs*0.6:.2f}" '
            f'font-size="{fs:.1f}" text-anchor="middle" fill="#3a2510">'
            f'{label}</text>'
        )
        # Dimensions
        svg.append(
            f'<text x="{sx + sw/2:.2f}" y="{sy + sh/2 + fs*0.8:.2f}" '
            f'font-size="{fs*0.8:.1f}" text-anchor="middle" fill="#6b4e1a">'
            f'{dims}</text>'
        )

    svg.append('</svg>')
    path.write_text("\n".join(svg))


# ---------------------------------------------------------------------------
# BOM — bill of materials as CSV
# ---------------------------------------------------------------------------

def export_bom(resolved, output_dir: str) -> str:
    """
    Write a CSV bill of materials to *output_dir*/bom.csv.

    Columns: Label, Role, Width_mm, Height_mm, Depth_mm, Qty, Material, Grain
    Panels with identical dimensions and role are collapsed into a single row
    with Qty > 1.

    Returns the path to the written file.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    csv_path = out / "bom.csv"

    # Deduplicate
    seen  = {}
    order = []
    for p in resolved.panels:
        key = (p.role, round(p.width, 1), round(p.height, 1), round(p.depth, 1))
        if key in seen:
            seen[key]["qty"] += 1
        else:
            row = dict(
                label    = p.label,
                role     = p.role,
                width    = p.width,
                height   = p.height,
                depth    = p.depth,
                qty      = 1,
                material = _material(p.role),
                grain    = p.grain_dir,
            )
            seen[key] = row
            order.append(key)

    # Hardware rows
    hardware = _hardware_rows(resolved)

    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["label", "role", "width", "height", "depth",
                        "qty", "material", "grain"],
        )
        writer.writeheader()
        for key in order:
            writer.writerow(seen[key])
        for row in hardware:
            writer.writerow(row)

    return str(csv_path)


def _material(role: str) -> str:
    if role in ("back", "drawer_bottom"):
        return f"HDF {C.BACK_THICKNESS}mm"
    return f"Melamine {C.THICKNESS}mm"


def _hardware_rows(resolved) -> list:
    """Generate BOM rows for hinges, slides, and handles."""
    rows = []

    if resolved.hinges:
        rows.append(dict(
            label="Hinge (European cup 35mm)",
            role="hardware",
            width=C.HINGE_CUP_DIAMETER,
            height="",
            depth="",
            qty=len(resolved.hinges),
            material="Metal",
            grain="",
        ))

    if resolved.slides:
        rows.append(dict(
            label=f"Drawer slide {resolved.slides[0].length:.0f}mm",
            role="hardware",
            width="",
            height=C.SLIDE_HEIGHT,
            depth=resolved.slides[0].length,
            qty=len(resolved.slides),
            material="Metal",
            grain="",
        ))

    # Count door + drawer_front panels for handle estimate
    handle_panels = [p for p in resolved.panels
                     if p.role in ("door", "drawer_front")]
    if handle_panels:
        rows.append(dict(
            label=f"Handle ({C.HANDLE_HOLE_SPACING:.0f}mm centres)",
            role="hardware",
            width="",
            height="",
            depth="",
            qty=len(handle_panels),
            material="Metal",
            grain="",
        ))

    return rows
