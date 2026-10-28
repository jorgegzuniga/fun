# FireRed Open World patch

`FireRed_Rev1_OpenWorld.ips` applies to **Pokémon FireRed (USA/Europe) Rev 1**
(SHA-1 `dd5945db9b930750cb39d00c84da8571feebf417`). Apply it with any IPS patcher
(Lunar IPS, Floating IPS, or an emulator's soft-patching) and start a **new game**.

What it changes:
- New game starts with Bicycle, Poké Flute, Silph Scope, Secret Key and HM01–HM07.
- HM field moves no longer require badges (overworld and party menu).
- Story roadblocks removed: Viridian old man, Pewter gym guide, Cerulean exit
  blockers, Vermilion ticket check, Saffron gate guards, Cycling Road gates,
  Snorlax (flute), Pokémon Tower ghosts (scope), Silph Co. door guard,
  Viridian/Cinnabar gym locks, Cerulean Cave guard.
- Kept: Route 22/23 badge gates to the Pokémon League; Sevii Islands progression.

`patch_openworld.py` regenerates the ROM and IPS (`python3 patch_openworld.py IN.gba OUT.gba OUT.ips`).
It reads constants and map data from a pret/pokefirered checkout; set `DECOMP` and `ROMPATH` in `consts.py`.
