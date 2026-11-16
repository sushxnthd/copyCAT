"""One shared copy schedule must make a target beat ALL rivals simultaneously.

Compress roots by binary outcome pattern. Select an integer count in each
pattern; its bound is the number of available roots with that pattern.
Constraints and witness validation use integer counts. HiGHS solves the MILP
with zero requested MIP gap. The report distinguishes solver conclusions from
the sorting-based exact pairwise certificate.
"""
import argparse,collections,itertools,json
from pathlib import Path
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from mmlu_release import exact_envelope

def joint(matrix,target,budget,strict=True):
    a=np.asarray(matrix,dtype=np.int64);M,n=a.shape;totals=a.sum(axis=1)
    patterns=collections.defaultdict(list)
    for i in range(n):patterns[tuple(int(v) for v in a[:,i])].append(i)
    pats=sorted(patterns);X=np.array(pats,dtype=np.int64).T;counts=np.array([len(patterns[p]) for p in pats])
    rivals=[j for j in range(M) if j!=target]
    co=X[target,None,:]-X[rivals,:]
    lower=totals[rivals]-totals[target]+int(strict)
    constraints=LinearConstraint(np.vstack([co,np.ones(len(pats))]),np.r_[lower,0],np.r_[np.full(len(rivals),np.inf),budget])
    r=milp(np.ones(len(pats)),integrality=np.ones(len(pats)),bounds=Bounds(np.zeros(len(pats)),counts),constraints=constraints,options={'mip_rel_gap':0.0,'time_limit':30})
    result={'target_index':target,'budget':budget,'status':int(r.status),'message':r.message,'strict_winner':strict,'patterns':len(pats)}
    if r.status==0:
        x=np.rint(r.x).astype(np.int64)
        assert np.max(abs(r.x-x))<1e-6 and (x>=0).all() and (x<=counts).all()
        inds=[i for p,c in zip(pats,x) for i in patterns[p][:c]]
        after=totals+a[:,inds].sum(axis=1)
        assert len(inds)<=budget and ((after[target]>after[rivals]).all() if strict else (after[target]>=after[rivals]).all())
        assert int(x.sum())==round(r.fun)
        result.update(feasible=True,minimum_copies=int(x.sum()),mip_gap=float(r.mip_gap),mip_dual_bound=float(r.mip_dual_bound),selected_root_indices=inds,after_correct_counts=after.tolist(),witness_validated=True)
    elif r.status==2:result.update(feasible=False)
    else:result.update(feasible=None)
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('matrix',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--reps',type=int,default=20000);args=p.parse_args()
    obj=json.loads(args.matrix.read_text());a=np.array(obj['accuracy'],dtype=np.int64);models=obj['models'];M,n=a.shape;B=n//10
    pairs=list(itertools.combinations(range(M),2));totals=a.sum(axis=1);order=sorted(range(M),key=lambda i:(-totals[i],models[i]));winner=order[0]
    joint_results=[];exclusions=[]
    for t in range(M):
        r=joint(a,t,B);r['model']=models[t];joint_results.append(r)
        if t!=winner:
            maximum_numerator=int(totals[t]-totals[winner]+np.sum((a[t]-a[winner])>0))
            if maximum_numerator<=0:
                assert r['feasible'] is False
                exclusions.append({'model':models[t],'blocking_rival':models[winner],'maximum_possible_correct_count_advantage':maximum_numerator,'impossible_unique_winner_for_any_one_copy_budget':True})
    min_dethrone=[]
    for j in range(M):
        if j==winner:continue
        r=exact_envelope((a[winner]-a[j]).tolist(),B)
        min_dethrone.append({'rival':models[j],'baseline_correct_gap':int(totals[winner]-totals[j]),'minimum_tie':r['minimum_tie_or_reversal'],'minimum_strict_dethrone':r['minimum_strict_reversal']})
    rng=np.random.default_rng(20261116);flips=np.zeros(len(pairs),dtype=int);winner_counts=collections.Counter();any_flips=0
    for _ in range(args.reps):
        inds=rng.choice(n,B,replace=False);new=totals+a[:,inds].sum(axis=1)
        fs=[(totals[i]-totals[j])*(new[i]-new[j])<0 for i,j in pairs];flips+=fs;any_flips+=any(fs)
        top=np.flatnonzero(new==new.max());winner_counts['|'.join(models[t] for t in top)]+=1
    all_rs=[exact_envelope((a[i]-a[j]).tolist(),n) for i,j in pairs]
    grid=[]
    for b in range(0,n+1):
        flip=sum(r['minimum_strict_reversal'] is not None and r['minimum_strict_reversal']<=b for r in all_rs)
        reach=sum(r['strict_baseline'] and r['minimum_tie_or_reversal'] is not None and r['minimum_tie_or_reversal']<=b for r in all_rs)
        grid.append({'B':b,'budget_fraction':b/n,'strict_reversals':flip,'strict_robust':sum(r['strict_baseline'] for r in all_rs)-reach,'strict_reaching_zero':reach})
    result={'n':n,'B':B,'models':models,'baseline':[{'model':models[i],'correct':int(totals[i]),'accuracy':float(totals[i]/n)} for i in order],'baseline_winner':models[winner],
            'dethroning':min_dethrone,'joint_unique_winner_feasibility':joint_results,'integer_exclusion_certificates':exclusions,
            'random':{'seed':20261116,'reps':args.reps,'B':B,'any_pair_flip':any_flips,'pair_flip_counts':[{'a':models[i],'b':models[j],'flips':int(f)} for (i,j),f in zip(pairs,flips)],'winning_sets':dict(winner_counts)},'budget_curve':grid}
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('budget_curve',)},indent=2))
if __name__=='__main__':main()
