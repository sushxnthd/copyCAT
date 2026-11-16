"""Independent exhaustive verification of integer/rational copy certificates."""
import itertools,json
from fractions import Fraction
from mmlu_release import exact_envelope,RX

def main():
    vectors=budgets=0
    for n in range(1,7):
        for d in itertools.product((-1,0,1),repeat=n):
            vectors+=1;values=[];min_tie=min_flip=None;D=sum(d)
            for B in range(n+1):
                curr=[Fraction(D+sum(d[i] for i in ids),n+B) for ids in itertools.combinations(range(n),B)]
                values.extend(curr);budgets+=1;r=exact_envelope(list(d),B)
                assert Fraction(r['lo_exact'])==min(values) and Fraction(r['hi_exact'])==max(values),(d,B,r)
                if D:
                    if min_tie is None and any(v*D<=0 for v in curr):min_tie=B
                    if min_flip is None and any(v*D<0 for v in curr):min_flip=B
                assert r['strict_reversal']==bool(D and any(v*D<0 for v in values))
            assert r['minimum_tie_or_reversal']==min_tie and r['minimum_strict_reversal']==min_flip
    r=exact_envelope([-1,0],1)
    assert r['lo_exact']=='-2/3' and r['hi_exact']=='-1/3' and r['min_k']==r['max_k']==1
    assert exact_envelope([1,0],1)['lo_exact']=='1/3'
    assert RX.match('m/samples_mmlu_prox_lite_en_biology_2026-10-10T12-49-35.585845.jsonl')
    for d,b in [([],0),([2],0),([1],-1),([1],2),([1],True)]:
        try:exact_envelope(d,b)
        except ValueError:pass
        else:raise AssertionError('invalid input accepted')
    out={'status':'PASS','signed_vectors':vectors,'subset_budget_cases':budgets,'arithmetic':'integer and exact fractions','independent_enumeration':True,'ratio_sensitive_regressions':True,'filename_regex_regression':True}
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
