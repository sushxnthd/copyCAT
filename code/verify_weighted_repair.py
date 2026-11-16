"""Post-hoc closure verification, not an independent effect replication."""
import json,argparse,itertools
from pathlib import Path
import numpy as np,pandas as pd
from weighted_measure import metrics,split
from refinement import minimum_flip_budget
from medqa_crossmetric import metrics as legacy

def main():
 p=argparse.ArgumentParser();p.add_argument('data',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 frames={n:pd.read_csv(a.data/(n+'.csv')) for n in ['qwen','llama','mistral']};rng=np.random.default_rng(20261116)
 cases=[];maxerr=0.;checks=0
 for setting in ['cot','direct']:
  for signal in ['conf_prob','conf_stated','conf_agree']:
   for A,B in itertools.combinations(frames,2):
    ds=[frames[n].query('setting==@setting').sort_values('qid').reset_index(drop=True) for n in [A,B]]
    assert ds[0].qid.equals(ds[1].qid)
    c=[df[signal].to_numpy() for df in ds];y=[df.correct.to_numpy() for df in ds]
    delta=(c[0]-y[0])**2-(c[1]-y[1])**2;k=minimum_flip_budget(delta,strict=True)
    schedules={'random_1_to_7':rng.integers(1,8,len(delta))}
    if k is not None and k<=127:
     m=np.ones(len(delta),int);order=np.argsort(delta if delta.mean()>0 else -delta,kind='stable');m[order[:k]]+=1;schedules['targeted_minimum']=m
    for name,m in schedules.items():
     entry={'setting':setting,'signal':signal,'pair':A+'-'+B,'schedule':name,'models':{}}
     for j,n in enumerate([A,B]):
      base=metrics(c[j],y[j],np.ones(len(m)))
      old=legacy(ds[j],signal)
      assert all(abs(base[key]-old[key])<1e-12 for key in base)
      cc,yy,ww=split(c[j],y[j],m);fixed=metrics(cc,yy,ww);naive=metrics(cc,yy,np.ones(len(ww)))
      errors={key:abs(base[key]-fixed[key]) for key in base};maxerr=max(maxerr,*errors.values());checks+=3
      assert max(errors.values())<1e-12
      entry['models'][n]={'baseline':base,'naive_split':naive,'mass_conserved_split':fixed,'absolute_error':errors}
     cases.append(entry)
 base=metrics([.1,.9],[0,1],[1,1]);changed=metrics([.1,.8,.9],[0,0,1],[.5,.5,1])
 assert abs(base['brier']-changed['brier'])>.1
 control=metrics([.2,.7],[0,1],[1,1]);wrong=metrics([.2,.2,.7],[0,0,1],[1,1,1])
 assert abs(control['brier']-wrong['brier'])>.001
 tied=metrics([.5,.5],[0,1],[1,1]);assert tied['auroc']==.5
 result={'status':'post-hoc implementation verification of an algebraic consequence; not novel weighted metrics','comparisons':18,'schedules':len(cases),'scalar_invariance_checks':checks,'maximum_absolute_error':maxerr,'tolerance':1e-12,'seed':20261116,'cases':cases,'failure_controls_passed':True}
 a.out.write_text(json.dumps(result,indent=2,allow_nan=False));print({k:v for k,v in result.items() if k!='cases'})
if __name__=='__main__':main()
