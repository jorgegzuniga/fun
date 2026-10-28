"""Open-world patch for Pokemon FireRed (USA, Rev 1). Usage: patch_openworld.py IN.gba OUT.gba OUT.ips"""
import sys, os, struct, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from consts import C
src, dst, ips_out = sys.argv[1:4]
orig = open(src, 'rb').read()
assert hashlib.sha1(orig).hexdigest() == 'dd5945db9b930750cb39d00c84da8571feebf417', 'expected FireRed USA Rev 1'
rom = bytearray(orig)
GBA = 0x08000000
ALWAYS = C('FLAG_SYS_POKEMON_GET')  # set as soon as the starter is received

def patch(off, old, new, why):
    assert rom[off:off+len(old)] == old, f'{why}: unexpected bytes at {off:#x}: {rom[off:off+len(old)].hex()}'
    rom[off:off+len(new)] = new
def le16(v): return struct.pack('<H', v)
def le32(v): return struct.pack('<I', v)
def retarget_flag(off, flag, why):
    """Change the flag a `checkflag` (0x2B) command tests to one that is always set."""
    patch(off, b'\x2b' + le16(C(flag)), b'\x2b' + le16(ALWAYS), why)

# --- 1. New-game hook: extra flags/vars/items, then fall through to EventScript_ResetAllMapFlags
RESET_ALL_MAP_FLAGS = 0x1A64F9
HOOK = 0xF00000
assert all(b == 0xFF for b in rom[HOOK:HOOK+0x400])
s = bytearray()
def setvar(var, val): s.extend(b'\x16' + le16(C(var)) + le16(val))
def setflag(flag): s.extend(b'\x29' + le16(C(flag)))
def additem(item, n=1): s.extend(b'\x44' + le16(C(item)) + le16(n))
setvar('VAR_MAP_SCENE_VIRIDIAN_CITY_OLD_MAN', 1)          # old man no longer lies across the road
setvar('VAR_MAP_SCENE_VIRIDIAN_CITY_GYM_DOOR', 1)         # Viridian Gym unlocked
setvar('VAR_MAP_SCENE_ROUTE5_ROUTE6_ROUTE7_ROUTE8_GATES', 1)  # Saffron gate guards already got their drink
setflag('FLAG_GOT_BICYCLE'); additem('ITEM_BICYCLE')       # Cycling Road gates open
setflag('FLAG_GOT_POKE_FLUTE'); additem('ITEM_POKE_FLUTE')  # Snorlax can be woken
additem('ITEM_SILPH_SCOPE')                               # Pokemon Tower ghosts
setflag('FLAG_HIDE_POKEMON_MANSION_B1F_SECRET_KEY'); additem('ITEM_SECRET_KEY')  # Cinnabar Gym unlocked
setflag('FLAG_HIDE_CERULEAN_CAVE_GUARD')                  # Cerulean Cave open
for i in range(1, 8): additem(f'ITEM_HM0{i}')
s.extend(b'\x05' + le32(GBA + RESET_ALL_MAP_FLAGS))       # goto original script (ends with `end`)
rom[HOOK:HOOK+len(s)] = s
patch(0x054B80, le32(GBA + RESET_ALL_MAP_FLAGS), le32(GBA + HOOK), 'NewGameInitData script pointer')

# --- 2. HM field moves no longer need badges
retarget_flag(0x1BDF95, 'FLAG_BADGE02_GET', 'Cut tree script')
retarget_flag(0x1BE08E, 'FLAG_BADGE06_GET', 'Rock Smash script')
retarget_flag(0x1BE19F, 'FLAG_BADGE04_GET', 'Strength boulder script')
patch(0x06D5B0, le32(C('FLAG_BADGE05_GET')), le32(ALWAYS), 'Surf badge check (GetInteractedWaterScript)')
patch(0x06D5E4, le32(C('FLAG_BADGE07_GET')), le32(ALWAYS), 'Waterfall badge check (GetInteractedWaterScript)')
# CursorCB_FieldMove: `cmp r4,#6; bhi skip` -> `cmp r4,#6; b skip` (never show "can't use until new badge")
patch(0x124694, bytes.fromhex('062c1bd8'), bytes.fromhex('062c1be0'), 'party menu badge check')

# --- 3. Story roadblocks
# Pewter: gym guide no longer drags you to Brock when leaving east (only the var==0 triggers)
import rom as R  # read-only map table lookup
pc = R.map_events('PewterCity')['coords']
for i in range(4):
    c = pc + 16 * i
    assert rom[c+6:c+10] == le16(C('VAR_MAP_SCENE_PEWTER_CITY')) + le16(0), 'Pewter trigger sanity'
    patch(c, rom[c:c+2], le16(0xFFFF), 'Pewter gym guide trigger')  # x = 0xFFFF: unreachable
# Cerulean: policeman / Slowbro no longer block exits before Bill gives the S.S. Ticket
retarget_flag(0x1664F2, 'FLAG_GOT_SS_TICKET', 'Cerulean exit blockers')
# Vermilion: harbor sailor lets you board the S.S. Anne without a ticket
retarget_flag(0x166C3E, 'FLAG_GOT_SS_TICKET', 'Vermilion ticket check')
# Saffron: Silph Co. door guard stands aside before Mr. Fuji is rescued
retarget_flag(0x1673E0, 'FLAG_RESCUED_MR_FUJI', 'Saffron Silph door guard position')
retarget_flag(0x167432, 'FLAG_RESCUED_MR_FUJI', 'Saffron Silph door guard dialogue')
# Oak's Lab: delivering the parcel no longer resets the Viridian old man (avoids repeating his tutorial)
patch(0x1698AC, b'\x16' + le16(C('VAR_MAP_SCENE_VIRIDIAN_CITY_OLD_MAN')) + le16(1), b'\x00' * 5, 'parcel old-man reset')

open(dst, 'wb').write(rom)

# --- IPS patch
assert len(rom) == len(orig)
recs = []; i = 0
while i < len(rom):
    if rom[i] != orig[i]:
        j = i
        while j < len(rom) and j - i < 0xFFFF and (rom[j] != orig[j] or (j + 1 < len(rom) and rom[j+1] != orig[j+1])):
            j += 1
        recs.append((i, bytes(rom[i:j]))); i = j
    else:
        i += 1
out = bytearray(b'PATCH')
for o, d in recs:
    if o == 0x454F46: o -= 1; d = bytes([orig[o]]) + d
    assert o < 0x1000000
    out += o.to_bytes(3, 'big') + len(d).to_bytes(2, 'big') + d
out += b'EOF'
open(ips_out, 'wb').write(out)
print(f'{len(recs)} IPS records; hook script {len(s)} bytes; sha1 {hashlib.sha1(rom).hexdigest()}')
