# Extra Pokémon vocalisations

Variety pack to complement the single modern cry per Pokémon in `audio/cries/`. All files: 48 kHz, stereo, 16-bit PCM WAV, leading/trailing silence trimmed (-55 dB), peak-normalised to -1 dBFS (plain gain, no compression).

**Sources** (game rips from The Sounds Resource, sounds.spriters-resource.com, plus PokeAPI legacy cries):
- **Pokkén Tournament** (Wii U) – Pikachu/Charizard/Garchomp voice banks with *named* reactions (LAUGH, SURPRISE, CMN_HAPPY/SAD/ANGRY, WIN, LOSE, KIAI…). Pikachu is Ikue Ohtani (anime voice). Labels are reliable.
- **Super Smash Bros. Ultimate** (Switch) – Pikachu, Charizard, Greninja (English voice bank) with named actions (taunt, sleep, dizzy, KO, teeter…). Labels reliable.
- **Pokémon Scarlet/Violet** (Switch) – emotion-labelled cry variants (GLAD1-3, SAD, ANGER, ENV, INDEX, ATK, SPATK, EX1-4) for Pikachu, Charizard, Dragonite, Piplup, Garchomp, Greninja. Labels come from the game data. SV Pikachu uses the Ohtani anime voice.
- **Pikachu voice bank PM025_01–99** (ripped from Pokémon Sword/Shield; this is the Ohtani “partner Pikachu” bank shared with Let's Go Pikachu) – file names are opaque; labels are **heuristic** (duration, syllable count, pitch and pitch slope via ffmpeg/numpy analysis, not by listening).
- **Hey You, Pikachu!** (N64), **Pokémon Stadium** (N64, “Pikachu_Anime” clips), **PokéPark 2** (Wii) – Ohtani Pikachu lines with opaque numeric names; labels are **heuristic**.
- **Pokémon Sword/Shield** cry variants 00_00–00_04 (Sobble, Raboot, Charizard, Garchomp, Dragonite) – the rip does not name the emotion; Sobble labels are heuristic.
- **Pokémon Snap** (N64) Dragonite; **Pokémon Stadium** game cries; **PokeAPI legacy** cries.

Not found: a dedicated anime-style Sobble *crying* clip (no game rip has one; SwSh variant `sobble/swsh_variant_03_long_sob.wav` is the closest). No extra Raboot/Sobble sources beyond SwSh (they are not in SV/Pokkén/Smash). Pokémon Unite / New Pokémon Snap / Mystery Dungeon DX / Let's Go have no voice rips on the site; myinstants is Cloudflare-blocked to curl.

Filename prefix = source game: `pokken_`, `smash_`, `sv_`, `letsgo_`, `heyyou_`, `stadium_`, `pokepark2_`, `swsh_`, `snap_`, `legacy_`.

## Pikachu (95 files)

| File | Dur (s) | Description | Original file | Source |
|---|---|---|---|---|
| `pikachu/sv_happy_01.wav` | 0.59 | Scarlet/Violet "GLAD1" emotion cry - happy/pleased | `PLAY_PV_0025 [PV=GLAD1].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454133/ |
| `pikachu/sv_happy_02.wav` | 0.60 | Scarlet/Violet "GLAD2" emotion cry - happy, alt take | `PLAY_PV_0025 [PV=GLAD2].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454133/ |
| `pikachu/sv_happy_03_big.wav` | 0.81 | Scarlet/Violet "GLAD3" emotion cry - biggest/most excited happy | `PLAY_PV_0025 [PV=GLAD3].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454133/ |
| `pikachu/sv_sad.wav` | 1.08 | Scarlet/Violet "SAD" emotion cry - sad/downcast (droopy version of cry) | `PLAY_PV_0025 [PV=SAD].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454133/ |
| `pikachu/sv_angry.wav` | 0.89 | Scarlet/Violet "ANGER" emotion cry - angry/annoyed | `PLAY_PV_0025 [PV=ANGER].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454133/ |
| `pikachu/sv_ambient_call.wav` | 0.85 | Scarlet/Violet "ENV" overworld/ambient call (wild idle vocalisation) | `PLAY_PV_0025 [PV=ENV].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454133/ |
| `pikachu/sv_short_04.wav` | 0.60 | Scarlet/Violet "EX4" extra clip - medium vocal fragment | `PLAY_PV_0025 [PV=EX4].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454133/ |
| `pikachu/sv_special_attack_cry.wav` | 0.50 | Scarlet/Violet "SPATK" special-attack shout | `PLAY_PV_0025 [PV=SPATK].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454133/ |
| `pikachu/pokken_intro_pika_01.wav` | 1.01 | Pokken Tournament (Ikue Ohtani anime voice) - battle-intro "Pika!" call | `VC_P025_V000_APPEAR_01.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399931/ |
| `pikachu/pokken_intro_pikachu_02.wav` | 3.04 | Pokken - longer battle-intro line, "Pika pika... Pikachu!"-style | `VC_P025_V000_APPEAR_03.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399931/ |
| `pikachu/pokken_intro_long_03.wav` | 3.81 | Pokken - longest intro line (~3.8s), energetic chatter | `VC_P025_V000_APPEAR_04.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399931/ |
| `pikachu/pokken_laugh.wav` | 1.55 | Pokken - Pikachu laughing/giggling | `VC_P025_V000_LAUGH.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399931/ |
| `pikachu/pokken_surprised.wav` | 0.86 | Pokken - surprised "Pika?!" | `VC_P025_V000_SURPRISE.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399931/ |
| `pikachu/pokken_happy_good.wav` | 1.09 | Pokken - pleased/approving "Pika!" (GOOD reaction) | `VC_P025_V000_GOOD.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399931/ |
| `pikachu/pokken_disappointed.wav` | 1.02 | Pokken - disappointed/unhappy reaction (BAD) | `VC_P025_V000_BAD.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399931/ |
| `pikachu/pokken_win_cheer_01.wav` | 3.02 | Pokken - victory cheer | `VC_P025_V000_WIN_01.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399931/ |
| `pikachu/pokken_win_cheer_02_long.wav` | 4.36 | Pokken - long victory celebration (~5.5s) | `VC_P025_V000_WIN_02.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399931/ |
| `pikachu/pokken_win_cheer_03.wav` | 2.41 | Pokken - victory cheer, alt | `VC_P025_V000_WIN_03.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399931/ |
| `pikachu/pokken_sad_lose.wav` | 3.38 | Pokken - sad/defeated whimper (lose) | `VC_P025_V000_LOSE.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399931/ |
| `pikachu/pokken_knocked_out.wav` | 2.87 | Pokken - knocked-out cry, falling "Pika-chuuu..." | `VC_P025_V000_LOSE_HP_ZERO.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399931/ |
| `pikachu/pokken_sad_short.wav` | 1.24 | Pokken - short dejected "pika..." (time-up loss) | `VC_P025_V000_LOSE_TIME_UP.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399931/ |
| `pikachu/pokken_strain_effort.wav` | 1.33 | Pokken - straining/powering-up effort shout (KIAI) | `VC_P025_V000_KIAI_03.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399931/ |
| `pikachu/pokken_effort_short.wav` | 0.69 | Pokken - short effort grunt "Pi!" | `VC_P025_V000_KIAI_01.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399931/ |
| `pikachu/pokken_big_attack_shout.wav` | 1.57 | Pokken - full-power attack yell "Pikaaa-chu!" | `VC_P025_V000_ATTACK_MAX_01.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399931/ |
| `pikachu/pokken_attack_shout.wav` | 1.95 | Pokken - strong attack shout | `VC_P025_V000_ATTACK_L_02.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399931/ |
| `pikachu/pokken_pi_short.wav` | 0.68 | Pokken - very short "Pi!" (light attack) | `VC_P025_V000_ATTACK_S_03.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399931/ |
| `pikachu/pokken_hurt.wav` | 1.46 | Pokken - hurt/pained cry | `VC_P025_V000_DAMAGE_L_02.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399931/ |
| `pikachu/pokken_dizzy.wav` | 2.02 | Pokken - stunned/dizzy wobbly voice (guard crush) | `VC_P025_V000_GUARD_CRUSH_01.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399931/ |
| `pikachu/pokken_powerup_shout.wav` | 1.13 | Pokken - power-up/burst shout | `VC_P025_V000_BURST_ATTACK_START.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399931/ |
| `pikachu/smash_taunt_01.wav` | 0.87 | Smash Bros Ultimate (Ohtani) - taunt "Pika..."-style | `vc_pikachu_appeal01.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409668/ |
| `pikachu/smash_taunt_pika_pika.wav` | 1.03 | Smash Ultimate - taunt, multi-syllable "Pika pika!" | `vc_pikachu_appeal02.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409668/ |
| `pikachu/smash_taunt_pikachu.wav` | 1.21 | Smash Ultimate - taunt "Pikachu!" | `vc_pikachu_appeal03.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409668/ |
| `pikachu/smash_long_pikachu.wav` | 3.17 | Smash Ultimate - long ~3.2s line (final-smash style "Pikaaa... chuuu!") | `vc_pikachu_006.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409668/ |
| `pikachu/smash_charge_strain.wav` | 1.59 | Smash Ultimate - sustained charge/strain ~1.6s | `vc_pikachu_004.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409668/ |
| `pikachu/smash_sleepy_yawn.wav` | 1.51 | Smash Ultimate - sleepy/drowsy (fall-asleep) murmur, closest to a yawn | `vc_pikachu_furasleep.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409668/ |
| `pikachu/smash_dizzy.wav` | 1.33 | Smash Ultimate - dazed/dizzy groan | `vc_pikachu_furafura.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409668/ |
| `pikachu/smash_whoa_teeter.wav` | 0.50 | Smash Ultimate - "whoa!" teetering on edge (startled) | `vc_pikachu_ottotto.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409668/ |
| `pikachu/smash_ko_scream.wav` | 2.75 | Smash Ultimate - KO scream (~3.3s) | `vc_pikachu_knockout.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409668/ |
| `pikachu/smash_launched_cry.wav` | 2.43 | Smash Ultimate - long cry when launched off-screen | `vc_pikachu_damage_twinkle.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409668/ |
| `pikachu/smash_slip_surprise.wav` | 1.21 | Smash Ultimate - slip/trip yelp (surprised) | `vc_pikachu_missfoot01.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409668/ |
| `pikachu/smash_lift_heavy_strain.wav` | 0.91 | Smash Ultimate - lifting heavy object, straining grunt | `vc_pikachu_heavyget.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409668/ |
| `pikachu/smash_hurt_short.wav` | 0.41 | Smash Ultimate - short hurt "Pi!" | `vc_pikachu_damage01.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409668/ |
| `pikachu/letsgo_pikachu_cheer.wav` | 1.89 | Lets Go Pikachu/SwSh partner voice bank (Ohtani) PM025_40 - bright 3-syllable "Pi-ka-chu!" (used as SwSh in-game cry) | `Play_PV_025_00_00 [PM025VC=PM025_40].ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/488706/ |
| `pikachu/letsgo_pika_pikachu.wav` | 1.98 | PM025_84 - 4-syllable "Pika-pikachu!" (SwSh in-game cry alt) | `Play_PV_025_00_00 [PM025VC=PM025_84].ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/488706/ |
| `pikachu/letsgo_pika_calm_low.wav` | 1.15 | PM025_32 - low, calm 2-syllable "Pi-ka" (SwSh in-game cry alt) | `Play_PV_025_00_00 [PM025VC=PM025_32].ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/488706/ |
| `pikachu/letsgo_pika_pika_happy.wav` | 1.16 | PM025_30 - high bright 2-syllable "Pika pika!" (heuristic: happy) | `Play_PV_025_00_00 [PM025VC=PM025_30].ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/488706/ |
| `pikachu/letsgo_pika_pika_excited_fast.wav` | 1.52 | PM025_37 - high, rapid 7-syllable chatter (heuristic: excited) | `Play_PV_025_00_00 [PM025VC=PM025_37].ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/488706/ |
| `pikachu/letsgo_pikachu_excited_high.wav` | 1.39 | PM025_75 - very high bright "Pikachu!" (heuristic: excited) | `Play_PV_025_00_00 [PM025VC=PM025_75].ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/488706/ |
| `pikachu/letsgo_pikachu_high_falling.wav` | 1.23 | PM025_74 - high 3-syllable with falling pitch (heuristic: cheerful) | `Play_PV_025_00_00 [PM025VC=PM025_74].ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/488706/ |
| `pikachu/letsgo_sigh_yawn_low.wav` | 1.62 | PM025_11 - single long low sustained sound ~2s (heuristic: sigh/yawn) | `Play_PV_025_00_00 [PM025VC=PM025_11].ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/488706/ |
| `pikachu/letsgo_sleepy_low.wav` | 3.63 | PM025_26 - long dark low-pitched ~3.8s (heuristic: sleepy/drowsy) | `Play_PV_025_00_00 [PM025VC=PM025_26].ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/488706/ |
| `pikachu/letsgo_sad_long.wav` | 5.27 | PM025_62 - long low ~5.3s, 6 syllables (heuristic: sad/whiny) | `Play_PV_025_00_00 [PM025VC=PM025_62].ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/488706/ |
| `pikachu/letsgo_sad_low.wav` | 3.64 | PM025_69 - low falling ~3.8s (heuristic: sad/tired) | `Play_PV_025_00_00 [PM025VC=PM025_69].ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/488706/ |
| `pikachu/letsgo_pika_question_01.wav` | 0.66 | PM025_22 - short single syllable rising pitch (heuristic: questioning "Pika?") | `Play_PV_025_00_00 [PM025VC=PM025_22].ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/488706/ |
| `pikachu/letsgo_pika_question_02.wav` | 0.51 | PM025_51 - short rising (heuristic: curious "Pi?") | `Play_PV_025_00_00 [PM025VC=PM025_51].ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/488706/ |
| `pikachu/letsgo_pi_surprised.wav` | 0.78 | PM025_53 - short high falling "Pi!" (heuristic: surprised) | `Play_PV_025_00_00 [PM025VC=PM025_53].ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/488706/ |
| `pikachu/letsgo_squeal_high.wav` | 2.97 | PM025_77 - very high rising ~3.3s (heuristic: squeal/shriek) | `Play_PV_025_00_00 [PM025VC=PM025_77].ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/488706/ |
| `pikachu/letsgo_chatter_long.wav` | 5.50 | PM025_16 - long ~5.5s high chatter, 13 syllables (heuristic: happy babbling) | `Play_PV_025_00_00 [PM025VC=PM025_16].ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/488706/ |
| `pikachu/letsgo_chatter_long_02.wav` | 5.17 | PM025_64 - long ~5.2s chatter, 13 syllables | `Play_PV_025_00_00 [PM025VC=PM025_64].ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/488706/ |
| `pikachu/letsgo_pi_tiny.wav` | 0.30 | PM025_21 - tiny 0.4s "pi" | `Play_PV_025_00_00 [PM025VC=PM025_21].ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/488706/ |
| `pikachu/letsgo_pikaaa_rising.wav` | 1.32 | PM025_46 - ~1.4s single drawn-out rising "Pikaaa?" | `Play_PV_025_00_00 [PM025VC=PM025_46].ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/488706/ |
| `pikachu/letsgo_pika_pika_cheer.wav` | 2.15 | PM025_99 - high 6-syllable ~2.3s cheer | `Play_PV_025_00_00 [PM025VC=PM025_99].ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/488706/ |
| `pikachu/stadium_anime_pikachu_01.wav` | 1.82 | Pokemon Stadium N64 anime-voice clip 02 (Ohtani) - 3-syllable "Pikachu" | `#025_Pikachu_Anime02.wav` | https://sounds.spriters-resource.com/nintendo_64/pokemonstadium/asset/427768/ |
| `pikachu/stadium_anime_pika_02.wav` | 1.25 | Stadium anime clip 03 - 2-syllable "Pika!" | `#025_Pikachu_Anime03.wav` | https://sounds.spriters-resource.com/nintendo_64/pokemonstadium/asset/427768/ |
| `pikachu/stadium_anime_pikachu_03.wav` | 2.22 | Stadium anime clip 04 - 3-syllable "Pikachu" ~2.5s | `#025_Pikachu_Anime04.wav` | https://sounds.spriters-resource.com/nintendo_64/pokemonstadium/asset/427768/ |
| `pikachu/stadium_anime_pika_pika_04.wav` | 1.58 | Stadium anime clip 05 - rapid 5-syllable "Pika pika pi" | `#025_Pikachu_Anime05.wav` | https://sounds.spriters-resource.com/nintendo_64/pokemonstadium/asset/427768/ |
| `pikachu/stadium_anime_rising_05.wav` | 2.04 | Stadium anime clip 06 - 4 syllables, rising pitch (heuristic: excited/questioning) | `#025_Pikachu_Anime06.wav` | https://sounds.spriters-resource.com/nintendo_64/pokemonstadium/asset/427768/ |
| `pikachu/stadium_anime_rising_06.wav` | 3.26 | Stadium anime clip 07 - 2 syllables rising ~3.5s | `#025_Pikachu_Anime07.wav` | https://sounds.spriters-resource.com/nintendo_64/pokemonstadium/asset/427768/ |
| `pikachu/stadium_anime_pika_pikachu_07.wav` | 2.53 | Stadium anime clip 10 - 5-syllable "Pika pika-chu" | `#025_Pikachu_Anime10.wav` | https://sounds.spriters-resource.com/nintendo_64/pokemonstadium/asset/427768/ |
| `pikachu/stadium_anime_chuu_08.wav` | 1.58 | Stadium anime clip 12 - single drawn-out syllable | `#025_Pikachu_Anime12.wav` | https://sounds.spriters-resource.com/nintendo_64/pokemonstadium/asset/427768/ |
| `pikachu/stadium_anime_falling_09.wav` | 1.47 | Stadium anime clip 13 - 2 syllables strongly falling pitch (heuristic: sad/deflated) | `#025_Pikachu_Anime13.wav` | https://sounds.spriters-resource.com/nintendo_64/pokemonstadium/asset/427768/ |
| `pikachu/stadium_anime_pikaaa_10.wav` | 1.17 | Stadium anime clip 14 - single sustained high "Pikaaa" | `#025_Pikachu_Anime14.wav` | https://sounds.spriters-resource.com/nintendo_64/pokemonstadium/asset/427768/ |
| `pikachu/heyyou_pikachu_01.wav` | 1.50 | Hey You, Pikachu! (N64, Ohtani) clip 1 - ~1.5s single sustained call | `1.wav` | https://sounds.spriters-resource.com/nintendo_64/heyyoupikachu/asset/396106/ |
| `pikachu/heyyou_long_02.wav` | 3.33 | Hey You Pikachu clip 2 - ~3.3s, 4 syllables | `2.wav` | https://sounds.spriters-resource.com/nintendo_64/heyyoupikachu/asset/396106/ |
| `pikachu/heyyou_chatter_high.wav` | 2.47 | Hey You Pikachu clip 5 - high, 8-syllable chatter (heuristic: happy) | `5.wav` | https://sounds.spriters-resource.com/nintendo_64/heyyoupikachu/asset/396106/ |
| `pikachu/heyyou_chatter_rapid.wav` | 3.68 | Hey You Pikachu clip 6 - rapid ~3.8s 16-syllable babble, rising (heuristic: excited/laughing) | `6.wav` | https://sounds.spriters-resource.com/nintendo_64/heyyoupikachu/asset/396106/ |
| `pikachu/heyyou_bright_call.wav` | 1.97 | Hey You Pikachu clip 7 - bright ~2s 2-syllable call | `7.wav` | https://sounds.spriters-resource.com/nintendo_64/heyyoupikachu/asset/396106/ |
| `pikachu/heyyou_low_rising.wav` | 2.51 | Hey You Pikachu clip 8 - low ~2.5s (heuristic: whiny/pleading) | `8.wav` | https://sounds.spriters-resource.com/nintendo_64/heyyoupikachu/asset/396106/ |
| `pikachu/heyyou_low_long_sad.wav` | 3.57 | Hey You Pikachu clip 10 - low dark ~3.6s (heuristic: sad/grumbly) | `10.wav` | https://sounds.spriters-resource.com/nintendo_64/heyyoupikachu/asset/396106/ |
| `pikachu/heyyou_pika_question.wav` | 0.58 | Hey You Pikachu clip 11 - short 2-syllable rising "Pika?" | `11.wav` | https://sounds.spriters-resource.com/nintendo_64/heyyoupikachu/asset/396106/ |
| `pikachu/heyyou_pi_bright.wav` | 0.99 | Hey You Pikachu clip 16 - bright ~1s "Pi!" | `16.wav` | https://sounds.spriters-resource.com/nintendo_64/heyyoupikachu/asset/396106/ |
| `pikachu/heyyou_giggle.wav` | 2.11 | Hey You Pikachu clip 22 - 9 fast syllables in 2s (heuristic: giggle/laugh) | `22.wav` | https://sounds.spriters-resource.com/nintendo_64/heyyoupikachu/asset/396106/ |
| `pikachu/heyyou_chu_rising.wav` | 0.55 | Hey You Pikachu clip 29 - short sharp rising (heuristic: surprised "Chu?!") | `29.wav` | https://sounds.spriters-resource.com/nintendo_64/heyyoupikachu/asset/396106/ |
| `pikachu/heyyou_pika_rising.wav` | 0.44 | Hey You Pikachu clip 36 - short rising "pika?" | `36.wav` | https://sounds.spriters-resource.com/nintendo_64/heyyoupikachu/asset/396106/ |
| `pikachu/heyyou_long_chatter_low.wav` | 3.38 | Hey You Pikachu clip 30 - ~3.4s low 7-syllable line | `30.wav` | https://sounds.spriters-resource.com/nintendo_64/heyyoupikachu/asset/396106/ |
| `pikachu/pokepark2_low_groan.wav` | 2.14 | PokePark 2 Wonders Beyond (Pikachu voice) clip 3 - low ~2.3s (heuristic: groan/yawn) | `S_PIKA_VOICE_streamfiles_00003.wav` | https://sounds.spriters-resource.com/wii/pokepark2wondersbeyond/asset/394741/ |
| `pikachu/pokepark2_low_chuckle.wav` | 1.81 | PokePark 2 clip 4 - low 4-syllable (heuristic: chuckle/struggle) | `S_PIKA_VOICE_streamfiles_00004.wav` | https://sounds.spriters-resource.com/wii/pokepark2wondersbeyond/asset/394741/ |
| `pikachu/pokepark2_high_call.wav` | 1.83 | PokePark 2 clip 1 - high bright ~1.8s call | `S_PIKA_VOICE_streamfiles_00001.wav` | https://sounds.spriters-resource.com/wii/pokepark2wondersbeyond/asset/394741/ |
| `pikachu/pokepark2_pikachu_rising.wav` | 1.00 | PokePark 2 clip 13 - high 3-syllable rising "Pikachu?!" | `S_PIKA_VOICE_streamfiles_00013.wav` | https://sounds.spriters-resource.com/wii/pokepark2wondersbeyond/asset/394741/ |
| `pikachu/pokepark2_bright_sustain.wav` | 1.22 | PokePark 2 clip 16 - bright sustained ~1.3s | `S_PIKA_VOICE_streamfiles_00016.wav` | https://sounds.spriters-resource.com/wii/pokepark2wondersbeyond/asset/394741/ |
| `pikachu/pokepark2_pi_surprised.wav` | 0.47 | PokePark 2 clip 18 - short sharply rising (heuristic: surprised "Pi?!") | `S_PIKA_VOICE_streamfiles_00018.wav` | https://sounds.spriters-resource.com/wii/pokepark2wondersbeyond/asset/394741/ |
| `pikachu/pokepark2_pika_question.wav` | 0.49 | PokePark 2 clip 6 - short rising 2-syllable "Pika?" | `S_PIKA_VOICE_streamfiles_00006.wav` | https://sounds.spriters-resource.com/wii/pokepark2wondersbeyond/asset/394741/ |
| `pikachu/pokepark2_pikaa.wav` | 1.36 | PokePark 2 clip 23 - ~1.4s 2-syllable "Pi-kaaa" | `S_PIKA_VOICE_streamfiles_00023.wav` | https://sounds.spriters-resource.com/wii/pokepark2wondersbeyond/asset/394741/ |
| `pikachu/stadium_game_cry.wav` | 1.17 | Pokemon Stadium N64 - in-game Pikachu cry | `#025_Pikachu.wav` | https://sounds.spriters-resource.com/nintendo_64/pokemonstadium/asset/427768/ |
| `pikachu/legacy_gen1_cry.wav` | 0.80 | PokeAPI legacy cry (classic Gen 1-5 style 8-bit-derived cry) | `legacy_pikachu.ogg` | https://raw.githubusercontent.com/PokeAPI/cries/main/cries/pokemon/legacy/25.ogg |

## Sobble (5 files)

| File | Dur (s) | Description | Original file | Source |
|---|---|---|---|---|
| `sobble/swsh_cry_standard.wav` | 0.72 | Sword/Shield standard cry 00_00 | `Play_PV_816_00_00.ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/430099/ |
| `sobble/swsh_variant_01_whimper.wav` | 1.27 | Sword/Shield variant 00_01 - ~1.3s sustained, gently falling (heuristic: whimper) | `Play_PV_816_00_01.ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/430099/ |
| `sobble/swsh_variant_02_falling_whine.wav` | 0.99 | Sword/Shield variant 00_02 - strongly falling pitch (heuristic: sad whine) | `Play_PV_816_00_02.ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/430099/ |
| `sobble/swsh_variant_03_long_sob.wav` | 1.61 | Sword/Shield variant 00_03 - longest ~1.8s sustained (heuristic: closest to crying/sobbing) | `Play_PV_816_00_03.ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/430099/ |
| `sobble/swsh_variant_04_short_rising.wav` | 0.78 | Sword/Shield variant 00_04 - short rising (heuristic: questioning/startled) | `Play_PV_816_00_04.ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/430099/ |

## Charizard (42 files)

| File | Dur (s) | Description | Original file | Source |
|---|---|---|---|---|
| `charizard/sv_happy_01.wav` | 0.63 | Scarlet/Violet "GLAD1" emotion cry - happy/pleased | `PLAY_PV_0006 [PV=GLAD1].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454133/ |
| `charizard/sv_happy_03_big.wav` | 0.80 | Scarlet/Violet "GLAD3" emotion cry - biggest/most excited happy | `PLAY_PV_0006 [PV=GLAD3].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454133/ |
| `charizard/sv_sad.wav` | 1.08 | Scarlet/Violet "SAD" emotion cry - sad/downcast (droopy version of cry) | `PLAY_PV_0006 [PV=SAD].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454133/ |
| `charizard/sv_angry.wav` | 1.83 | Scarlet/Violet "ANGER" emotion cry - angry/annoyed | `PLAY_PV_0006 [PV=ANGER].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454133/ |
| `charizard/sv_cry_pokedex.wav` | 1.04 | Scarlet/Violet "INDEX" Pokedex cry (full standard cry) | `PLAY_PV_0006 [PV=INDEX].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454133/ |
| `charizard/sv_ambient_call.wav` | 0.97 | Scarlet/Violet "ENV" overworld/ambient call (wild idle vocalisation) | `PLAY_PV_0006 [PV=ENV].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454133/ |
| `charizard/sv_short_04.wav` | 0.56 | Scarlet/Violet "EX4" extra clip - medium vocal fragment | `PLAY_PV_0006 [PV=EX4].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454133/ |
| `charizard/sv_special_attack_cry.wav` | 0.49 | Scarlet/Violet "SPATK" special-attack shout | `PLAY_PV_0006 [PV=SPATK].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454133/ |
| `charizard/sv_attack_grunt.wav` | 0.21 | Scarlet/Violet "ATK" short physical-attack grunt | `PLAY_PV_0006 [PV=ATK].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454133/ |
| `charizard/pokken_roar_intro_01.wav` | 2.45 | Pokken Tournament - big battle-intro roar (~3s) | `VC_P006_V000_APPEAR_01.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399930/ |
| `charizard/pokken_roar_intro_02.wav` | 1.44 | Pokken - intro roar, alt (~2s) | `VC_P006_V000_APPEAR_02.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399930/ |
| `charizard/pokken_roar_powerup.wav` | 2.66 | Pokken - mega-evolution/burst power-up roar (~3.2s) | `VC_P006_V000_BURST_ATTACK_START.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399930/ |
| `charizard/pokken_roar_attack_max.wav` | 1.75 | Pokken - full-power attack roar | `VC_P006_V000_ATTACK_MAX_01.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399930/ |
| `charizard/pokken_angry_01.wav` | 0.55 | Pokken - angry growl | `VC_P006_V000_CMN_ANGRY_01.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399930/ |
| `charizard/pokken_angry_02.wav` | 0.83 | Pokken - angry growl, alt | `VC_P006_V000_CMN_ANGRY_02.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399930/ |
| `charizard/pokken_happy_01.wav` | 0.60 | Pokken - happy rumble | `VC_P006_V000_CMN_HAPPY_01.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399930/ |
| `charizard/pokken_happy_02.wav` | 1.37 | Pokken - happy call (~2s) | `VC_P006_V000_CMN_HAPPY_04.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399930/ |
| `charizard/pokken_sad.wav` | 1.68 | Pokken - sad low groan | `VC_P006_V000_CMN_SAD_03.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399930/ |
| `charizard/pokken_laugh_chuff.wav` | 1.12 | Pokken - laugh/chuffing (snort-like) | `VC_P006_V000_LAUGH.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399930/ |
| `charizard/pokken_surprised_snort.wav` | 0.47 | Pokken - surprised huff/snort | `VC_P006_V000_SURPRISE.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399930/ |
| `charizard/pokken_grunt_snort_01.wav` | 0.42 | Pokken - short effort grunt / snort | `VC_P006_V000_KIAI_01.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399930/ |
| `charizard/pokken_grunt_snort_02.wav` | 0.32 | Pokken - short effort grunt / snort, alt | `VC_P006_V000_KIAI_02.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399930/ |
| `charizard/pokken_hurt.wav` | 0.96 | Pokken - hurt roar | `VC_P006_V000_DAMAGE_L_01.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399930/ |
| `charizard/pokken_defeated_long.wav` | 3.53 | Pokken - defeated, long groan (~4s) | `VC_P006_V000_LOSE.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399930/ |
| `charizard/pokken_victory_roar.wav` | 1.00 | Pokken - victory roar | `VC_P006_V000_WIN_01.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399930/ |
| `charizard/pokken_stunned.wav` | 2.00 | Pokken - stunned/dazed groan | `VC_P006_V000_GUARD_CRUSH_01.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399930/ |
| `charizard/smash_sleep_snore_snort.wav` | 3.90 | Smash Ultimate - falling-asleep snoring/snorting (~3.9s, 10 breaths) | `vc_plizardon_furasleep.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409671/ |
| `charizard/smash_drowsy_groan_yawn.wav` | 1.54 | Smash Ultimate - dizzy low groan (closest to a yawn) | `vc_plizardon_furafura.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409671/ |
| `charizard/smash_taunt_roar.wav` | 0.80 | Smash Ultimate - taunt roar | `vc_plizardon_appeal02.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409671/ |
| `charizard/smash_taunt_growl.wav` | 0.74 | Smash Ultimate - taunt growl | `vc_plizardon_appeal01.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409671/ |
| `charizard/smash_victory_rumble.wav` | 1.94 | Smash Ultimate - low victory rumble (~1.9s) | `vc_plizardon_win03.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409671/ |
| `charizard/smash_ko_roar.wav` | 2.89 | Smash Ultimate - KO roar (~3.2s) | `vc_plizardon_knockout.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409671/ |
| `charizard/smash_launched_roar.wav` | 2.42 | Smash Ultimate - long cry when launched | `vc_plizardon_damage_twinkle.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409671/ |
| `charizard/smash_roar_attack.wav` | 0.79 | Smash Ultimate - attack roar | `vc_plizardon_special_s01.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409671/ |
| `charizard/smash_snort_short.wav` | 0.16 | Smash Ultimate - very short grunt/snort | `vc_plizardon_heavyget.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409671/ |
| `charizard/smash_startled.wav` | 1.10 | Smash Ultimate - startled slip roar | `vc_plizardon_missfoot01.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409671/ |
| `charizard/swsh_variant_01.wav` | 1.42 | Sword/Shield alt cry variant 00_01 (camp/emotion vocalisation; exact emotion unlabelled in rip) | `Play_PV_006_00_01.ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/499010/ |
| `charizard/swsh_variant_02.wav` | 1.87 | Sword/Shield alt cry variant 00_02 (camp/emotion vocalisation; exact emotion unlabelled in rip) | `Play_PV_006_00_02.ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/499010/ |
| `charizard/swsh_variant_03.wav` | 0.84 | Sword/Shield alt cry variant 00_03 (camp/emotion vocalisation; exact emotion unlabelled in rip) | `Play_PV_006_00_03.ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/499010/ |
| `charizard/swsh_variant_04.wav` | 0.39 | Sword/Shield alt cry variant 00_04 (camp/emotion vocalisation; exact emotion unlabelled in rip) | `Play_PV_006_00_04.ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/499010/ |
| `charizard/stadium_game_cry.wav` | 1.79 | Pokemon Stadium N64 - in-game cry | `#006_Charizard.wav` | https://sounds.spriters-resource.com/nintendo_64/pokemonstadium/asset/427768/ |
| `charizard/legacy_gen1_cry.wav` | 0.93 | PokeAPI legacy cry (classic Gen 1-5) | `legacy_charizard.ogg` | https://raw.githubusercontent.com/PokeAPI/cries/main/cries/pokemon/legacy/6.ogg |

## Garchomp (28 files)

| File | Dur (s) | Description | Original file | Source |
|---|---|---|---|---|
| `garchomp/sv_happy_01.wav` | 0.62 | Scarlet/Violet "GLAD1" emotion cry - happy/pleased | `PLAY_PV_0445 [PV=GLAD1].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454136/ |
| `garchomp/sv_happy_03_big.wav` | 0.78 | Scarlet/Violet "GLAD3" emotion cry - biggest/most excited happy | `PLAY_PV_0445 [PV=GLAD3].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454136/ |
| `garchomp/sv_sad.wav` | 1.07 | Scarlet/Violet "SAD" emotion cry - sad/downcast (droopy version of cry) | `PLAY_PV_0445 [PV=SAD].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454136/ |
| `garchomp/sv_angry.wav` | 1.10 | Scarlet/Violet "ANGER" emotion cry - angry/annoyed | `PLAY_PV_0445 [PV=ANGER].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454136/ |
| `garchomp/sv_cry_pokedex.wav` | 1.02 | Scarlet/Violet "INDEX" Pokedex cry (full standard cry) | `PLAY_PV_0445 [PV=INDEX].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454136/ |
| `garchomp/sv_ambient_call.wav` | 0.80 | Scarlet/Violet "ENV" overworld/ambient call (wild idle vocalisation) | `PLAY_PV_0445 [PV=ENV].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454136/ |
| `garchomp/sv_short_04.wav` | 0.61 | Scarlet/Violet "EX4" extra clip - medium vocal fragment | `PLAY_PV_0445 [PV=EX4].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454136/ |
| `garchomp/sv_special_attack_cry.wav` | 1.07 | Scarlet/Violet "SPATK" special-attack shout | `PLAY_PV_0445 [PV=SPATK].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454136/ |
| `garchomp/sv_attack_grunt.wav` | 1.07 | Scarlet/Violet "ATK" short physical-attack grunt | `PLAY_PV_0445 [PV=ATK].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454136/ |
| `garchomp/pokken_roar_intro_01.wav` | 2.90 | Pokken Tournament - battle-intro roar (~2.9s) | `VC_P445_V000_APPEAR_01.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399934/ |
| `garchomp/pokken_roar_intro_02.wav` | 1.94 | Pokken - intro roar, alt (~2.5s) | `VC_P445_V000_APPEAR_03.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399934/ |
| `garchomp/pokken_roar_mega.wav` | 1.62 | Pokken - mega-evolution power-up roar | `VC_P445_V000_BURST_ATTACK_START.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399934/ |
| `garchomp/pokken_roar_attack.wav` | 1.21 | Pokken - heavy attack roar | `VC_P445_V000_ATTACK_L_01.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399934/ |
| `garchomp/pokken_roar_attack_max.wav` | 0.94 | Pokken - full-power attack roar | `VC_P445_V000_ATTACK_MAX_01.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399934/ |
| `garchomp/pokken_angry.wav` | 0.93 | Pokken - angry snarl | `VC_P445_V000_CMN_ANGRY_02.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399934/ |
| `garchomp/pokken_happy.wav` | 1.14 | Pokken - happy call | `VC_P445_V000_CMN_HAPPY_04.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399934/ |
| `garchomp/pokken_sad.wav` | 1.43 | Pokken - sad low moan | `VC_P445_V000_CMN_SAD_03.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399934/ |
| `garchomp/pokken_laugh.wav` | 1.22 | Pokken - growly laugh | `VC_P445_V000_LAUGH.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399934/ |
| `garchomp/pokken_surprised.wav` | 0.38 | Pokken - surprised snort | `VC_P445_V000_SURPRISE.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399934/ |
| `garchomp/pokken_hurt.wav` | 1.27 | Pokken - hurt roar | `VC_P445_V000_DAMAGE_L_03.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399934/ |
| `garchomp/pokken_victory_roar.wav` | 3.72 | Pokken - victory roar (~3.7s) | `VC_P445_V000_WIN_01.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399934/ |
| `garchomp/pokken_defeated_long.wav` | 6.61 | Pokken - defeated, long (~6.6s) | `VC_P445_V000_LOSE.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399934/ |
| `garchomp/pokken_stunned.wav` | 1.41 | Pokken - stunned/dazed | `VC_P445_V000_GUARD_CRUSH_01.wav` | https://sounds.spriters-resource.com/wii_u/pokkentournament/asset/399934/ |
| `garchomp/swsh_variant_01.wav` | 0.62 | Sword/Shield alt cry variant 00_01 (camp/emotion vocalisation; emotion unlabelled) | `Play_PV_445_00_01.ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/499004/ |
| `garchomp/swsh_variant_02.wav` | 1.10 | Sword/Shield alt cry variant 00_02 (camp/emotion vocalisation; emotion unlabelled) | `Play_PV_445_00_02.ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/499004/ |
| `garchomp/swsh_variant_03.wav` | 0.66 | Sword/Shield alt cry variant 00_03 (camp/emotion vocalisation; emotion unlabelled) | `Play_PV_445_00_03.ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/499004/ |
| `garchomp/swsh_variant_04.wav` | 0.27 | Sword/Shield alt cry variant 00_04 (camp/emotion vocalisation; emotion unlabelled) | `Play_PV_445_00_04.ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/499004/ |
| `garchomp/legacy_gen4_cry.wav` | 0.94 | PokeAPI legacy cry (DS-era Gen 4) | `legacy_garchomp.ogg` | https://raw.githubusercontent.com/PokeAPI/cries/main/cries/pokemon/legacy/445.ogg |

## Greninja (25 files)

| File | Dur (s) | Description | Original file | Source |
|---|---|---|---|---|
| `greninja/sv_happy_01.wav` | 0.74 | Scarlet/Violet "GLAD1" emotion cry - happy/pleased | `PLAY_PV_0658 [PV=GLAD1].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454138/ |
| `greninja/sv_happy_02.wav` | 0.73 | Scarlet/Violet "GLAD2" emotion cry - happy, alt take | `PLAY_PV_0658 [PV=GLAD2].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454138/ |
| `greninja/sv_happy_03_big.wav` | 0.96 | Scarlet/Violet "GLAD3" emotion cry - biggest/most excited happy | `PLAY_PV_0658 [PV=GLAD3].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454138/ |
| `greninja/sv_sad.wav` | 1.29 | Scarlet/Violet "SAD" emotion cry - sad/downcast (droopy version of cry) | `PLAY_PV_0658 [PV=SAD].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454138/ |
| `greninja/sv_angry.wav` | 0.90 | Scarlet/Violet "ANGER" emotion cry - angry/annoyed | `PLAY_PV_0658 [PV=ANGER].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454138/ |
| `greninja/sv_cry_pokedex.wav` | 1.19 | Scarlet/Violet "INDEX" Pokedex cry (full standard cry) | `PLAY_PV_0658 [PV=INDEX].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454138/ |
| `greninja/sv_ambient_call.wav` | 0.94 | Scarlet/Violet "ENV" overworld/ambient call (wild idle vocalisation) | `PLAY_PV_0658 [PV=ENV].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454138/ |
| `greninja/sv_short_04.wav` | 0.67 | Scarlet/Violet "EX4" extra clip - medium vocal fragment | `PLAY_PV_0658 [PV=EX4].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454138/ |
| `greninja/sv_special_attack_cry.wav` | 1.29 | Scarlet/Violet "SPATK" special-attack shout | `PLAY_PV_0658 [PV=SPATK].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454138/ |
| `greninja/sv_attack_grunt.wav` | 1.27 | Scarlet/Violet "ATK" short physical-attack grunt | `PLAY_PV_0658 [PV=ATK].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454138/ |
| `greninja/smash_taunt_01.wav` | 0.45 | Smash Ultimate (English voice) - taunt call | `vc_gekkouga_appeal01.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409636/ |
| `greninja/smash_taunt_02.wav` | 0.48 | Smash Ultimate - taunt call, alt | `vc_gekkouga_appeal03.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409636/ |
| `greninja/smash_victory_01.wav` | 3.10 | Smash Ultimate - victory "Greninja"-style call (~2s) | `vc_gekkouga_win01.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409636/ |
| `greninja/smash_victory_02.wav` | 1.92 | Smash Ultimate - victory line, alt | `vc_gekkouga_win02.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409636/ |
| `greninja/smash_final_smash_long.wav` | 4.04 | Smash Ultimate - final smash long cry (~3.5s) | `vc_gekkouga_final02.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409636/ |
| `greninja/smash_final_smash_shout.wav` | 0.83 | Smash Ultimate - final smash shout | `vc_gekkouga_final03.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409636/ |
| `greninja/smash_ko_cry.wav` | 2.31 | Smash Ultimate - KO cry | `vc_gekkouga_knockout.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409636/ |
| `greninja/smash_launched_cry.wav` | 2.02 | Smash Ultimate - long cry when launched | `vc_gekkouga_damage_twinkle.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409636/ |
| `greninja/smash_dizzy.wav` | 1.76 | Smash Ultimate - dazed/dizzy | `vc_gekkouga_furafura.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409636/ |
| `greninja/smash_sleepy.wav` | 1.85 | Smash Ultimate - falling asleep (sleepy murmur) | `vc_gekkouga_furasleep.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409636/ |
| `greninja/smash_whoa.wav` | 0.54 | Smash Ultimate - "whoa" teetering on ledge | `vc_gekkouga_ottotto.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409636/ |
| `greninja/smash_attack_shout.wav` | 0.54 | Smash Ultimate - attack shout | `vc_gekkouga_attack07.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409636/ |
| `greninja/smash_attack_hup.wav` | 0.21 | Smash Ultimate - short "hup!" attack grunt | `vc_gekkouga_attack01.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409636/ |
| `greninja/smash_hurt.wav` | 0.38 | Smash Ultimate - hurt | `vc_gekkouga_damage02.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409636/ |
| `greninja/smash_slip_yelp.wav` | 0.83 | Smash Ultimate - slip yelp (surprised) | `vc_gekkouga_missfoot02.wav` | https://sounds.spriters-resource.com/nintendo_switch/supersmashbrosultimate/asset/409636/ |

## Dragonite (17 files)

| File | Dur (s) | Description | Original file | Source |
|---|---|---|---|---|
| `dragonite/sv_happy_01.wav` | 0.67 | Scarlet/Violet "GLAD1" emotion cry - happy/pleased | `PLAY_PV_0149 [PV=GLAD1].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454133/ |
| `dragonite/sv_happy_02.wav` | 0.66 | Scarlet/Violet "GLAD2" emotion cry - happy, alt take | `PLAY_PV_0149 [PV=GLAD2].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454133/ |
| `dragonite/sv_happy_03_big.wav` | 0.85 | Scarlet/Violet "GLAD3" emotion cry - biggest/most excited happy | `PLAY_PV_0149 [PV=GLAD3].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454133/ |
| `dragonite/sv_sad.wav` | 1.10 | Scarlet/Violet "SAD" emotion cry - sad/downcast (droopy version of cry) | `PLAY_PV_0149 [PV=SAD].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454133/ |
| `dragonite/sv_angry.wav` | 0.63 | Scarlet/Violet "ANGER" emotion cry - angry/annoyed | `PLAY_PV_0149 [PV=ANGER].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454133/ |
| `dragonite/sv_cry_pokedex.wav` | 1.10 | Scarlet/Violet "INDEX" Pokedex cry (full standard cry) | `PLAY_PV_0149 [PV=INDEX].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454133/ |
| `dragonite/sv_ambient_call.wav` | 1.02 | Scarlet/Violet "ENV" overworld/ambient call (wild idle vocalisation) | `PLAY_PV_0149 [PV=ENV].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454133/ |
| `dragonite/sv_short_04.wav` | 0.58 | Scarlet/Violet "EX4" extra clip - medium vocal fragment | `PLAY_PV_0149 [PV=EX4].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454133/ |
| `dragonite/sv_special_attack_cry.wav` | 0.49 | Scarlet/Violet "SPATK" special-attack shout | `PLAY_PV_0149 [PV=SPATK].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454133/ |
| `dragonite/swsh_variant_01.wav` | 0.96 | Sword/Shield alt cry variant 00_01 (camp/emotion vocalisation; emotion unlabelled) | `Play_PV_149_00_01.ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/499010/ |
| `dragonite/swsh_variant_02.wav` | 0.63 | Sword/Shield alt cry variant 00_02 (camp/emotion vocalisation; emotion unlabelled) | `Play_PV_149_00_02.ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/499010/ |
| `dragonite/swsh_variant_03.wav` | 1.14 | Sword/Shield alt cry variant 00_03 (camp/emotion vocalisation; emotion unlabelled) | `Play_PV_149_00_03.ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/499010/ |
| `dragonite/swsh_variant_04.wav` | 0.35 | Sword/Shield alt cry variant 00_04 (camp/emotion vocalisation; emotion unlabelled) | `Play_PV_149_00_04.ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/499010/ |
| `dragonite/snap_call_01.wav` | 1.32 | Pokemon Snap (N64) - Dragonite call | `dragonite.wav` | https://sounds.spriters-resource.com/nintendo_64/pokemonsnap/asset/395212/ |
| `dragonite/snap_call_02.wav` | 0.43 | Pokemon Snap (N64) - Dragonite call, alt | `dragonite2.wav` | https://sounds.spriters-resource.com/nintendo_64/pokemonsnap/asset/395212/ |
| `dragonite/stadium_game_cry.wav` | 1.42 | Pokemon Stadium N64 - in-game cry | `#149_Dragonite.wav` | https://sounds.spriters-resource.com/nintendo_64/pokemonstadium/asset/427768/ |
| `dragonite/legacy_gen1_cry.wav` | 0.90 | PokeAPI legacy cry (classic Gen 1-5) | `legacy_dragonite.ogg` | https://raw.githubusercontent.com/PokeAPI/cries/main/cries/pokemon/legacy/149.ogg |

## Piplup (14 files)

| File | Dur (s) | Description | Original file | Source |
|---|---|---|---|---|
| `piplup/sv_happy_01.wav` | 0.39 | Scarlet/Violet "GLAD1" emotion cry - happy/pleased | `PLAY_PV_0393 [PV=GLAD1].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454136/ |
| `piplup/sv_happy_02.wav` | 0.39 | Scarlet/Violet "GLAD2" emotion cry - happy, alt take | `PLAY_PV_0393 [PV=GLAD2].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454136/ |
| `piplup/sv_happy_03_big.wav` | 0.51 | Scarlet/Violet "GLAD3" emotion cry - biggest/most excited happy | `PLAY_PV_0393 [PV=GLAD3].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454136/ |
| `piplup/sv_sad.wav` | 0.72 | Scarlet/Violet "SAD" emotion cry - sad/downcast (droopy version of cry) | `PLAY_PV_0393 [PV=SAD].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454136/ |
| `piplup/sv_angry.wav` | 1.00 | Scarlet/Violet "ANGER" emotion cry - angry/annoyed | `PLAY_PV_0393 [PV=ANGER].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454136/ |
| `piplup/sv_cry_pokedex.wav` | 0.64 | Scarlet/Violet "INDEX" Pokedex cry (full standard cry) | `PLAY_PV_0393 [PV=INDEX].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454136/ |
| `piplup/sv_ambient_call.wav` | 0.51 | Scarlet/Violet "ENV" overworld/ambient call (wild idle vocalisation) | `PLAY_PV_0393 [PV=ENV].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454136/ |
| `piplup/sv_short_01.wav` | 0.33 | Scarlet/Violet "EX1" extra clip - very short chirp/blip | `PLAY_PV_0393 [PV=EX1].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454136/ |
| `piplup/sv_short_02.wav` | 0.36 | Scarlet/Violet "EX2" extra clip - short vocal fragment | `PLAY_PV_0393 [PV=EX2].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454136/ |
| `piplup/sv_short_03.wav` | 0.40 | Scarlet/Violet "EX3" extra clip - short vocal fragment | `PLAY_PV_0393 [PV=EX3].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454136/ |
| `piplup/sv_short_04.wav` | 0.49 | Scarlet/Violet "EX4" extra clip - medium vocal fragment | `PLAY_PV_0393 [PV=EX4].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454136/ |
| `piplup/sv_attack_grunt.wav` | 0.60 | Scarlet/Violet "ATK" short physical-attack grunt | `PLAY_PV_0393 [PV=ATK].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454136/ |
| `piplup/sv_special_attack_cry.wav` | 0.71 | Scarlet/Violet "SPATK" special-attack shout | `PLAY_PV_0393 [PV=SPATK].wav` | https://sounds.spriters-resource.com/nintendo_switch/pokemonscarletviolet/asset/454136/ |
| `piplup/legacy_gen4_cry.wav` | 0.61 | PokeAPI legacy cry (DS-era Gen 4) | `legacy_piplup.ogg` | https://raw.githubusercontent.com/PokeAPI/cries/main/cries/pokemon/legacy/393.ogg |

## Raboot (5 files)

| File | Dur (s) | Description | Original file | Source |
|---|---|---|---|---|
| `raboot/swsh_cry_standard.wav` | 0.80 | Sword/Shield standard cry 00_00 | `Play_PV_814_00_00.ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/430099/ |
| `raboot/swsh_variant_01.wav` | 0.83 | Sword/Shield alt cry variant 00_01 (camp/emotion vocalisation; emotion unlabelled) | `Play_PV_814_00_01.ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/430099/ |
| `raboot/swsh_variant_02.wav` | 0.85 | Sword/Shield alt cry variant 00_02 (camp/emotion vocalisation; emotion unlabelled) | `Play_PV_814_00_02.ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/430099/ |
| `raboot/swsh_variant_03.wav` | 0.92 | Sword/Shield alt cry variant 00_03 (camp/emotion vocalisation; emotion unlabelled) | `Play_PV_814_00_03.ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/430099/ |
| `raboot/swsh_variant_04.wav` | 0.58 | Sword/Shield alt cry variant 00_04 (camp/emotion vocalisation; emotion unlabelled) | `Play_PV_814_00_04.ogg` | https://sounds.spriters-resource.com/nintendo_switch/pokemonswordshield/asset/430099/ |
