#!/bin/bash
# Convert the downloaded models (models/raw/**) into models/blend/<name>.blend
# (rebuilds materials, fixes normal maps, bakes Y-up -> Z-up, hides extra meshes).
set -e
cd "$(dirname "$0")/.."
BLENDER=${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}
mkdir -p models/blend
prep() {  # name  dae-filename
  f=$(find models/raw -name "$2" | head -1)
  if [ -z "$f" ]; then echo "!! missing $2 for $1 (see README)"; return 1; fi
  echo "prep $1 <- $f"
  "$BLENDER" -b --python scripts/prep.py -- "$1" "$f" "models/blend/$1.blend" > /dev/null 2>&1
}
prep pikachu   pm0025_00_00.dae
prep piplup    pm0393_00_00.dae
prep sobble    pm0951_00_00.dae
prep raboot    pm0955_00_00.dae
prep greninja  0725_11_00.dae
prep charizard pm0006_00_00.dae
prep garchomp  pm0445_00_00.dae
prep dragonite pm0149_00_00.dae
echo done
