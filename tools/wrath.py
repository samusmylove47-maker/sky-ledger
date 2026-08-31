import random, statistics
random.seed(12345)
N=400000
def roll_d20(wrath,M):
    W=wrath+5
    x=random.random()*W; y=random.random()*M
    A=(x+y+10)/2.0
    R=(x-y)+A/2.0
    d=min(max(int(R*20.0/A),0),19)+1
    return d/10.0
def extra(wrath,maxExtra=210,chance=0.49,minus=80):
    if wrath<115: return 1.0
    if random.random()>=chance: return 1.0
    b=max(10.0,(wrath-minus)/2.0)
    return min(maxExtra,100.0+b*random.random())/100.0
def mean_mult(wrath,M,n=N):
    return sum(roll_d20(wrath,M)*extra(wrath) for _ in range(n))/n
print("Reproducing the agent's section D table (M=450):")
print(f"{'Wrath':>6} {'E[d20*extra]':>13} {'agent':>8}")
agent={150:0.478,200:0.631,250:0.798,300:0.977,350:1.153,400:1.314,450:1.459,500:1.589,600:1.807,800:2.108}
for w,a in agent.items():
    m=mean_mult(w,450)
    print(f"{w:>6} {m:>13.3f} {a:>8.3f}   {'OK' if abs(m-a)<0.03 else 'MISMATCH'}")
print("\nSection C: % gain in mean variable damage from +104 ATK")
print(f"{'baseWrath':>10} {'M=400':>8} {'M=450':>8} {'M=500':>8}   agent(M=450)")
ag={320:31.9,345:28.3,372:24.6}
for w in (320,345,372):
    row=[]
    for M in (400,450,500):
        a=mean_mult(w,M); b=mean_mult(w+104,M); row.append((b/a-1)*100)
    print(f"{w:>10} {row[0]:>7.1f}% {row[1]:>7.1f}% {row[2]:>7.1f}%   {ag[w]:>6.1f}%")

print("\n=== CONSISTENCY TEST: does the Step2+Step3 chain reproduce the MEASURED histogram? ===")
# damage-roll agent measured, on real logs: 23.08% mode at 'mid', 5.99% at 'max'=2*mid,
# E[D20]=9.332, and mid/MAX in 0.44..0.56 (median 0.490).
for wrath,M in ((372,450),(345,450),(476,450)):
    d20=[roll_d20(wrath,M) for _ in range(200000)]
    from collections import Counter
    c=Counter(round(v*10) for v in d20)
    n=len(d20)
    print(f"\n  Wrath={wrath} M={M}   E[D20]={sum(d20)/n*10:.3f}   P(d=10)={c[10]/n*100:.2f}%  P(d=20)={c[20]/n*100:.2f}%  P(d=1)={c[1]/n*100:.2f}%")
    # now WITH the extra multiplier, as damage would actually be observed
    obs=[a*extra(wrath) for a in d20]
    cc=Counter(round(v,4) for v in obs)
    top=cc.most_common(3)
    print(f"    after Step3, modal values: {[(v,f'{k/n*100:.1f}%') for v,k in top]}")
    print(f"    P(value is an exact 0.1 lattice point) = {sum(k for v,k in cc.items() if abs(v*10-round(v*10))<1e-9)/n*100:.1f}%")
