import argparse,json,numpy as np
from pathlib import Path
from analyze_fastfact_prospective import valid_claims,score_blocked
parser=argparse.ArgumentParser(description='Exact adjacent-conjunction shift identity')
parser.add_argument('fastfact',type=Path);parser.add_argument('--out',type=Path,required=True)
args=parser.parse_args();args.out.parent.mkdir(parents=True,exist_ok=True)
rs=[json.loads(x) for x in args.fastfact.read_text().splitlines()]
a=[];b=[];cs=[];odd=0;positive=0
for r in rs:
 y=valid_claims(r);n=len(y)
 if not n:continue
 m=n//2;u=sum(y[2*j]!=y[2*j+1] for j in range(m));baseline=np.mean(y);shift=score_blocked(y,2)-baseline
 if n%2:
  odd+=1;singleton=y[-1];forced=-u/(n+1);endpoint=(singleton-baseline)/(n+1)
 else:forced=-u/n;endpoint=0
 assert abs(shift-forced-endpoint)<1e-12
 positive+=int(shift>1e-12);a.append(shift);b.append(forced);cs.append(endpoint)
result={'n':len(a),'odd':odd,'positive_shifts':positive,'mean_total':np.mean(a),'discordance_component':np.mean(b),'singleton_component':np.mean(cs)}
args.out.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
