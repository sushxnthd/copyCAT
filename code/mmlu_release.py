"""Acquire and audit the complete pinned English MMLU-ProX-Lite result slice.

All exact-match comparisons use integer numerators and rational comparisons.
The saved interval is a tight hull with attained endpoints, not a continuous
set of attainable values. Accuracy differences are A minus B (higher better).
"""
from __future__ import annotations
import argparse, concurrent.futures, csv, hashlib, itertools, json, re, urllib.request
from fractions import Fraction
from pathlib import Path

REPO='3ae3ae3ae/mmlu-prox-lite-evals'
REV='691773a72b353486961d40e99a6c5cbe31c89c43'
RX=re.compile(r'^([^/]+)/samples_mmlu_prox_lite_en_(.+?)_\d{4}-\d{2}-\d{2}T.*\.jsonl$')

def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Epistemics-reproduction/1.0'})
    with urllib.request.urlopen(req,timeout=90) as r:return r.read()

def acquire(root):
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    api=f'https://huggingface.co/api/datasets/{REPO}/tree/{REV}'
    listing_file=root/'root_listing.json'
    if not listing_file.exists():listing_file.write_bytes(fetch(api+'?recursive=false&expand=false&limit=100'))
    listing=json.loads(listing_file.read_text())
    models=sorted(x['path'] for x in listing if x['type']=='directory' and x['path']!='token-usage')
    assert len(models)==10,models
    def get_listing(model):
        p=root/(model+'_listing.json')
        if not p.exists():p.write_bytes(fetch(api+'/'+model+'?recursive=true&expand=false&limit=1000'))
        rows=json.loads(p.read_text());assert len(rows)<1000,'Possible truncated listing'
        return [x for x in rows if RX.match(x.get('path',''))]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        files=[x for arr in ex.map(get_listing,models) for x in arr]
    domains=sorted({RX.match(x['path']).group(2) for x in files})
    assert len(domains)==14 and len(files)==140,(domains,len(files))
    assert len({(RX.match(x['path']).group(1),RX.match(x['path']).group(2)) for x in files})==140
    def get_file(meta):
        rel=meta['path'];p=root/rel;p.parent.mkdir(parents=True,exist_ok=True)
        if not p.exists():p.write_bytes(fetch(f'https://huggingface.co/datasets/{REPO}/resolve/{REV}/'+rel))
        raw=p.read_bytes();assert len(raw)==meta['size'],('size',rel)
        gitsha=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        if not meta.get('lfs'):assert gitsha==meta['oid'],('blob',rel)
        return {'path':rel,'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'git_blob_sha1':gitsha,'tree_oid':meta['oid']}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        manifest=list(ex.map(get_file,files))
    (root/'manifest.json').write_text(json.dumps({'repository':REPO,'revision':REV,'models':models,'domains':domains,'files':manifest},indent=2)+'\n')
    return models,domains,manifest

def exact_envelope(d,budget):
    if not d or any(x not in (-1,0,1) for x in d):raise ValueError('binary accuracy difference vector required')
    n=len(d)
    if isinstance(budget,bool) or not isinstance(budget,int) or not 0<=budget<=n:raise ValueError('invalid budget')
    D=sum(d);s=sorted(d);lo=hi=Fraction(D,n);lo_k=hi_k=0;lc=uc=0
    min_tie=min_flip=None
    for k in range(1,n+1):
        lc+=s[k-1];uc+=s[-k]
        l=Fraction(D+lc,n+k);u=Fraction(D+uc,n+k)
        if k<=budget:
            if l<lo:lo,lo_k=l,k
            if u>hi:hi,hi_k=u,k
        if D:
            edge=l if D>0 else u
            if min_tie is None and (edge<=0 if D>0 else edge>=0):min_tie=k
            if min_flip is None and (edge<0 if D>0 else edge>0):min_flip=k
    strict=D!=0
    return {'n':n,'B':budget,'baseline':float(Fraction(D,n)),'baseline_num':D,
            'lo':float(lo),'hi':float(hi),'lo_exact':str(lo),'hi_exact':str(hi),
            'strict_baseline':strict,'reaches_zero':lo<=0<=hi,
            'strict_reversal':bool(D>0 and lo<0 or D<0 and hi>0),
            'min_k':lo_k,'max_k':hi_k,'minimum_tie_or_reversal':min_tie,
            'minimum_strict_reversal':min_flip}

def load_data(root):
    root=Path(root);manifest=json.loads((root/'manifest.json').read_text());data={};docs={};coverage=[]
    for f in manifest['files']:
        p=root/f['path'];raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==f['sha256']
        model,domain=RX.match(f['path']).groups();m={}
        for line in raw.splitlines():
            if not line.strip():continue
            row=json.loads(line);doc=row['doc'];qid=doc.get('question_id');dh=row.get('doc_hash')
            assert qid is not None and dh is not None,('missing identifier',p)
            key=(str(qid),str(dh));v=row['exact_match']
            assert type(v) in (int,float) and v in (0,1),('nonbinary',p,v)
            assert key not in m,('duplicate root',p,key)
            canonical=json.dumps(doc,sort_keys=True,ensure_ascii=False)
            dk=(domain,key)
            assert dk not in docs or docs[dk]==canonical,('doc identity mismatch',p,key)
            docs[dk]=canonical;m[key]=int(v)
        data[(model,domain)]=m;coverage.append({'model':model,'domain':domain,'raw_rows':len(m),'raw_accuracy':sum(m.values())/len(m)})
    models=manifest['models'];domains=manifest['domains']
    common={dom:sorted(set.intersection(*(set(data[(m,dom)]) for m in models))) for dom in domains}
    keys=[(dom,key) for dom in domains for key in common[dom]]
    matrix=[[data[(m,dom)][key] for dom,key in keys] for m in models]
    return models,domains,data,common,keys,matrix,coverage

def write_csv(path,rows):
    with Path(path).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def audit(root,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    models,domains,data,common,keys,matrix,coverage=load_data(root)
    domain_rows=[]
    for dom in domains:
        ks=common[dom]
        for a,b in itertools.combinations(models,2):
            d=[data[(a,dom)][k]-data[(b,dom)][k] for k in ks]
            domain_rows.append({'domain':dom,'model_a':a,'model_b':b,**exact_envelope(d,len(d)//10)})
    pooled=[];witnesses=[]
    for ia,ib in itertools.combinations(range(len(models)),2):
        d=[a-b for a,b in zip(matrix[ia],matrix[ib])];r=exact_envelope(d,len(d)//10)
        pooled.append({'model_a':models[ia],'model_b':models[ib],**r})
        if r['strict_reversal']:
            inds=sorted(range(len(d)),key=lambda i:(d[i],i),reverse=r['baseline_num']<0)[:r['minimum_strict_reversal']]
            num=sum(d)+sum(d[i] for i in inds)
            assert num*sum(d)<0 and len(inds)<=r['B']
            witnesses.append({'model_a':models[ia],'model_b':models[ib],'k':len(inds),'baseline_num':sum(d),'after_num':num,'denominator':len(d)+len(inds),'selected_root_indices':inds,'selected_roots':[keys[i] for i in inds]})
    for row in coverage:row['common_rows']=len(common[row['domain']])
    def summ(rows):
        strict=[r for r in rows if r['strict_baseline']]
        return {'pairs':len(rows),'strict_baselines':len(strict),'baseline_ties':len(rows)-len(strict),'strict_reaching_zero':sum(r['reaches_zero'] for r in strict),'strict_reversals':sum(r['strict_reversal'] for r in rows),'strict_certified_robust':sum(not r['reaches_zero'] for r in strict)}
    summary={'repository':REPO,'revision':REV,'models':models,'domains':domains,'english_result_files':len(coverage),'domain_common_counts':{d:len(common[d]) for d in domains},'domain':summ(domain_rows),'pooled':summ(pooled),'pooled_common_questions':len(keys),'total_raw_rows':sum(r['raw_rows'] for r in coverage),'all_binary_and_question_identity_checks_passed':True}
    for name,rows in [('domain_pairs.csv',domain_rows),('pooled_pairs.csv',pooled),('coverage.csv',coverage)]:write_csv(out/name,rows)
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (out/'witnesses.json').write_text(json.dumps(witnesses,indent=2)+'\n')
    (out/'aligned_binary_matrix.json').write_text(json.dumps({'models':models,'keys':keys,'accuracy':matrix},indent=2)+'\n')
    return summary

def main():
    p=argparse.ArgumentParser();p.add_argument('--data-root',type=Path,required=True);p.add_argument('--out-dir',type=Path,required=True);p.add_argument('--download',action='store_true');args=p.parse_args()
    if args.download:
        models,domains,files=acquire(args.data_root);print('Verified',len(files),'files for',len(models),'models and',len(domains),'domains',flush=True)
    print(json.dumps(audit(args.data_root,args.out_dir),indent=2))
if __name__=='__main__':main()
