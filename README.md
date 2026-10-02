# The Festival Star

A 5-minute, fully procedural 3D Pokémon short film, built and rendered with Python scripts in Blender. The film has no people. Its soundtrack is also generated from code: an original orchestral score with Pokémon motifs, plus effects, ambience and the Pokémon's voices (see [Sound](#sound)).

Everything is generated from code: the island, trees and weather, the lighting for each time of day, the character animation, the effects, the camera work and the final edit. **This repo contains only that code.** It includes no game assets (see [Getting the models](#1-getting-the-models)).

## The story

It's the morning of the island festival. **Pikachu** wakes under the giant festival tree and runs off to gather its friends: **Piplup** and **Sobble** at the lake, **Raboot** juggling a ball, and **Greninja**, who jumps down from its rock. **Garchomp** and **Dragonite** join them.

At midday a ball game gets out of hand. Garchomp's super-kick knocks the glowing Star off the top of the tree. It rolls down the meadow and plops into the lake. Greninja dives in and rescues it, but the Star's light has gone out.

At sunset, Pikachu's sparks can't relight it. So Dragonite flies Pikachu up the mountain to wake a sleepy **Charizard**.

That night, Charizard's flame brings the Star back to life. The lanterns light up, a bonfire roars, and the festival ends with a dance and fireworks.

The film runs 42 shots, 300 seconds at 24 fps, in four acts.

## How it's built

```
terrain.py   heightfield (numpy): valley, lake, waterfall plateau, mountain ring, Charizard's peak
world.py     builds world.blend: terrain + shaders, water, waterfall, forests (instanced), grass
             & flowers (geometry nodes, wind, camera-focused density), rocks, cloud deck
leaves.py    leaf-card foliage scattered over canopy blobs (geometry nodes, realized per tree)
festival.py  giant-tree props: paper lanterns, bunting, the Star, picnic, ball (glow via drivers)
look.py      time-of-day presets (Nishita sky, sun, exposure, compositor depth-fog, bloom)
prep.py      imports a character model, rebuilds its materials, normalises orientation/scale
rig.py       procedural character "Actor": root path + layered pose clips -> baked keyframes,
             plus analytic bone transforms (for riding, holding and effects)
anim.py      clip library: walk/run gait, look-at, talk, blink, wave, hop, jump, kick, dance,
             stretch, sleep, sad, surprised, fly/flap, fire-breath, point, ride, ...
fx.py        effects built from keyframed objects: fire, electric sparks, splashes, tears,
             fireflies, fireworks, smoke, glow bursts
shotlib.py   shot framework: cameras (depth of field, handheld shake), attach/ride, titles
shots.py     the screenplay: every shot as a Python function
render.py    renders one shot (preview / stills / final)
render_all.sh, assemble.py, dashboard.py   batch render, ffmpeg edit, live progress page
```

## Requirements

- **Blender 4.5 LTS.** It needs the built-in Collada (`.dae`) importer, which Blender 5.0 removes.
- **Python 3** with Pillow (`pip install pillow`), for preview contact sheets.
- **ffmpeg**, for assembling the movie.
- A GPU that runs EEVEE. It was developed on an Apple M1 MacBook Pro with 16 GB of memory.

The scripts expect Blender at `/Applications/Blender.app/Contents/MacOS/Blender`. If yours is somewhere else, set `BLENDER=/path/to/blender` before running them.

## 1. Getting the models

The Pokémon models are the property of Nintendo, Creatures Inc. and GAME FREAK inc., and are **not included**. You download fan-ripped copies of the in-game models yourself from **[The Models Resource](https://www.models-resource.com/)**. Please respect their terms and don't redistribute them.

1. On The Models Resource, go to **Nintendo Switch → Pokémon Scarlet / Violet**. Download the following models; these are the exact files the film uses:

   | Character | Page on The Models Resource | File used |
   |---|---|---|
   | Pikachu   | #0025 Pikachu   | `pm0025_00_00.dae` (the default form) |
   | Piplup    | #0393 Piplup    | `pm0393_00_00.dae` |
   | Sobble    | #0816 Sobble    | `pm0951_00_00.dae` |
   | Raboot    | #0814 Raboot    | `pm0955_00_00.dae` |
   | Charizard | #0006 Charizard | `pm0006_00_00.dae` |
   | Garchomp  | #0445 Garchomp  | `pm0445_00_00.dae` |
   | Dragonite | #0149 Dragonite | `pm0149_00_00.dae` |

2. **Greninja** comes from **Nintendo Switch → Pokémon Legends: Z-A → Greninja**, file `0725_11_00.dae`. The Scarlet/Violet Greninja imports with an incomplete skeleton, so don't use that one.

3. Unzip each download anywhere under `models/raw/`. Subfolder names don't matter: `prep_all.sh` finds each file by its name. Keep the textures (`.png`) next to each `.dae`.

4. Convert the models into Blender files:

   ```bash
   scripts/prep_all.sh        # -> models/blend/<name>.blend
   ```

   This step rebuilds the materials (base colour, layer-mask tinting, ambient occlusion, normal maps, glossy eyes, emissive fire). It also rotates each rig to face the same way, clears Greninja's broken custom normals and hides Sobble's tear mesh (the film shows it when Sobble cries).

## 2. Build the world

```bash
"$BLENDER" -b --python scripts/world.py      # -> world.blend (about 3 minutes)
```

## 3. Preview and render

```bash
scripts/preview.sh s03_wake                              # 6 low-res stills -> tmp/pv_s03_wake.jpg
"$BLENDER" -b --python scripts/render.py -- s03_wake stills 1,80    # full-quality stills
"$BLENDER" -b --python scripts/render.py -- s03_wake final          # one shot, all frames
scripts/render_all.sh                    # every shot; resumable, skips finished frames
python3 scripts/dashboard.py             # live progress page at http://localhost:8765
python3 scripts/assemble.py              # -> The_Festival_Star.mp4 (with fades at act breaks)
```

The final render is 1920×1080 in EEVEE, with ray-traced reflections, depth of field and motion blur. That takes about 10–18 seconds per frame on an M1, so roughly 24–36 hours for all 7,200 frames. On a Mac, run `caffeinate -dimsu -w <pid>` so the machine doesn't sleep partway through. For a quicker test, lower `FINAL_RES` or the `samples` value in `render.py`.

## Sound

The soundtrack is added after the render, so it never needs the picture re-rendered. The audio code is in `audio/`;
the samples, sound effects and voices aren't in the repo. `audio/fetch_assets.sh` downloads them from their original
sources (about 3.2 GB). Full details and licences are in [`audio/README.md`](audio/README.md).

```bash
audio/fetch_assets.sh                                               # once
(cd audio/music && python3 score.py midi && python3 mix_music.py)   # the score (~13 min)
(cd audio/sfx && python3 sfx.py)                                     # effects, ambience, voices
python3 audio/master.py                                              # -> The_Festival_Star_with_sound.mp4
```

## Making your own shots

A shot is a decorated function in `shots.py`:

```python
@shot('s99_hello', 4, 'morning')          # name, seconds, lighting preset
def s99(S):
    """Pikachu waves at Sobble"""
    P = S.actor('pikachu'); Sb = S.actor('sobble')
    P.key(1, (2, 5), 180)                  # position (x, y) snapped to the ground, facing (degrees)
    Sb.key(1, (2, 3.5), 0)
    P.add(10, 90, wave('left'), 6, 6)      # clip, start/end frame, blend in/out
    P.add(1, 96, look(lambda f: Sb.head_world(f)), 0, 0)
    Sb.add(20, 96, happy_bounce(), 6, 6)
    S.camera(40, 2.8)                      # lens (mm), f-stop
    S.cam_keys([(1, (5, 1, 0.6), (2, 4.3, 0.3), 40)])
```

Lighting presets are `dawn`, `morning`, `noon`, `afternoon`, `golden`, `sunset`, `dusk` and `night`. Story locations like `TREE`, `BLANKET`, `MEADOW`, `LEDGE` and `STAR_HOME` are defined at the top of `shotlib.py`.

## Notes

- The code (MIT licence) is released for learning and fan purposes. Pokémon and all related names and designs are trademarks of Nintendo, Creatures Inc. and GAME FREAK inc. This project is not affiliated with or endorsed by them.
- The animation is generated by code rather than keyframed by hand. Every movement is built from simple layered motions (rotations summed on each bone), so it's easy to change but stylised.
