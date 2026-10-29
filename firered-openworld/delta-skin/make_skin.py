"""Builds a Delta GBA controller skin for the iPhone Duo inner display, held upright and half-folded:
game above the fold, controls below it."""
import json, zipfile, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 626, 890          # Delta's mapping size for iphone/inner/portrait (points)
FOLD = H / 2             # the hinge runs across the middle when held upright
OUT_SCALE = 3            # Delta renders inner-display assets at 3x -> 1878x2670
SS = 2                   # supersampling for smooth edges
K = OUT_SCALE * SS

# Layout in points
SCREEN = dict(x=13, y=22, width=600, height=400)       # GBA 3:2 at 2.5x, clear of the fold
L_BTN = dict(x=16, y=470, width=170, height=54)
R_BTN = dict(x=440, y=470, width=170, height=54)
MENU = dict(x=278, y=478, width=70, height=38)
DPAD = dict(x=40, y=575, width=210, height=210)
A_BTN = dict(x=482, y=588, width=96, height=96)
B_BTN = dict(x=368, y=666, width=96, height=96)
SELECT = dict(x=214, y=812, width=84, height=32)
START = dict(x=328, y=812, width=84, height=32)

BG = (24, 26, 34); BEZEL = (12, 13, 18); KEY = (58, 62, 76); KEY_HI = (82, 87, 104)
RED = (214, 64, 52); RED_HI = (236, 98, 84); TEXT = (225, 228, 236); DIM = (120, 125, 140)

def font(pt, bold=True):
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf' % ('-Bold' if bold else ''), int(pt * K))
def box(f, inset=0):
    return [(f['x'] + inset) * K, (f['y'] + inset) * K, (f['x'] + f['width'] - inset) * K, (f['y'] + f['height'] - inset) * K]
def label(d, f, text, pt, fill=TEXT, dy=0):
    cx = (f['x'] + f['width'] / 2) * K; cy = (f['y'] + f['height'] / 2 + dy) * K
    d.text((cx, cy), text, font=font(pt), fill=fill, anchor='mm')

def draw(img):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W * K, H * K], fill=BG)
    # top half: bezel around the game screen
    d.rounded_rectangle(box(dict(x=5, y=12, width=616, height=420)), radius=18 * K, fill=BEZEL)
    d.rectangle(box(SCREEN), fill=(0, 0, 0))
    # the fold: a soft darker band so nothing important sits on the crease
    d.rectangle([0, (FOLD - 6) * K, W * K, (FOLD + 6) * K], fill=(16, 17, 23))
    # shoulder buttons + menu
    for f, t in ((L_BTN, 'L'), (R_BTN, 'R')):
        d.rounded_rectangle(box(f), radius=16 * K, fill=KEY, outline=KEY_HI, width=2 * K)
        label(d, f, t, 24)
    d.rounded_rectangle(box(MENU), radius=19 * K, fill=KEY, outline=KEY_HI, width=2 * K)
    label(d, MENU, 'MENU', 13)
    # d-pad
    x, y, s = DPAD['x'], DPAD['y'], DPAD['width']; t = s / 3
    for r in ([x + t, y, x + 2 * t, y + s], [x, y + t, x + s, y + 2 * t]):
        d.rounded_rectangle([v * K for v in r], radius=12 * K, fill=KEY, outline=KEY_HI, width=2 * K)
    d.rectangle([(x + t + 2) * K, (y + t + 2) * K, (x + 2 * t - 2) * K, (y + 2 * t - 2) * K], fill=KEY)
    cx, cy = x + s / 2, y + s / 2
    d.ellipse([(cx - 16) * K, (cy - 16) * K, (cx + 16) * K, (cy + 16) * K], fill=(48, 51, 63))
    a = 13; o = s / 2 - t / 2  # arrow triangles, pointing outward from the centre
    for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
        px, py = cx + dx * o, cy + dy * o
        tip = (px + dx * a * 0.8, py + dy * a * 0.8)
        bx, by = px - dx * a * 0.5, py - dy * a * 0.5
        pts = [tip, (bx - dy * a, by + dx * a), (bx + dy * a, by - dx * a)]
        d.polygon([(u * K, v * K) for u, v in pts], fill=DIM)
    # A / B
    for f, t in ((A_BTN, 'A'), (B_BTN, 'B')):
        d.ellipse(box(f), fill=RED, outline=RED_HI, width=3 * K)
        label(d, f, t, 34)
    # select / start
    for f, t in ((SELECT, 'SELECT'), (START, 'START')):
        d.rounded_rectangle(box(f), radius=16 * K, fill=KEY, outline=KEY_HI, width=2 * K)
        label(d, f, t, 12)

img = Image.new('RGB', (W * K, H * K))
draw(img)
img = img.resize((W * OUT_SCALE, H * OUT_SCALE), Image.LANCZOS)
img.save('inner_portrait.png', optimize=True)

def item(inputs, f, edges=10):
    return {'inputs': inputs, 'frame': f, 'extendedEdges': {'top': edges, 'bottom': edges, 'left': edges, 'right': edges}}
info = {
    'name': 'FireRed Duo (Half-Folded)',
    'identifier': 'com.jorgegzuniga.gba.duo-halffolded',
    'gameTypeIdentifier': 'com.rileytestut.delta.game.gba',
    'debug': False,
    'representations': {'iphone': {'inner': {'portrait': {
        'assets': {'large': 'inner_portrait.png'},
        'items': [
            dict(item({'up': 'up', 'down': 'down', 'left': 'left', 'right': 'right'}, DPAD, 18), extendedEdges={'top': 18, 'bottom': 6, 'left': 18, 'right': 18}),
            item(['a'], A_BTN, 12),
            item(['b'], B_BTN, 12),
            item(['l'], L_BTN, 10),
            item(['r'], R_BTN, 10),
            item(['menu'], MENU, 8),
            item(['select'], SELECT, 12),
            item(['start'], START, 12),
        ],
        'screens': [{'inputFrame': {'x': 0, 'y': 0, 'width': 240, 'height': 160},
                     'outputFrame': SCREEN, 'placement': 'controller'}],
        'mappingSize': {'width': W, 'height': H},
        'extendedEdges': {'top': 7, 'bottom': 7, 'left': 7, 'right': 7},
        'translucent': False,
    }}}},
}
json.dump(info, open('info.json', 'w'), indent=2)
out = sys.argv[1]
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    z.write('info.json'); z.write('inner_portrait.png')
print('wrote', out)
