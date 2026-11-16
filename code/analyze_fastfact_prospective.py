#!/usr/bin/env python3
"""Prospectively locked FaStfact-Bench granularity validation."""
from __future__ import annotations
import argparse,csv,json
from collections import defaultdict
from pathlib import Path
import numpy as np
INVALID_LABELS={"NA","N/A","invalid_label"}
MODELS=["DeepSeek-R1","DeepSeek-V3","Qwen2.5-7B-Instruct","gpt-4o"]
def valid_claims(rec):
    out=[]
    for c in rec.get("claims_lst",[]):
        action=(c.get("annotation_status_details") or {}).get("action");label=c.get("annotator_label")
        if action=="removed" or not label or label in INVALID_LABELS:continue
        out.append(1 if label=="supported" else 0)
    return out
def score_blocked(y,block):
    if not y:return None
    if block==1:return float(np.mean(y))
    return float(np.mean([float(all(y[i:i+block])) for i in range(0,len(y),block)]))
def bootstrap_mean_shift(rows,key,reps=50000,seed=20261113):
    d=np.array([r[key]-r["atomic"] for r in rows],dtype=float);rng=np.random.default_rng(seed);n=len(d);sims=[]
    left=reps
    while left:
        b=min(2000,left);idx=rng.integers(0,n,size=(b,n));sims.append(d[idx].mean(axis=1));left-=b
    sims=np.concatenate(sims);return float(d.mean()),float(np.quantile(sims,.025)),float(np.quantile(sims,.975))
def bootstrap_pair_margin(rows,reps=50000,seed=20261116):
    da=np.array([r["atomic_margin"] for r in rows]);dp=np.array([r["pair_margin"] for r in rows]);dd=dp-da;rng=np.random.default_rng(seed);n=len(rows);sa=[];sp=[];sd=[];left=reps
    while left:
        b=min(2000,left);idx=rng.integers(0,n,size=(b,n));sa.append(da[idx].mean(axis=1));sp.append(dp[idx].mean(axis=1));sd.append(dd[idx].mean(axis=1));left-=b
    sa,sp,sd=map(np.concatenate,(sa,sp,sd));q=lambda x:[float(np.quantile(x,.025)),float(np.quantile(x,.975))]
    return {"atomic_margin":float(da.mean()),"atomic_ci":q(sa),"pair_margin":float(dp.mean()),"pair_ci":q(sp),"margin_change":float(dd.mean()),"change_ci":q(sd)}
def main():
    ap=argparse.ArgumentParser();ap.add_argument("jsonl",type=Path);ap.add_argument("--out-dir",type=Path,default=Path("results"));args=ap.parse_args()
    recs=[json.loads(x) for x in args.jsonl.read_text(encoding="utf-8").splitlines() if x.strip()];rows=[];by_question=defaultdict(dict)
    for idx,rec in enumerate(recs):
        y=valid_claims(rec)
        if not y:continue
        row={"idx":idx,"question":rec.get("question","").strip(),"model":rec.get("model"),"source":rec.get("prompt_source"),"n_claims":len(y),"atomic":score_blocked(y,1),"pair":score_blocked(y,2),"triple":score_blocked(y,3)}
        rows.append(row);by_question[row["question"]][row["model"]]=row
    args.out_dir.mkdir(parents=True,exist_ok=True);model_rows=[]
    for model in MODELS:
        rs=[r for r in rows if r["model"]==model]
        model_rows.append({"model":model,"n":len(rs),"mean_claims":np.mean([r["n_claims"] for r in rs]),"atomic":np.mean([r["atomic"] for r in rs]),"pair":np.mean([r["pair"] for r in rs]),"pair_shift":np.mean([r["pair"]-r["atomic"] for r in rs]),"triple":np.mean([r["triple"] for r in rs]),"triple_shift":np.mean([r["triple"]-r["atomic"] for r in rs])})
    with (args.out_dir/"fastfact_prospective_model_results.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=model_rows[0].keys());w.writeheader();w.writerows(model_rows)
    primary=bootstrap_mean_shift(rows,"pair");triple=bootstrap_mean_shift(rows,"triple",seed=20261114);A,B="DeepSeek-R1","Qwen2.5-7B-Instruct";matched=[]
    for q,m in by_question.items():
        if A in m and B in m:matched.append({"question":q,"source":m[A]["source"],"atomic_margin":m[A]["atomic"]-m[B]["atomic"],"pair_margin":m[A]["pair"]-m[B]["pair"]})
    pair=bootstrap_pair_margin(matched)
    summary={"records_total":len(recs),"responses_scored":len(rows),"claims_scored":int(sum(r["n_claims"] for r in rows)),"pair_shift":{"mean":primary[0],"ci95":[primary[1],primary[2]]},"triple_shift":{"mean":triple[0],"ci95":[triple[1],triple[2]]},"matched_pair":{"A":A,"B":B,"n":len(matched),**pair},"protocol_sha256":"47ac7d71051fde119313313414570fa2145edb74d94ab51085a25be4b47ad5f0","source_blob_sha":"dfc3e47aa40dbd31350dc2fa88d595808001ed95"}
    (args.out_dir/"fastfact_prospective_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8");print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
