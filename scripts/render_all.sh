#!/bin/bash
# Render every shot at final quality (resumable: finished frames are skipped).
# usage: scripts/render_all.sh [first_shot]
cd "$(dirname "$0")/.."
BLENDER=${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}
mkdir -p frames/final logs
SHOTS=$(python3 -c "
import re
s=open('scripts/shots.py').read()
print(' '.join(sorted(m for m in re.findall(r\"@shot\('(\w+)'\", s) if m!='test')))
")
for s in $SHOTS; do
  if [ -n "$1" ] && [[ "$s" < "$1" ]]; then continue; fi
  n=$(python3 -c "
import re
s=open('scripts/shots.py').read()
m=re.search(r\"@shot\('$s', (\d+)\", s); print(int(m.group(1))*24)")
  have=$(ls frames/final/$s 2>/dev/null | wc -l | tr -d ' ')
  if [ "$have" -ge "$n" ] && [ -z "$(find frames/final/$s -size 0 2>/dev/null)" ]; then echo "skip $s ($have/$n)"; continue; fi
  # remove zero-byte placeholders from an interrupted run
  find frames/final/$s -size 0 -delete 2>/dev/null
  echo "$(date '+%H:%M:%S') render $s ($have/$n)"
  "$BLENDER" -b --python scripts/render.py -- $s final > logs/$s.log 2>&1
  grep -E "FINAL|Error|Traceback" logs/$s.log | tail -3
done
echo "$(date '+%H:%M:%S') ALL SHOTS RENDERED"
