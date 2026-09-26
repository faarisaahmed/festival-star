#!/bin/bash
# Quick low-res contact sheet of one shot: scripts/preview.sh s03_wake  -> tmp/pv_s03_wake.jpg
cd "$(dirname "$0")/.."
BLENDER=${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}
mkdir -p tmp frames/pstills
rm -f frames/pstills/$1_*.jpg
"$BLENDER" -b --python scripts/render.py -- $1 pstills ${2:-auto} 2>&1 | grep -E "BUILD|Error|Traceback" -A6
python3 - "$1" <<'P'
import sys, glob
from PIL import Image
n = sys.argv[1]
fs = sorted(glob.glob(f'frames/pstills/{n}_*.jpg'))
W, H, cols = 640, 360, 3
im = Image.new('RGB', (cols * W, ((len(fs) + cols - 1) // cols) * H))
for i, f in enumerate(fs):
    im.paste(Image.open(f), ((i % cols) * W, (i // cols) * H))
im.save(f'tmp/pv_{n}.jpg', quality=85)
print('wrote', f'tmp/pv_{n}.jpg')
P
