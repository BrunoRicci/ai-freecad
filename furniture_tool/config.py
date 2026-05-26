"""
config.py — Single source of truth for all furniture variables.

All dimensions in millimetres.
Edit this file to change defaults; everything else derives from these values.
No hardcoded numbers anywhere else in the codebase.
"""

# ---------------------------------------------------------------------------
# MATERIAL
# ---------------------------------------------------------------------------

THICKNESS           = 18       # Melamine board thickness (mm). Default 18mm.
BACK_THICKNESS      = 8        # Back panel (thinner board or HDF). mm.

# ---------------------------------------------------------------------------
# BOARD STOCK — maximum raw board dimensions from supplier.
# Used by the solver to flag panels that exceed a single board.
# ---------------------------------------------------------------------------

BOARD_MAX_WIDTH     = 2750     # mm  (common melamine sheet width)
BOARD_MAX_HEIGHT    = 1830     # mm  (common melamine sheet height)

# ---------------------------------------------------------------------------
# STRUCTURAL CLEARANCES & TOLERANCES
# ---------------------------------------------------------------------------

GAP_DOOR            = 2.0      # Gap between door edge and carcass (each side). mm.
GAP_DRAWER_SIDE     = 12.5     # Gap each side for drawer slide hardware. mm.
GAP_DRAWER_TOP      = 3.0      # Gap above drawer front. mm.
GAP_DRAWER_BOTTOM   = 3.0      # Gap below drawer front (above floor or lower drawer). mm.
GAP_SHELF           = 0.5      # Shelf-to-panel side gap (shelf slides in). mm.
GAP_BACK_RABBET     = 8.0      # Depth of rabbet that receives the back panel. mm.

TOLERANCE_SAW       = 0.5      # CNC/saw kerf tolerance added to cut dims. mm.
TOLERANCE_ASSEMBLY  = 0.2      # Assembly fit tolerance (drill/bore). mm.

# ---------------------------------------------------------------------------
# JOINERY — Confirmat screws
# ---------------------------------------------------------------------------

CONFIRMAT_DIAMETER      = 7.0      # Confirmat screw shaft diameter. mm.
CONFIRMAT_HEAD_DIAMETER = 10.0     # Confirmat head (countersink) diameter. mm.
CONFIRMAT_HEAD_DEPTH    = 7.0      # Depth of countersink pocket. mm.
CONFIRMAT_HOLE_DEPTH    = 50.0     # Total bore depth into receiving panel. mm.
CONFIRMAT_EDGE_OFFSET   = 37.0     # Distance from panel edge to screw centre. mm.
CONFIRMAT_MIN_SPACING   = 150.0    # Minimum spacing between two confirmats. mm.
CONFIRMAT_MAX_SPACING   = 400.0    # Maximum spacing between two confirmats. mm.

# ---------------------------------------------------------------------------
# HARDWARE — Drawer slides (side-mount, soft-close, ball bearing)
# ---------------------------------------------------------------------------

SLIDE_HEIGHT            = 45.0    # Height of slide body. mm.
SLIDE_THICKNESS         = 13.0    # Total thickness per side (slide + clearance). mm.
SLIDE_SETBACK_FRONT     = 0.0     # Slide flush with front face of carcass. mm.
SLIDE_SETBACK_REAR      = 0.0     # Slide flush with rear face of carcass. mm.
SLIDE_VERTICAL_OFFSET   = 0.0     # Bottom of slide above drawer floor. mm.

# Drawer box is inset from carcass opening:
#   opening_width - 2 * GAP_DRAWER_SIDE = drawer_box_width
#   opening_height - GAP_DRAWER_TOP - GAP_DRAWER_BOTTOM = drawer_box_height

# ---------------------------------------------------------------------------
# HARDWARE — European cup hinges (35mm boring)
# ---------------------------------------------------------------------------

HINGE_CUP_DIAMETER      = 35.0    # Standard cup bore. mm.
HINGE_CUP_DEPTH         = 13.5    # Depth of cup bore into door. mm.
HINGE_BACKSET           = 37.0    # Distance from door edge to cup centre. mm.
HINGE_FROM_TOP          = 100.0   # Distance from door top to first hinge centre. mm.
HINGE_FROM_BOTTOM       = 100.0   # Distance from door bottom to last hinge centre. mm.
HINGE_MAX_SPAN          = 1200.0  # If door taller than this, add a third hinge. mm.

# ---------------------------------------------------------------------------
# HARDWARE — Surface-mounted handles
# ---------------------------------------------------------------------------

HANDLE_HOLE_SPACING     = 128.0   # Centre-to-centre between fixing holes. mm. (std: 96, 128, 160)
HANDLE_HOLE_DIAMETER    = 5.0     # Through-hole diameter. mm.
HANDLE_OFFSET_FROM_EDGE = 45.0    # Distance from door/drawer edge to handle centre. mm.

# ---------------------------------------------------------------------------
# VISUAL / FREECAD DISPLAY
# ---------------------------------------------------------------------------

COLOR_CARCASS   = (0.82, 0.71, 0.55)   # Warm wood tone  (R, G, B) 0–1
COLOR_DOOR      = (0.75, 0.65, 0.50)   # Slightly darker
COLOR_DRAWER    = (0.78, 0.68, 0.52)
COLOR_BACK      = (0.88, 0.80, 0.65)   # Lighter (HDF/back board)
COLOR_HARDWARE  = (0.55, 0.55, 0.60)   # Metallic grey

TRANSPARENCY    = 0                     # 0 = fully opaque, 100 = invisible
