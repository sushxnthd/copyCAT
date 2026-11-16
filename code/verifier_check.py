import argparse,json,statistics
from pathlib import Path
parser=argparse.ArgumentParser(description='Fixed-pair reused-verifier robustness check')
parser.add_argument('predictions_dir',type=Path);parser.add_argument('--out',type=Path,required=True)
cli=parser.parse_args();cli.out.parent.mkdir(parents=True,exist_ok=True);p=cli.predictions_dir
data={n:{r['prompt']:r for r in [json.loads(x) for x in (p/(n+'.jsonl')).read_text().splitlines()] if r.get('ChatGPT_Labels') is not None} for n in ['alpaca-7B','vicuna-7b','vicuna-13b']}
results=[]
for B in ['vicuna-13b','vicuna-7b']:
 qs=sorted(data['alpaca-7B'].keys()&data[B].keys())
 for label in ['ChatGPT_Labels','LLAMA+NP_Labels']:
  scores=[]
  for model in ['alpaca-7B',B]:
   vals=[]
   for q in qs:
    r=data[model][q];labs=r[label];assert labs is not None and len(labs)==len(r['facts'])
    n=len(labs);k=max(1,round(.08*n));y=[int(x=='S') for x in labs]
    vals.append((sum(y)/n,(sum(y)+sum(y[-k:]))/(n+k)))
   scores.append([statistics.mean(x[i] for x in vals) for i in [0,1]])
  row=dict(A='alpaca-7B',B=B,n=len(qs),verifier=label,baseline_margin=scores[0][0]-scores[1][0],refined_margin=scores[0][1]-scores[1][1]);row['strict_reversal']=row['baseline_margin']*row['refined_margin']<0;results.append(row)
cli.out.write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
