# PARSER-ROLE: NOT-THE-ENGINE  the engine is gapengine.py
# This file builds its own damage-line pattern for a local purpose and is NOT
# authoritative. Enforced by check_oneengine.py.
import re,sys,datetime,os,collections
TS=re.compile(r'^\[(\w{3}) (\w{3}) +(\d+) (\d+):(\d+):(\d+) (\d+)\] (.*)$')
MON={m:i+1 for i,m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split())}
HIT=re.compile(r'^You (\w+) (.+?) for ([\d,]+) points? of damage\.')
SPL=re.compile(r'^You (?:hit )?(.+?) for ([\d,]+) points? of (\w+) damage by (.+?)\.')
DOT=re.compile(r'^(.+?) has taken ([\d,]+) damage from your (.+?)\.')
def run(fn,gap=6):
    ev=[]
    for ln in open(fn,errors='replace'):
        m=TS.match(ln.rstrip('\n'))
        if not m: continue
        t=datetime.datetime(int(m.group(7)),MON[m.group(2)],int(m.group(3)),int(m.group(4)),int(m.group(5)),int(m.group(6)))
        x=m.group(8); d=0
        a=SPL.match(x)
        if a and ' damage by ' in x: d=int(a.group(2).replace(',',''))
        else:
            a=HIT.match(x)
            if a: d=int(a.group(3).replace(',',''))
            else:
                a=DOT.match(x)
                if a: d=int(a.group(2).replace(',',''))
        if d: ev.append((t,d))
    if not ev: return
    # segment into engaged windows separated by > gap seconds of no damage
    segs=[]; cur=[ev[0]]
    for e in ev[1:]:
        if (e[0]-cur[-1][0]).total_seconds()>gap: segs.append(cur); cur=[e]
        else: cur.append(e)
    segs.append(cur)
    eng=sum(max((s[-1][0]-s[0][0]).total_seconds(),1) for s in segs)
    tot=sum(d for _,d in ev)
    wall=(ev[-1][0]-ev[0][0]).total_seconds()
    # best 60s rolling window
    best=0
    for i,(t0,_) in enumerate(ev):
        s=0
        for t,d in ev[i:]:
            if (t-t0).total_seconds()>60: break
            s+=d
        best=max(best,s)
    best30=0
    for i,(t0,_) in enumerate(ev):
        s=0
        for t,d in ev[i:]:
            if (t-t0).total_seconds()>30: break
            s+=d
        best30=max(best30,s)
    print(f"{os.path.basename(fn)[:38]:<38} wall {wall:>5.0f}s {tot/wall:>6.1f} | engaged {eng:>5.0f}s ({len(segs):>3} seg) {tot/eng:>6.1f} | best60 {best/60:>6.1f} | best30 {best30/30:>6.1f}")
print(f"{'log':<38} {'wall dps':>19} | {'engaged dps':>28} | {'peak60':>13} | {'peak30':>13}")
for f in sys.argv[1:]: run(f)
