"""Independent tiny-instance brute-force checks of joint MILP feasibility."""
import itertools,json
import numpy as np
from joint_winners import joint

def brute(a,t,B):
    n=a.shape[1];base=a.sum(axis=1);rivals=[j for j in range(len(a)) if j!=t]
    for k in range(B+1):
        for ids in itertools.combinations(range(n),k):
            total=base+a[:,ids].sum(axis=1)
            if (total[t]>total[rivals]).all():return k
    return None

def main():
    rng=np.random.default_rng(20261116);cases=0
    examples=[np.array([[1,1,0,0],[0,1,1,0],[1,0,0,1]])]
    examples += [rng.integers(0,2,size=(int(rng.integers(2,5)),int(rng.integers(1,9)))) for _ in range(70)]
    for a in examples:
        for t in range(len(a)):
            for B in sorted(set([0,1,a.shape[1]//2,a.shape[1]])):
                if B>a.shape[1]:continue
                expected=brute(a,t,B);r=joint(a,t,B);cases+=1
                assert r['status'] in (0,2),r
                assert r['feasible']==(expected is not None),(a,t,B,expected,r)
                if expected is not None:assert r['minimum_copies']==expected
    a=examples[0]
    assert joint(a,0,1)['feasible'] is False and joint(a,0,2)['minimum_copies']==2
    assert all(any(((a[0]-a[j]).sum()+(a[0,i]-a[j,i]))>0 for i in range(4)) for j in (1,2))
    print(json.dumps({'status':'PASS','joint_brute_force_cases':cases,'independent_subset_enumeration':True,'incompatible_pairwise_witness_regression':True},indent=2))
if __name__=='__main__':main()
