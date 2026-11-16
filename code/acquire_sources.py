"""Acquire public research releases, then verify content hashes. No model inference."""
import argparse,base64,concurrent.futures,hashlib,json,urllib.request,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser();parser.add_argument('--data-root',type=Path,required=True);args=parser.parse_args()
DATA=args.data_root.resolve();DATA.mkdir(parents=True,exist_ok=True)
def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Epistemics-reproduction/1.0'})
    with urllib.request.urlopen(req,timeout=90) as r:return r.read()
def blob(repo,sha,path):
    p=DATA/path
    if not p.exists():
        obj=json.loads(get(f'https://api.github.com/repos/{repo}/git/blobs/{sha}'));p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(base64.b64decode(obj['content']))
    return path,len(p.read_bytes())
jobs=[('JhishanDeb/medqa-confidence','ac0abac9634f16200d8860db81f74b6e5d6271e6','qwen.csv'),('JhishanDeb/medqa-confidence','270e0e019920e4d9b8e6622ea0685e40323d3285','llama.csv'),('JhishanDeb/medqa-confidence','2afd9626b5786a9bb6b451bf2c53f0e49ffe6183','mistral.csv'),('Yingjia-Wan/FastFact','dfc3e47aa40dbd31350dc2fa88d595808001ed95','fastfact.jsonl')]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
    for a in ex.map(lambda args:blob(*args),jobs):print('downloaded',a,flush=True)
for ident,folder,sha in [('1lgPqysx2H7zMcyBmuNDztNTAlvfYK0jQ','factscore','449dcd2b34dd9cc4e920ede9be042c8314b3bdce918f416ed42a8b120a28cf5c'),('155exEdKs7R21gZF4G-x54-XN3qswBcPo','factscore_human','404482c9a7d588d581a2f7a78d609fe6bfec4ddc0f729c8560a61b1743dbffab')]:
    p=DATA/(folder+'.zip')
    if not p.exists():p.write_bytes(get('https://drive.google.com/uc?export=download&id='+ident))
    assert hashlib.sha256(p.read_bytes()).hexdigest()==sha,('archive hash',folder)
    target=DATA/folder;target.mkdir(exist_ok=True)
    with zipfile.ZipFile(p) as z:
        assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist());z.extractall(target)
expected=json.loads((ROOT/'source_sha256.json').read_text())
for rel,sha in expected.items():assert hashlib.sha256((DATA/rel).read_bytes()).hexdigest()==sha,rel
print('PASS: all',len(expected),'original input hashes verified',flush=True)
