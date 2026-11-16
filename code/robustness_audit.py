"""JSON CLI for bounded multiplicity sensitivity and declared-lineage checks."""
import argparse,json
from pathlib import Path
from refinement import at_most_interval,minimum_flip_budget,check_lineage,ria_score,_vector

def audit(obj,budget):
    a=_vector(obj['loss_a']);b=_vector(obj['loss_b'])
    if a.shape!=b.shape:raise ValueError('A/B root loss arrays must align')
    d=a-b;(lo,kl),(hi,ku)=at_most_interval(d,budget)
    result={'n':len(d),'budget':budget,'baseline_A_minus_B':float(d.mean()),'attained_lower':lo,'lower_attaining_k':kl,'attained_upper':hi,'upper_attaining_k':ku,'strict_order_robust':bool(lo>0 or hi<0),'minimum_tie_or_reversal_k':minimum_flip_budget(d),'minimum_strict_reversal_k':minimum_flip_budget(d,strict=True),'scope':'shared, distinct, one-extra-copy roots; additive equal-root score; tight hull, not continuous attainable set'}
    if 'leaves' in obj:
        result['lineage']=check_lineage(obj.get('root_masses'),obj['leaves'])
        if result['lineage']['status']=='verified_declared_masses':
            result['ria_score']=ria_score([x['loss'] for x in obj['leaves']],[x['mass'] for x in obj['leaves']])
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('json');p.add_argument('--budget',type=int,required=True);args=p.parse_args()
    try:print(json.dumps(audit(json.loads(Path(args.json).read_text()),args.budget),indent=2,allow_nan=False))
    except (ValueError,KeyError,TypeError) as e:p.error(str(e))
