import re,sys,collections,statistics,os
HIT=re.compile(r'^\[.*?\] You (\w+) (.+?) for ([\d,]+) points? of damage\.(.*)$')
SPL=re.compile(r'^\[.*?\] You (?:hit )?(.+?) for ([\d,]+) points? of (\w+) damage by (.+?)\.(.*)$')
def run(fn):
    norm=collections.defaultdict(list); crit=collections.defaultdict(list)
    for ln in open(fn,errors='replace'):
        m=SPL.match(ln)
        if m and ' damage by ' in ln:
            (crit if 'Critical' in m.group(5) else norm)['spell:'+m.group(4)].append(int(m.group(2).replace(',',''))); continue
        m=HIT.match(ln)
        if m:
            (crit if 'Critical' in m.group(4) else norm)[m.group(1)].append(int(m.group(3).replace(',','')))
    print(f"\n##### {os.path.basename(fn)}")
    print(f"{'channel':<26} {'n':>4} {'min':>5} {'max':>6} {'mean':>7} {'med':>6} | {'ncrit':>5} {'cmin':>5} {'cmax':>6} {'cmean':>7} | {'crit x':>6} {'max/min':>7}")
    for k in sorted(set(norm)|set(crit), key=lambda x:-(sum(norm.get(x,[]))+sum(crit.get(x,[])))):
        a=norm.get(k,[]); b=crit.get(k,[])
        if len(a)<4: continue
        cm=(statistics.mean(b)/statistics.mean(a)) if b else 0
        print(f"{k[:26]:<26} {len(a):>4} {min(a):>5} {max(a):>6} {statistics.mean(a):>7.1f} {statistics.median(a):>6.0f} | "
              f"{len(b):>5} {(min(b) if b else 0):>5} {(max(b) if b else 0):>6} {(statistics.mean(b) if b else 0):>7.1f} | {cm:>6.2f} {max(a)/min(a):>7.2f}")
for f in sys.argv[1:]: run(f)
