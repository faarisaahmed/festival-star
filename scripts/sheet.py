import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))) + '/'
import sys, glob
from PIL import Image, ImageDraw
name = sys.argv[1]
fs = sorted(glob.glob(ROOT + f'tmp/clips/{name}_*.png'))
cols = 7; W = 256
rows = (len(fs) + cols - 1) // cols
im = Image.new('RGB', (cols * W, rows * W))
d = ImageDraw.Draw(im)
for i, f in enumerate(fs):
    x, y = (i % cols) * W, (i // cols) * W
    im.paste(Image.open(f).convert('RGB'), (x, y))
    d.text((x + 4, y + 4), f.split('_', 2)[-1][:-4], fill=(0, 0, 0))
im.save(ROOT + f'tmp/clips_{name}.jpg', quality=85)
