"""Cross-metric transfer check for Brier-selected refinement roots.

Input CSVs are the released per_question.csv files from JhishanDeb/medqa-confidence.
The script selects the minimum Brier-flip subset and reports Brier, 15-bin ECE,
and AUROC before/after duplicating those same qids in both compared models.
"""
from __future__ import annotations
import argparse, pandas as pd, numpy as np
from scipy.stats import rankdata
from refinement import minimum_flip_budget

def auroc(c,y):
    c=np.asarray(c,float);y=np.asarray(y,int);n1=y.sum();n0=len(y)-n1
    if n1==0 or n0==0:return np.nan
    r=rankdata(c)
    return float((r[y==1].sum()-n1*(n1+1)/2)/(n1*n0))
def ece(c,y,bins=15):
    c=np.asarray(c,float);y=np.asarray(y,float);idx=np.minimum((c*bins).astype(int),bins-1);tot=0.0
    for b in range(bins):
        m=idx==b
        if m.any():tot+=abs(y[m].sum()-c[m].sum())
    return float(tot/len(c))
def metrics(df,signal):
    c=df[signal].to_numpy(float);y=df.correct.to_numpy(float)
    return {'brier':float(np.mean((c-y)**2)),'ece':ece(c,y),'auroc':auroc(c,y)}
def run(A,B,setting,signal):
    a=A[A.setting==setting].sort_values('qid');b=B[B.setting==setting].sort_values('qid')
    q=sorted(set(a.qid)&set(b.qid));a=a.set_index('qid').loc[q].reset_index();b=b.set_index('qid').loc[q].reset_index()
    d=(a[signal]-a.correct)**2-(b[signal]-b.correct)**2;k=minimum_flip_budget(d.to_numpy())
    order=np.argsort(d.to_numpy()) if d.mean()>0 else np.argsort(-d.to_numpy());chosen=set(a.qid.to_numpy()[order[:k]])
    def dup(df):return pd.concat([df,df[df.qid.isin(chosen)]],ignore_index=True)
    return k,metrics(a,signal),metrics(b,signal),metrics(dup(a),signal),metrics(dup(b),signal)
