"""Post-hoc matched-prompt audit of the entire disclosed rule/model-pair family."""
import argparse,itertools,csv,statistics
from pathlib import Path
from analyze_factscore import load,response_score

def main():
 p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('--out-dir',type=Path,default=Path('results'));a=p.parse_args()
 data={f.stem:{r['prompt']:r for r in load(f)} for f in sorted(a.directory.glob('*.jsonl'))};rows=[]
 for A,B in itertools.combinations(data,2):
  qs=sorted(set(data[A])&set(data[B]));assert qs
  for rule in ['none','last_one','last_8pct','last_quarter','last_half','he_she']:
   vals=[]
   for model in [A,B]:
    rs=[data[model][q] for q in qs];ss=[response_score(r,rule) for r in rs]
    total=sum(len(r['facts']) for r in rs);added=sum(round(frac*len(r['facts'])) for r,(s,frac) in zip(rs,ss))
    vals.append((statistics.mean(s for s,f in ss),added/total))
   rows.append(dict(A=A,B=B,n=len(qs),rule=rule,score_A=vals[0][0],score_B=vals[1][0],margin=vals[0][0]-vals[1][0],global_added_fraction_A=vals[0][1],global_added_fraction_B=vals[1][1]))
 a.out_dir.mkdir(exist_ok=True,parents=True)
 with (a.out_dir/'factscore_matched_all_pairs.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
 for r in rows:
  if r['A']=='alpaca-7B' and r['B'] in ['vicuna-7b','vicuna-13b'] and r['rule'] in ['none','last_8pct']:print(r)
if __name__=='__main__':main()
