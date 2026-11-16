import argparse,json,hashlib,statistics,collections,itertools
from pathlib import Path
import numpy as np
parser=argparse.ArgumentParser(description='Exploratory fixed-support count transport')
parser.add_argument('human_dir',type=Path);parser.add_argument('--out-dir',type=Path,required=True)
cli=parser.parse_args();cli.out_dir.mkdir(parents=True,exist_ok=True)
src=cli.human_dir;assert len(list(src.glob('*.jsonl')))==3
rows=[];stats={};pure=[]
for path in sorted(src.glob('*.jsonl')):
 rs=[json.loads(x) for x in path.read_text().splitlines()];counter=collections.Counter()
 for ri,r in enumerate(rs):
  ss=[]
  for si,a in enumerate(r.get('annotations') or []):
   mf=a.get('model-atomic-facts') or [];hf=a.get('human-atomic-facts') or [];counter['sentences']+=1
   yy=[int(f['label']=='S') for f in hf if f['label'] in ['S','NS']]
   m=len(mf);h=len(hf);v=len(yy)
   mt=[x['text'].strip().casefold() for x in mf];ht=[x['text'].strip().casefold() for x in hf]
   if mt and ht and set(mt)==set(ht) and collections.Counter(mt)!=collections.Counter(ht):pure.append((path.stem,ri,si,mt,ht))
   if not yy:counter['no_scored_human_fact']+=1;continue
   if not m:counter['no_model_fact']+=1;continue
   counter['eligible_sentences']+=1;counter['count_disagree']+=int(m!=h)
   ss.append((m,h,v,float(np.mean(yy))))
  if ss:
   m,h,v,s=np.array(ss).T
   rows.append({'model':path.stem,'topic':r['topic'],'n_sentences':len(ss),'model_count_score':float(m@s/m.sum()),'human_count_score':float(h@s/h.sum()),'human_valid_score':float(v@s/v.sum()),'equal_sentence_score':float(s.mean()),'original_index':ri})
 stats[path.stem]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),**dict(counter),'responses_total':len(rs),'responses_eligible':sum(x['model']==path.stem for x in rows)}
for r in rows:r['effect']=r['human_count_score']-r['model_count_score'];r['valid_effect']=r['human_valid_score']-r['model_count_score']
def boot(rs,key,seed=20261116):
 groups=collections.defaultdict(list)
 for r in rs:groups[r['topic']].append(r[key])
 sums=np.array([sum(x) for x in groups.values()]);ns=np.array([len(x) for x in groups.values()]);rng=np.random.default_rng(seed);sims=[]
 for _ in range(25):
  ix=rng.integers(0,len(groups),(2000,len(groups)));sims.extend(sums[ix].sum(1)/ns[ix].sum(1))
 return {'estimate':float(np.mean([x[key] for x in rs])),'ci95':np.quantile(sims,[.025,.975]).tolist(),'n_rows':len(rs),'n_topics':len(groups)}
summary={'status':'exploratory, observed-count transport with fixed human sentence values','sources':stats,'overall':boot(rows,'effect'),'by_model':{n:boot([r for r in rows if r['model']==n],'effect') for n in stats},'valid_count_sensitivity':{n:boot([r for r in rows if r['model']==n],'valid_effect') for n in stats},'pure_same_surface_set_different_multiplicities':len(pure)}
matched=[]
for A,B in itertools.combinations(stats,2):
 aa={r['topic']:r for r in rows if r['model']==A};bb={r['topic']:r for r in rows if r['model']==B};qs=sorted(aa.keys()&bb.keys())
 matched.append({'A':A,'B':B,'n':len(qs),'model_count_margin':statistics.mean(aa[q]['model_count_score']-bb[q]['model_count_score'] for q in qs),'human_count_margin':statistics.mean(aa[q]['human_count_score']-bb[q]['human_count_score'] for q in qs)})
summary['matched_model_order']=matched
(cli.out_dir/'natural_summary.json').write_text(json.dumps(summary,indent=2));(cli.out_dir/'natural_response_rows.json').write_text(json.dumps(rows));(cli.out_dir/'natural_pure_surface_cases.json').write_text(json.dumps(pure,indent=2));print(json.dumps(summary,indent=2))
