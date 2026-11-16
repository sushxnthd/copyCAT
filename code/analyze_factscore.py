"""Reproduce the label-free FActScore refinement controls from released ChatGPT labels."""
from __future__ import annotations
import argparse,json,math,statistics

def load(path):
    rows=[]
    for line in open(path,encoding='utf-8'):
        o=json.loads(line)
        if o.get('ChatGPT_Labels') is not None:rows.append(o)
    return rows
def response_score(o,rule='none'):
    labs=o['ChatGPT_Labels'];facts=o['facts'];n=len(labs);w=[1]*n
    if rule=='last_one':w[-1]+=1
    elif rule=='last_8pct':
        k=max(1,round(.08*n))
        for i in range(n-k,n):w[i]+=1
    elif rule=='last_quarter':
        k=max(1,math.ceil(.25*n))
        for i in range(n-k,n):w[i]+=1
    elif rule=='last_half':
        k=max(1,math.ceil(.5*n))
        for i in range(n-k,n):w[i]+=1
    elif rule=='he_she':
        for i,f in enumerate(facts):
            if f.startswith('He ') or f.startswith('She '):w[i]+=1
    return sum(wi*(lab=='S') for wi,lab in zip(w,labs))/sum(w),(sum(w)-n)/n
def macro(rows,rule):
    vals=[];fracs=[]
    for o in rows:
        s,f=response_score(o,rule);vals.append(s);fracs.append(f)
    return statistics.mean(vals),statistics.mean(fracs)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('alpaca');ap.add_argument('vicuna');args=ap.parse_args()
    A,V=load(args.alpaca),load(args.vicuna)
    for rule in ['none','last_one','last_8pct','last_quarter','last_half','he_she']:
        a,fa=macro(A,rule);v,fv=macro(V,rule)
        print(rule,{'alpaca':a,'vicuna':v,'margin':a-v,'added_frac_alpaca':fa,'added_frac_vicuna':fv})
