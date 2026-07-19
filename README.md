# ai-freecad

Python-based parametric geometry scripting with FreeCAD running fully headless inside a GitHub Codespace.
No GUI, no display server, no manual setup — open in Codespaces and start writing geometry code immediately.

The goal is to generate 3D geometry programmatically (STEP / STL / FreeCAD `.FCStd` files) and eventually
render the output in-browser via a Three.js viewer.

---

## Getting Started

### Open in GitHub Codespaces

1. Click **Code → Codespaces → Create codespace on main** on the GitHub repo page.
2. Wait for the container to build (~3–5 minutes the first time — FreeCAD AppImage is downloaded and extracted).
3. When the terminal prompt appears, FreeCAD is ready. No further setup needed.

The `postCreateCommand` in `.devcontainer/devcontainer.json` runs `.devcontainer/setup.sh` automatically.
It downloads the latest FreeCAD Linux AppImage, extracts it, and wires `import FreeCAD` into the system
Python path via a `.pth` file.

### Verify the setup

```bash
python3 -c "import FreeCAD; print(FreeCAD.Version())"
```

---

## Running the Demo Scripts

### hello_geometry.py

Creates a Box (20×10×5 mm) and a Cylinder (r=4, h=15 mm), reports their volumes,
and exports them to `output/`.

```bash
python3 scripts/hello_geometry.py
```

Output files:
- `output/box.step`
- `output/cylinder.stl`

### export_example.py — parametric L-bracket

Generates an L-shaped bracket using a boolean cut operation.
Accepts optional `width` and `height` arguments (in mm).

```bash
# defaults: width=10, height=20
python3 scripts/export_example.py

# custom dimensions
python3 scripts/export_example.py 15 30
python3 scripts/export_example.py --width 25 --height 50
```

Output files:
- `output/bracket.step`
- `output/bracket.stl`

---

## Writing Your Own Scripts

```python
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")   # suppress Qt warnings

import FreeCAD as App
import Part

doc = App.newDocument("MyDoc")

# Parametric objects (recomputed by the document)
box = doc.addObject("Part::Box", "MyBox")
box.Length = 50.0
box.Width  = 30.0
box.Height = 10.0
doc.recompute()

# Raw shape operations (no document needed)
sphere = Part.makeSphere(15.0)
result = box.Shape.fuse(sphere)

result.exportStep("output/my_shape.step")
```

### Key modules

| Module | Purpose |
|--------|---------|
| `FreeCAD` / `App` | Document model, vectors, placements |
| `Part` | BREP solids, boolean ops, STEP export |
| `Mesh` | STL mesh generation and export |

> **Do not import `FreeCADGui`** — there is no display in a Codespace.
> All geometry operations work through `FreeCAD`, `Part`, and `Mesh` alone.

---

## Headless Notes

- FreeCAD runs with no display required. `QT_QPA_PLATFORM=offscreen` is set automatically.
- The FreeCAD Python libs come from the extracted AppImage at `~/.FreeCAD/squashfs-root/usr/lib/`.
- `FreeCADCmd` (the headless CLI for `.FCMacro` files) is available at:
  ```
  ~/.FreeCAD/squashfs-root/usr/bin/FreeCADCmd
  ```
  Example:
  ```bash
  ~/.FreeCAD/squashfs-root/usr/bin/FreeCADCmd scripts/mymacro.FCMacro
  ```

---

## Local AI (Ollama + Qwen)

The Codespace also installs [Ollama](https://ollama.com) and pulls a local
Qwen model automatically (see `.devcontainer/setup.sh`), so future
AI-driven geometry generation can run against a local model with no
external API keys. See [`ollama/README.md`](ollama/README.md) for
configuration and usage.

---

## Roadmap

- [ ] Three.js in-browser viewer for STL / STEP output
- [ ] GitHub Actions workflow to render geometry on push
- [ ] More parametric examples (gears, enclosures, brackets)
