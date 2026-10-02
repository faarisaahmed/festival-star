#!/usr/bin/env bash
# Download everything the soundtrack needs. None of it is in this repo; it all comes from its original source.
# About 3.2 GB of downloads, about 3 GB on disk. Safe to re-run: anything already present is skipped.
#   audio/fetch_assets.sh
set -euo pipefail
cd "$(dirname "$0")"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
dl() { [ -s "$2" ] || { echo "  $2"; curl -fL --retry 3 -A "$UA" -o "$2.part" "$1" && mv "$2.part" "$2"; }; }

echo "== python packages"
python3 -m pip install --quiet numpy scipy soundfile mido pyloudnorm

echo "== sfizz (SFZ sample player, built from source; needs cmake + ninja)"
if [ ! -x tools/sfizz/build/library/bin/sfizz_render ]; then
  [ -d tools/sfizz ] || git clone --recursive --depth 1 https://github.com/sfztools/sfizz.git tools/sfizz
  cmake -S tools/sfizz -B tools/sfizz/build -G Ninja -DCMAKE_BUILD_TYPE=Release -DSFIZZ_RENDER=ON -DSFIZZ_JACK=OFF \
        -DSFIZZ_LV2=OFF -DSFIZZ_VST=OFF -DSFIZZ_AU=OFF -DSFIZZ_SHARED=OFF -DSFIZZ_TESTS=OFF -DSFIZZ_DEMOS=OFF \
        -DSFIZZ_BENCHMARKS=OFF > /dev/null
  ninja -C tools/sfizz/build > /dev/null
fi

echo "== Virtual Playing Orchestra 3 (orchestral samples, free - virtualplaying.com)"
mkdir -p vpo
if [ ! -d vpo/Virtual-Playing-Orchestra3/libs ]; then
  dl https://archive.org/download/virtual-playing-orchestra-3-2-wave-files/Virtual-Playing-Orchestra3-2-wave-files.zip vpo/wav.zip
  dl https://virtualplaying.com/vp-downloads/Virtual-Playing-Orchestra3-3-performance-scripts.zip vpo/perf.zip
  dl https://virtualplaying.com/vp-downloads/Virtual-Playing-Orchestra3-3-standard-scripts.zip vpo/std.zip
  (cd vpo && unzip -q -o wav.zip && unzip -q -o perf.zip && unzip -q -o std.zip && rm -f wav.zip perf.zip std.zip)
fi

echo "== Salamander Grand Piano V3 (freepats.zenvoid.org)"
mkdir -p piano
if ! ls piano/*/SalamanderGrandPianoV3.sfz > /dev/null 2>&1; then
  dl https://freepats.zenvoid.org/Piano/SalamanderGrandPiano/SalamanderGrandPianoV3+20161209_48khz24bit.tar.xz piano/sal.tar.xz
  (cd piano && tar xJf sal.tar.xz && rm sal.tar.xz)
fi

echo "== MuseScore General soundfont (marimba, koto, taiko, accordion, woodblock)"
mkdir -p sf2
dl https://ftp.osuosl.org/pub/musescore/soundfont/MuseScore_General/MuseScore_General.sf2 sf2/MuseScore_General.sf2

echo "== BBC Sound Effects (RemArc licence: personal, educational and research use only)"
mkdir -p sfx/raw
while read -r id name; do
  [ -z "$id" ] && continue
  [ -s "sfx/raw/$name.wav" ] || { echo "  $name"; python3 tools/bbc.py get "$id" "sfx/raw/$name.wav"; }
done < sfx/bbc_sounds.txt

echo "== Pokémon cries (PokeAPI + Pokémon Showdown)"
mkdir -p cries
for p in pikachu:25 piplup:393 sobble:816 raboot:814 greninja:658 charizard:6 garchomp:445 dragonite:149; do
  n=${p%%:*}; i=${p##*:}
  dl "https://raw.githubusercontent.com/PokeAPI/cries/main/cries/pokemon/latest/$i.ogg" "cries/$n.ogg"
  dl "https://play.pokemonshowdown.com/audio/cries/$n.mp3" "cries/${n}_sd.mp3"
done

echo "== Pokémon voice clips (game rips listed in cries/extra/INDEX.md)"
python3 tools/fetch_voices.py

echo "done. Next: (cd music && python3 score.py midi && python3 mix_music.py); (cd sfx && python3 sfx.py); python3 master.py"
