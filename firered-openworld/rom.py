import struct, json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from consts import C, DECOMP, ROMPATH
rom = bytearray(open(ROMPATH,'rb').read())
def u8(o): return rom[o]
def u16(o): return struct.unpack_from('<H',rom,o)[0]
def u32(o): return struct.unpack_from('<I',rom,o)[0]
def isptr(v): return 0x08000000 <= v < 0x09000000
def off(v): return v - 0x08000000
def find_all(b, align=1):
    res=[]; i=rom.find(b)
    while i!=-1:
        if i%align==0: res.append(i)
        i=rom.find(b,i+1)
    return res
def plausible_header(o):
    if o+28>len(rom): return False
    a,b,c,d = struct.unpack_from('<IIII',rom,o)
    return isptr(a) and isptr(b) and isptr(c) and (d==0 or isptr(d))
def find_map_groups():
    groups = json.load(open(os.path.join(DECOMP,'data/maps/map_groups.json')))
    order = groups['group_order']
    n = len(order)
    for o in range(0, len(rom)-4*n, 4):
        ok=True
        for g in range(n):
            p=u32(o+4*g)
            if not isptr(p): ok=False;break
            q=u32(off(p))
            if not isptr(q) or not plausible_header(off(q)): ok=False;break
        if ok: return o, order, groups
    return None
_mg=None
def maps():
    """dict name->header offset"""
    global _mg
    if _mg: return _mg
    o, order, groups = find_map_groups()
    res={}
    for gi,g in enumerate(order):
        tbl=off(u32(o+4*gi))
        for mi,mname in enumerate(groups[g]):
            res[mname]=(off(u32(tbl+4*mi)), gi, mi)
    _mg=res
    return res
def map_events(name):
    h,_,_=maps()[name]
    ev=off(u32(h+4))
    nobj,nwarp,ncoord,nbg=rom[ev:ev+4]
    objs=off(u32(ev+4)) if nobj else None
    coords=off(u32(ev+12)) if ncoord else None
    return dict(hdr=h,ev=ev,nobj=nobj,objs=objs,ncoord=ncoord,coords=coords,nbg=nbg,bgs=off(u32(ev+16)) if nbg else None, nwarp=nwarp, warps=off(u32(ev+8)) if nwarp else None, scripts=off(u32(h+8)))
def map_json(name):
    return json.load(open(os.path.join(DECOMP,'data/maps',name,'map.json')))
