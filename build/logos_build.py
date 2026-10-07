"""把 logos/ 下的原图裁掉四周留白，统一 24px 高、宽度按原比例，输出 {ticker: {src, w, h}}。"""
import base64, glob, io, json, os
from PIL import Image, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

BOX_W, BOX_H = 9999, 24  # 统一高度，宽度随原比例
SRC = {os.path.basename(f)[:-4]: f for f in glob.glob('logos/*.png') if '_bw' not in f and '_user' not in f}
SRC['MRVL'] = 'logos/MRVL_bw.png'
SRC['SPCX'] = 'logos/SPCX_user.png'          # 用户提供的 SpaceX 字标
SRC['SNDK'] = 'logos/SNDK_user.png'          # 用户提供的闪迪字标


def crop(im):
    im = im.convert('RGBA')
    bg = Image.new('RGBA', im.size, (255, 255, 255, 0))
    flat = Image.alpha_composite(Image.new('RGBA', im.size, 'white'), im).convert('L')
    ink = flat.point(lambda v: 255 if v < 235 else 0)          # 非白像素
    alpha = im.split()[3].point(lambda v: 255 if v > 20 else 0)
    mask = ImageChops.multiply(ink, alpha) if im.getextrema()[3][0] < 255 else ink
    bb = mask.getbbox() or (0, 0, *im.size)
    pad = 2
    return im.crop((max(bb[0] - pad, 0), max(bb[1] - pad, 0), min(bb[2] + pad, im.width), min(bb[3] + pad, im.height)))


out = {}
for tk, f in SRC.items():
    im = crop(Image.open(f))
    ar = im.width / im.height
    w, h = (BOX_W, BOX_W / ar) if BOX_H * ar > BOX_W else (BOX_H * ar, BOX_H)
    t = im.copy()
    t.thumbnail((round(w * 2), round(h * 2)), Image.LANCZOS)   # 2 倍分辨率，高分屏不糊
    buf = io.BytesIO(); t.save(buf, 'PNG', optimize=True)
    out[tk] = dict(src='data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode(), w=round(w), h=round(h))

# 亚马逊：FMP 图只有微笑箭头，改用 Wikimedia 的完整字标 SVG（603x182）
svg = open('logos/AMZN.svg', 'rb').read()
ar = 603 / 182
out['AMZN'] = dict(src='data:image/svg+xml;base64,' + base64.b64encode(svg).decode(),
                   w=round(min(BOX_W, BOX_H * ar)), h=round(min(BOX_W, BOX_H * ar) / ar))
# 字标型 logo 统一高度后显得过重，按用户要求缩到 0.8 倍
for tk in ('SPCX', 'INTC', 'LIN', 'COST', 'LRCX', 'AMZN', 'SNDK'):
    out[tk]['w'] = round(out[tk]['w'] * 0.8); out[tk]['h'] = round(BOX_H * 0.8, 1)
json.dump(out, open('build/logos.json', 'w'))
for k in ('SPCX', 'INTC', 'AMZN', 'MRVL', 'NVDA'):
    print(k, out[k]['w'], out[k]['h'])
