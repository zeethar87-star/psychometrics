# Layer Standard (AIA-like)

| Layer | Meaning | Color | Example |
|---|---|---|---|
| A-WALL | Walls | 1 (red) | `LINE` segments of wall centerline |
| A-DOOR | Doors | 3 (green) | door swing arcs |
| A-WIND | Windows | 4 (cyan) | window boundary lines |
| A-GRID | Structural grid | 8 (gray) | grid reference lines |
| A-ANNO | Annotation | 7 (white) | text and dimensions |

MVP currently emits `A-WALL` only.
