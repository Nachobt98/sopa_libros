"""KDP page layout configuration."""

# KDP trim size: 6x9 inches at 300 DPI.
TRIM_W_IN = 6.0
TRIM_H_IN = 9.0
DPI = 300
PAGE_W_PX = int(TRIM_W_IN * DPI)
PAGE_H_PX = int(TRIM_H_IN * DPI)

# Safe margins.
gutter_in = 0.375
outside_in = 0.25
top_in = 0.25
bottom_in = 0.25

gutter_px = int(gutter_in * DPI)
outside_px = int(outside_in * DPI)
top_px = int(top_in * DPI)
bottom_px = int(bottom_in * DPI)

SAFE_LEFT = gutter_px + 50
SAFE_RIGHT = PAGE_W_PX - outside_px - 50
SAFE_TOP = top_px + 120
SAFE_BOTTOM = PAGE_H_PX - bottom_px - 220

TOP_PX = top_px
BOTTOM_PX = bottom_px
