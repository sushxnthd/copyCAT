"""Recompute all 18 Brier comparisons and post-hoc transfer/random controls."""
import argparse,itertools,json
from pathlib import Path
import pandas as pd,numpy as np
from refinement import at_most_interval,minimum_flip_budget
from medqa_crossmetric import metrics

def main():
 p=argparse.ArgumentParser();p.add_argument('data_dir',type=Path);p.add_argument('--out-dir',type=Path,default=Path('results'));args=p.parse_args()
 frames={name:pd.read_csv(args.data_dir/(fn+'.csv')) for name,fn in [('Qwen','qwen'),('Llama','llama'),('Mistral','mistral')]}
 rows=[];transfer=[];randoms=[]
 for setting in ['cot','direct']:
  for signal in ['conf_prob','conf_stated','conf_agree']:
   for A,B in itertools.combinations(frames,2):
    a=frames[A].query('setting==@setting').sort_values('qid').reset_index(drop=True)
    b=frames[B].query('setting==@setting').sort_values('qid').reset_index(drop=True)
    assert len(a)==len(b)==1273 and a.qid.equals(b.qid)
    assert a.gold.equals(b.gold)
    d=((a[signal]-a.correct)**2-(b[signal]-b.correct)**2).to_numpy()
    assert np.isfinite(d).all();base=float(d.mean());lo,hi=at_most_interval(d,127)
    k=minimum_flip_budget(d,strict=True)
    rows.append(dict(setting=setting,signal=signal,pair=A+'-'+B,n=len(d),baseline=base,lower=lo[0],upper=hi[0],lower_k=lo[1],upper_k=hi[1],minimum_strict_reversal_k=k))
    if k is not None and k<=127:
     chosen=np.argsort(d if base>0 else -d,kind='stable')[:k]
     ad=pd.concat([a,a.iloc[chosen]]);bd=pd.concat([b,b.iloc[chosen]])
     ma,mb,da,db=[metrics(x,signal) for x in [a,b,ad,bd]]
     row={'setting':setting,'signal':signal,'pair':A+'-'+B,'min_flip_roots':k}
     for metric in ma:
      row[metric+'_delta_before']=ma[metric]-mb[metric];row[metric+'_delta_after']=da[metric]-db[metric]
     transfer.append(row)
     rng=np.random.default_rng(20261115);flips=0
     for _ in range(20):
      ix=np.argpartition(rng.random((1000,len(d))),126,axis=1)[:,:127]
      vals=(d.sum()+d[ix].sum(1))/(len(d)+127)
      flips+=int(np.sum(vals*base<0))
     randoms.append({'setting':setting,'signal':signal,'pair':A+'-'+B,'draws':20000,'roots_per_draw':127,'seed':20261115,'strict_reversals':flips})
 args.out_dir.mkdir(parents=True,exist_ok=True)
 pd.DataFrame(rows).to_csv(args.out_dir/'medqa_all18.csv',index=False)
 pd.DataFrame(transfer).to_csv(args.out_dir/'medqa_crossmetric_recomputed.csv',index=False)
 (args.out_dir/'medqa_random_controls_recomputed.json').write_text(json.dumps(randoms,indent=2))
 print(json.dumps({'comparisons':len(rows),'strict_reversible_at_10pct':len(transfer),'random_controls':randoms},indent=2))
if __name__=='__main__':main()
