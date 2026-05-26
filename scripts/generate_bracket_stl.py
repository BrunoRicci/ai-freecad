"""
generate_bracket_stl.py — pure-Python L-bracket STL generator (no FreeCAD required).

Produces the same geometry as export_example.py but uses only stdlib.

Usage:
    python3 scripts/generate_bracket_stl.py
    python3 scripts/generate_bracket_stl.py 15 30
"""

import argparse
import math
import os
import struct

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")


def normal(v0, v1, v2):
    ax, ay, az = v1[0]-v0[0], v1[1]-v0[1], v1[2]-v0[2]
    bx, by, bz = v2[0]-v0[0], v2[1]-v0[1], v2[2]-v0[2]
    nx = ay*bz - az*by
    ny = az*bx - ax*bz
    nz = ax*by - ay*bx
    length = math.sqrt(nx*nx + ny*ny + nz*nz) or 1.0
    return (nx/length, ny/length, nz/length)


def quad_tris(p0, p1, p2, p3):
    """Split quad (p0,p1,p2,p3) into two triangles with computed normals."""
    n1 = normal(p0, p1, p2)
    n2 = normal(p0, p2, p3)
    return [(n1, p0, p1, p2), (n2, p0, p2, p3)]


def write_binary_stl(triangles, path):
    header = b"L-bracket (ai-freecad pure-python)".ljust(80, b"\x00")
    with open(path, "wb") as f:
        f.write(header)
        f.write(struct.pack("<I", len(triangles)))
        for n, v0, v1, v2 in triangles:
            f.write(struct.pack("<3f", *n))
            f.write(struct.pack("<3f", *v0))
            f.write(struct.pack("<3f", *v1))
            f.write(struct.pack("<3f", *v2))
            f.write(struct.pack("<H", 0))


def make_bracket_triangles(width: float, height: float):
    """
    L-bracket geometry matching export_example.py:
      outer box (W x D x H) minus a notch in the top-right corner.
    Depth D = W/2, wall thickness T = 0.25 * min(W, H).
    """
    W = width
    H = height
    D = W / 2
    T = min(W, H) * 0.25

    tris = []

    # ── Rectangular faces ─────────────────────────────────────────────────────

    # Bottom  (Z=0)  normal (0,0,-1)
    tris += quad_tris((W,0,0),(0,0,0),(0,D,0),(W,D,0))

    # Right lower leg (X=W, Z: 0→T)  normal (+1,0,0)
    tris += quad_tris((W,0,0),(W,D,0),(W,D,T),(W,0,T))

    # Inner step horizontal (Z=T, X: T→W)  normal (0,0,+1)
    tris += quad_tris((T,0,T),(W,0,T),(W,D,T),(T,D,T))

    # Inner step vertical (X=T, Z: T→H)  normal (-1,0,0)
    tris += quad_tris((T,0,H),(T,0,T),(T,D,T),(T,D,H))

    # Top vertical leg (Z=H, X: 0→T)  normal (0,0,+1)
    tris += quad_tris((0,0,H),(T,0,H),(T,D,H),(0,D,H))

    # Left (X=0, Z: 0→H)  normal (-1,0,0)
    tris += quad_tris((0,0,0),(0,0,H),(0,D,H),(0,D,0))

    # ── L-shaped front and back faces ─────────────────────────────────────────
    # Cross-section vertices (X, Z): P0..P5 going around the L
    # P0(0,0) P1(W,0) P2(W,T) P3(T,T) P4(T,H) P5(0,H)

    for y, sign in ((0.0, -1), (D, +1)):
        pts = [
            (0, y, 0),
            (W, y, 0),
            (W, y, T),
            (T, y, T),
            (T, y, H),
            (0, y, H),
        ]
        # Fan from pts[0]; reverse vertex order for back face to flip winding
        pairs = [(pts[1], pts[2]), (pts[2], pts[3]), (pts[3], pts[4]), (pts[4], pts[5])]
        for a, b in pairs:
            if sign == -1:
                v0, v1, v2 = pts[0], a, b
            else:
                v0, v1, v2 = pts[0], b, a
            n = normal(v0, v1, v2)
            tris.append((n, v0, v1, v2))

    return tris


def main():
    p = argparse.ArgumentParser()
    p.add_argument("width",  nargs="?", type=float, default=10.0)
    p.add_argument("height", nargs="?", type=float, default=20.0)
    args = p.parse_args()

    W, H = args.width, args.height
    print(f"Generating L-bracket (pure-python): width={W} mm, height={H} mm")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tris = make_bracket_triangles(W, H)

    path = os.path.join(OUTPUT_DIR, "bracket.stl")
    write_binary_stl(tris, path)
    print(f"  Wrote {len(tris)} triangles → {path}")
    print("Done.")


if __name__ == "__main__":
    main()
