# PARSER-ROLE: NOT-THE-ENGINE  the engine is gapengine.py
# The engine declares ENGINE in its own header. THIS FILE IS THE ONE SESSION C MISTOOK FOR IT
# on 3 Sep -- C's words: "48 lines with no docstring", four regexes read in a minute, and a `dot` label that does not occur
# in the engine at all. C published a defect from it and withdrew it a day
# later. Kept, not deleted: its HIT pattern leaves the trailing parenthetical OPEN and
# it has a DoT branch -- both places where this throwaway is RIGHT and the hardened
# engine is not. An exploratory script written before the shape was decided is open
# where a shipped one has narrowed. See HANDOFF.md section 92.
import re,sys,collections,datetime,glob,os
TS=re.compile(r'^\[(\w{3}) (\w{3}) +(\d+) (\d+):(\d+):(\d+) (\d+)\] (.*)$')
MON={m:i+1 for i,m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split())}
# "You <verb> <target> for N points of damage.[ (Critical)]"
HIT=re.compile(r'^You (\w+) (.+?) for ([\d,]+) points? of damage\.(.*)$')
# "You hit <t> for N points of <type> damage by <Spell>."
SPL=re.compile(r'^You (?:hit )?(.+?) for ([\d,]+) points? of (\w+) damage by (.+?)\.(.*)$')
# "<t> has taken N damage from your <Spell>."
DOT=re.compile(r'^(.+?) has taken ([\d,]+) damage from your (.+?)\.(.*)$')
MISS=re.compile(r'^You try to (\w+) (.+?), but (miss|.+?)!')
def parse(fn):
    rows=[]
    for ln in open(fn,errors='replace'):
        m=TS.match(ln.rstrip('\n'))
        if not m: continue
        t=datetime.datetime(int(m.group(7)),MON[m.group(2)],int(m.group(3)),int(m.group(4)),int(m.group(5)),int(m.group(6)))
        rows.append((t,m.group(8)))
    return rows
def analyse(fn):
    rows=parse(fn)
    if not rows: return None
    ev=[]
    verbs=collections.Counter(); miss=collections.Counter()
    for t,x in rows:
        m=SPL.match(x)
        if m and 'points of' in x and ' damage by ' in x:
            ev.append((t,'spell:'+m.group(4),int(m.group(2).replace(',','')),'Critical' in m.group(5))); continue
        m=HIT.match(x)
        if m:
            ev.append((t,'melee:'+m.group(1),int(m.group(3).replace(',','')),'Critical' in m.group(4))); verbs[m.group(1)]+=1; continue
        m=DOT.match(x)
        if m: ev.append((t,'dot:'+m.group(3),int(m.group(2).replace(',','')),False)); continue
        m=MISS.match(x)
        if m: miss[m.group(3)]+=1
    if not ev: return None
    lo=min(e[0] for e in ev); hi=max(e[0] for e in ev)
    span=(hi-lo).total_seconds() or 1
    tot=sum(e[2] for e in ev)
    print(f"\n===== {os.path.basename(fn)}   span {span:.0f}s   events {len(ev)}   total {tot:,}   RAW DPS {tot/span:.1f}")
    print(f"      misses/avoids: {dict(miss)}")
    byc=collections.defaultdict(lambda:[0,0,0])  # n, dmg, crits
    for t,c,d,cr in ev:
        b=byc[c]; b[0]+=1; b[1]+=d; b[2]+=cr
    for c,(n,d,cr) in sorted(byc.items(),key=lambda x:-x[1][1]):
        print(f"      {c[:34]:<34} n={n:>4}  dmg={d:>8,}  {d/span:>7.1f} DPS  avg {d/n:>6.1f}  crit {cr/n*100:>5.1f}%")
    return span,tot,ev
for fn in sys.argv[1:]:
    analyse(fn)
