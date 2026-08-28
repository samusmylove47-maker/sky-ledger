import re,sys,collections,os
HIT=re.compile(r'^\[.*?\] You (\w+) (.+?) for ([\d,]+) points? of damage\.')
MISS=re.compile(r'^\[.*?\] You try to (\w+) (.+?), but (.+?)!')
tot=collections.Counter()
for fn in sys.argv[1:]:
    for ln in open(fn,errors='replace'):
        m=HIT.match(ln)
        if m: tot['hit']+=1; continue
        m=MISS.match(ln)
        if m:
            o=m.group(3)
            if o=='miss': tot['miss']+=1
            elif 'dodge' in o: tot['dodge']+=1
            elif 'parry' in o or 'parries' in o: tot['parry']+=1
            elif 'block' in o: tot['block']+=1
            elif 'riposte' in o: tot['riposte']+=1
            elif 'absorb' in o: tot['absorb']+=1
            elif 'INVULNERABLE' in o.upper(): tot['invuln']+=1
            else: tot['other:'+o[:26]]+=1
n=sum(v for k,v in tot.items())
print("YOUR OUTGOING SWINGS across", len(sys.argv)-1, "logs:  total attempts =", n)
for k,v in tot.most_common(): print(f"   {k:<36} {v:>6}  {v/n*100:>6.2f}%")
G=sum(tot[k] for k in ('dodge','parry','block','riposte'))
print(f"\n   ACTIVE-DEFENCE AVOIDANCE G = {G}/{n} = {G/n*100:.2f}%")
print(f"   miss (AC/skill roll)       = {tot['miss']/n*100:.2f}%")
print(f"   land rate                  = {tot['hit']/n*100:.2f}%")
for s in (0.10,0.20,0.30):
    print(f"   Strikethrough {int(s*100)}% -> +{s*G/tot['hit']*100:.2f}% landed swings")
