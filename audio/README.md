# The Festival Star: sound

The soundtrack is built entirely from code: an original orchestral score, sound effects, ambience and the Pokémon's
voices, all placed to the picture and mixed onto the finished movie. **The video is not re-rendered.** The audio is
muxed onto the existing video stream (`ffmpeg -c:v copy`).

**This folder contains only code.** The audio itself isn't included. There are no samples, sound effects, cries or
rendered music: they are large, and most of them can't be redistributed. `fetch_assets.sh` downloads everything from
the original sources.

## Building the soundtrack

Requirements: Python 3, `ffmpeg`, `fluidsynth`, plus `cmake`, `ninja` and a C++ compiler (to build sfizz).
On a Mac: `brew install ffmpeg fluid-synth cmake ninja`.

```bash
audio/fetch_assets.sh                                        # about 3.2 GB of downloads, run once (see below)
(cd audio/music && python3 score.py midi && python3 mix_music.py)   # the score -> music/score_mix.wav (~13 min)
(cd audio/sfx && python3 sfx.py)                                     # ambience, effects, voices -> sfx/out/ (~20 s)
python3 audio/master.py                                              # mix + master -> The_Festival_Star_with_sound.mp4
```

`master.py` expects the rendered `The_Festival_Star.mp4` (from `scripts/assemble.py`) in the repo root. It writes:
- `The_Festival_Star_with_sound.mp4` next to it
- the master WAV and four stems (music, ambience, effects, voices) in `audio/final/`

### What `fetch_assets.sh` downloads

| What | Used for | Source |
|---|---|---|
| sfizz (built from source) | plays the SFZ sample libraries | github.com/sfztools/sfizz |
| Virtual Playing Orchestra 3.2 wave files + 3.3 scripts (~700 MB) | strings, woodwinds, brass, harp, celesta, mallets, timpani, cymbals, choir | virtualplaying.com (free, no restrictions) |
| Salamander Grand Piano V3 (~1.2 GB) | piano | freepats.zenvoid.org (CC-BY) |
| MuseScore General soundfont (~215 MB) | marimba, koto, taiko, accordion, woodblock | MuseScore (MIT) |
| 61 BBC Sound Effects (`sfx/bbc_sounds.txt`, ~1 GB) | ambiences, water, fire, wings, footsteps, fireworks | sound-effects.bbcrewind.co.uk (RemArc licence: personal, educational, research use) |
| Pokémon cries | each Pokémon's main cry | PokeAPI cries, Pokémon Showdown |
| 231 voice clips (`cries/extra/INDEX.md`) | Pikachu's lines, roars, sobs, cheers | game rips on sounds.spriters-resource.com, fetched by `tools/fetch_voices.py` |

If some voice clips can't be fetched (a page moved, say), `sfx.py` falls back to that Pokémon's standard cry and
prints which clips are missing.

## How it works

```
music/score.py       the screenplay of the score: every cue as code, in absolute seconds against the picture
music/engine.py      tiny scoring engine: notes/chords/arpeggios/dynamics -> one MIDI file per instrument;
                     plays them through sfizz (sampled orchestra) or FluidSynth (soundfont)
music/mix_music.py   renders the stems, pans them, adds a synthetic concert-hall reverb, masters
music/balance.py     checks the melody sits on top of the accompaniment in each scene
sfx/sfx.py           every sound effect, ambience bed and voice line placed to the frame; also synthesises
                     the magic (Star twinkles, chimes, the reignition), Pikachu's electricity, wingbeats, whooshes
master.py            loudness-matches the stems, ducks the music under voices, limits, muxes into the mp4
tools/               BBC SFX search/fetch, onset finder, MIDI dumper, voice-clip fetcher
```

Event times come straight from the frame numbers in `scripts/shots.py`. Each shot starts at the cumulative sum of the
shot lengths, sorted by name, the same way `assemble.py` orders them.

### The score
The score is original. It has a Festival Star theme, a Star motif, and motifs for Charizard, Dragonite, Greninja and
Sobble. It also quotes short, re-harmonised Pokémon motifs:
- the Red/Blue title fanfare (opening, flight)
- Pallet Town (morning, the rescue)
- Route 1 (the run, the dance jig)
- the Pokémon Center theme (Dragonite comforts Garchomp)
- the healing jingle (in the bells when the Star relights)
- the Red/Blue ending theme (fireworks, finale)

Dynamics drive the mod wheel (cc1) of the Performance patches.

Glissandos on strings, winds and brass are true continuous slides: one note on its own channel, bent smoothly
(±24 semitones) with an eased curve. Harp and mallet glissandos are evenly paced sweeps (at most ~16 notes a second)
with every note left to ring. Timpani and cymbal rolls use real roll samples, so they don't sound like repeated hits.

## Licences
The code is MIT, like the rest of the repo. The downloaded assets keep their own licences (see the table).
The BBC effects are licensed for personal, educational and research use only, so a soundtrack built with them is too.
Pokémon cries, voices and musical motifs belong to Nintendo, Creatures Inc. and GAME FREAK inc.
This is a non-commercial fan project.
