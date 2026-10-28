import re, os
DECOMP = '/tmp/claude-0/-home-user-fun/5a225ad3-5633-5822-aa80-c6725109e428/scratchpad/work/pokefirered'
ROMPATH = '/root/.claude/uploads/5a225ad3-5633-5822-aa80-c6725109e428/bd6c61e8-Pokemon_-_FireRed_Version_USA_Europe_Rev_1.gba'
_raw = {}
for h in ['opponents.h','global.h','flags.h','vars.h','items.h','species.h','moves.h','maps.h','map_groups.h','field_effects.h']:
    p = os.path.join(DECOMP,'include/constants',h)
    if not os.path.exists(p): continue
    for line in open(p):
        m = re.match(r'\s*#define\s+(\w+)\s+(.+?)\s*(//.*)?$', line)
        if m: _raw[m.group(1)] = m.group(2)
_cache = {}
def C(name):
    if name in _cache: return _cache[name]
    expr = _raw[name]
    expr = re.sub(r'/\*.*?\*/','',expr)
    def rep(mm):
        t = mm.group(0)
        if t in _raw: return str(C(t))
        return t
    e = re.sub(r'\b[A-Za-z_]\w*\b', rep, expr)
    v = eval(e, {'__builtins__':{}})
    _cache[name] = v
    return v
