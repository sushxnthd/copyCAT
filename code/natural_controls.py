import argparse,json,re,itertools,collections
from pathlib import Path
import numpy as np
parser=argparse.ArgumentParser(description='Post-hoc support shuffle and literal dedup controls')
parser.add_argument('human_dir',type=Path);parser.add_argument('predictions_dir',type=Path);parser.add_argument('--out',type=Path,required=True)
cli=parser.parse_args();cli.out.parent.mkdir(parents=True,exist_ok=True)
assert len(list(cli.human_dir.glob('*.jsonl')))==3 and len(list(cli.predictions_dir.glob('*.jsonl')))==12
rng=np.random.default_rng(20261117);sims=np.zeros(10000);actual=[]
for p in sorted(cli.human_dir.glob('*.jsonl')):
 for line in p.read_text().splitlines():
  r=json.loads(line);triples=[]
  for a in r.get('annotations') or []:
   h=a.get('human-atomic-facts') or [];m=a.get('model-atomic-facts') or [];ys=[f['label']=='S' for f in h if f['label'] in ['S','NS']]
   if ys and m:triples.append((len(m),len(h),np.mean(ys)))
  if not triples:continue
  m,h,s=np.array(triples).T;coef=h/h.sum()-m/m.sum();actual.append(float(coef@s))
  ix=np.argsort(rng.random((10000,len(s))),axis=1);sims+=(s[ix]*coef).sum(axis=1)
sims/=len(actual);effect=np.mean(actual)
rows=[]
for p in sorted(cli.predictions_dir.glob('*.jsonl')):
 vals=[];repeated=0;conflicts=0
 for line in p.read_text().splitlines():
  r=json.loads(line);labels=r.get('ChatGPT_Labels')
  if labels is None:continue
  groups=collections.defaultdict(list)
  for f,l in zip(r['facts'],labels):groups[re.sub(r'\W+',' ',f.casefold()).strip()].append(l)
  conflicts+=sum(len(set(g))>1 for g in groups.values());repeated+=int(len(groups)<len(labels))
  if any(len(set(g))>1 for g in groups.values()):continue
  vals.append((np.mean([l=='S' for l in labels]),np.mean([g[0]=='S' for g in groups.values()])))
 rows.append({'model':p.stem,'n':len(vals),'responses_with_repeats':repeated,'conflicting_groups':conflicts,'baseline':float(np.mean([a for a,b in vals])),'deduplicated':float(np.mean([b for a,b in vals]))})
flips=[(a['model'],b['model']) for a,b in itertools.combinations(rows,2) if (a['baseline']-b['baseline'])*(a['deduplicated']-b['deduplicated'])<0]
out={'status':'post-hoc falsification controls','permutation':{'reps':10000,'seed':20261117,'responses':len(actual),'observed':float(effect),'null_mean':float(sims.mean()),'null_ci95':np.quantile(sims,[.025,.975]).tolist(),'two_sided_monte_carlo_p':float((1+np.sum(abs(sims)>=abs(effect)))/10001),'interpretation':'conditional within-response support-shuffle diagnostic, not population causal inference'},'exact_normalized_dedup':rows,'dedup_pair_reversals':flips}
cli.out.write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
