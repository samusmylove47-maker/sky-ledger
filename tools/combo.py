import os,re,json,sys,collections,datetime,statistics
SPELLS=json.load(open(os.environ['SPELLS']))['spells']
ABBR={'Warrior':'WAR','Paladin':'PAL','Shadow Knight':'SHD','Ranger':'RNG','Monk':'MNK','Rogue':'ROG',
      'Berserker':'BER','Bard':'BRD','Beastlord':'BST','Cleric':'CLR','Druid':'DRU','Shaman':'SHM',
      'Enchanter':'ENC','Magician':'MAG','Necromancer':'NEC','Wizard':'WIZ'}
S2C={}
for s in SPELLS:
    cs={ab for full,ab in ABBR.items() if re.search(r'\*\s*'+re.escape(full)+r'\s*-\s*Level', s.get('classes') or '')}
    if cs: S2C.setdefault(s['name'],set()).update(cs)
TS=re.compile(r'^\[(\w{3}) (\w{3}) +(\d+) (\d+):(\d+):(\d+) (\d+)\] (.*)$')
MON={m:i+1 for i,m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split())}
CAST=re.compile(r'^You begin casting (.+?)\.')
BYSP=re.compile(r'^You (?:hit )?(.+?) for ([\d,]+) points? of (\w+) damage by (.+?)\.')
DOT=re.compile(r'^(.+?) has taken ([\d,]+) damage from your (.+?)\.')
VRB=re.compile(r'^You (\w+) (.+?) for ([\d,]+) points? of damage\.')
def run(fn):
    ev=[]; excl=collections.Counter(); verbs=collections.Counter(); chan=collections.Counter()
    for ln in open(fn,errors='replace'):
        m=TS.match(ln.rstrip('\n'))
        if not m: continue
        t=datetime.datetime(int(m.group(7)),MON[m.group(2)],int(m.group(3)),int(m.group(4)),int(m.group(5)),int(m.group(6)))
        x=m.group(8); d=0; nm=None
        a=BYSP.match(x)
        if a and ' damage by ' in x: d=int(a.group(2).replace(',','')); nm=a.group(4); chan['proc/nuke']+=d
        else:
            a=DOT.match(x)
            if a: d=int(a.group(2).replace(',','')); nm=a.group(3); chan['dot']+=d
            else:
                a=VRB.match(x)
                if a:
                    d=int(a.group(3).replace(',','')); verbs[a.group(1)]+=1
                    chan['melee' if a.group(1) in ('slash','crush','pierce','hit','punch','bite','maul','slice') else 'autoskill']+=d
                else:
                    a=CAST.match(x)
                    if a: nm=a.group(1)
        if nm:
            base=re.sub(r'\s+(I|II|III|IV|V|VI|VII|VIII|IX|X)$','',nm).strip()
            for c in (nm,base):
                if c in S2C and len(S2C[c])==1: excl[list(S2C[c])[0]]+=1; break
        if d: ev.append((t,d))
    if verbs.get('strike',0)>3: excl['MNK']+=99
    if verbs.get('backstab',0)>0: excl['ROG']+=99
    if verbs.get('frenzy',0)>0: excl['BER']+=99
    if not ev or len(ev)<40: return None
    segs=[]; cur=[ev[0]]
    for e in ev[1:]:
        if (e[0]-cur[-1][0]).total_seconds()>6: segs.append(cur); cur=[e]
        else: cur.append(e)
    segs.append(cur)
    eng=sum(max((s[-1][0]-s[0][0]).total_seconds(),1) for s in segs)
    tot=sum(d for _,d in ev)
    return tot/eng, tot, eng, excl, chan
out=[]
for fn in sys.argv[1:]:
    r=run(fn)
    if r: out.append((r[0],os.path.basename(fn),r[3],r[4],r[2]))
out.sort(reverse=True)
print(f"{'engDPS':>7}  {'secs':>5}  {'classes seen (exclusive)':<34} {'channel mix':<48} log")
for dps,fn,excl,chan,eng in out[:22]:
    tot=sum(chan.values()) or 1
    mix=' '.join(f"{k}{v/tot*100:.0f}%" for k,v in chan.most_common())
    print(f"{dps:>7.1f}  {eng:>5.0f}  {'+'.join(sorted(excl)) or '?':<34} {mix:<48} {fn[:30]}")
