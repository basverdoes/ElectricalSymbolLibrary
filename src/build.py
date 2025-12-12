import pathlib
import yaml
import numpy as np
from svglib.svglib import svg2rlg
from reportlab.graphics import shapes
from reportlab.graphics import renderSVG
from reportlab.lib import colors
from reportlab.graphics.charts.textlabels import Label

"""
CONSTANTS
"""

debug = False

canvas_size_h = 400 # px
canvas_size_v = 300
canvas_margin = 10

ann_size_h = 60
sym_space  = 2

"""
HELPERS
"""

def add_debug_cursor(arr, color=colors.red):
    if debug:
        g = shapes.Group()
        l1 = shapes.Line(-2, 0, 2, 0, strokeColor=color)
        l2 = shapes.Line( 0, -2, 0, 2, strokeColor=color)
        g.add(l1)
        g.add(l2)
        g.translate(arr[0], arr[1])
        d.add(g)

"""
SCRIPT
"""

# Read config
with open('./config/grid.yml', 'r', encoding='utf8') as f:
    grid = yaml.safe_load(f)

# Background
c = renderSVG.SVGCanvas(size=(canvas_size_h, canvas_size_v))
# d = shapes.Drawing(canvas_size_h, canvas_size_v)
# d.add(shapes.Rect(0, 0, canvas_size_h, canvas_size_v, fillColor=colors.white))

add_debug_cursor(np.array([0,0]))

# Add content
ccol = np.array([canvas_margin, canvas_size_v], dtype=float)
add_debug_cursor(ccol, color=colors.blue)
for col in grid['columns']:

    # print title

    crow = ccol + np.array([ann_size_h, 0])
    add_debug_cursor(crow, color=colors.aquamarine)
    for row in col['rows']:
        crow -= np.array([0, int(row['height'])])

        # print title

        csym = np.copy(crow)
        for sym in row['symbols']:
            path = pathlib.Path('./symbols') / (sym + '.svg')

            g = svg2rlg(path).asGroup()
            add_debug_cursor(csym, color=colors.green)

            if g.width > 40:
                if g.width % 10 > 1e-3:
                    sym_width = g.width // 10 * 10 + 10
                else:
                    sym_width = g.width // 10 * 10
            else:
                sym_width = 20

            # align symbol in center of cell
            csymi = np.copy(csym) + np.array([(sym_width-g.width)/2,
                                              int(row['height']) / 2 - g.height / 2])

            add_debug_cursor(csymi, color=colors.greenyellow)
            g.translate(*csymi)
            renderSVG.draw(g, c)
            # d.add(g)

            csym += np.array([sym_width, 0])
            csym += np.array([sym_space, 0])

        for ann in row['legend']:
            pass

c.save('../electrical-symbol-library-new.svg')

# Turn top-level group into layer in Inkscape to avoid having to perform an ungroup operation when opening the output
# file for the first time.
with open('../electrical-symbol-library-new.svg', 'r+', encoding='utf8') as f:
    lines = f.readlines()
    for i in range(len(lines)):
        if lines[i].find('<svg') > -1: # add inkscape XML namespace
            lines[i] = lines[i].replace('>', ' xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape">')
        if lines[i].find('<g id="group"') > -1:
            lines[i] = lines[i].replace('id="group"', 'inkscape:groupmode="layer" id="workspace"')
            break
    f.seek(0)
    f.writelines(lines)