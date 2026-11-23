"""Shared utilities for integrated exploratory sections in notebooks 06, 07, and 09. Original 01-07 outputs remain distinct."""
from pathlib import Path
import os, json, hashlib, time, platform, inspect
import numpy as np
import pandas as pd
import networkx as nx
import scipy
from scipy import stats
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path, connected_components
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(os.environ.get('NETWORK_ANALYSIS_LOCAL_ROOT', '.')).resolve()
OUT = Path(os.environ.get('NETWORK_ANALYSIS_SUPPLEMENT_ROOT', str(ROOT/'Results/Supplementary'))).resolve()
TABLES, FIGURES, ARRAYS, VALIDATION = [OUT/x for x in ('Tables','Figures','Arrays','Validation')]
for folder in (TABLES,FIGURES,ARRAYS,VALIDATION): folder.mkdir(parents=True,exist_ok=True)
AIRLINES = ['AA','DL','WN']
MODELS = ['observed','reciprocal','directed']
STRATEGIES = ['Degree','Betweenness','Random (mean of matched orders)']
METRICS = ['Efficiency','Reachability','Largest SCC']
RETAIN = ['Efficiency retention','Reachability retention','Largest SCC retention']
KEYS = ['Airline','Network set','Network']
SEED = 20261118
CHECKS = []
STAGE = 'supplement'

def begin(stage):
    global STAGE, CHECKS
    STAGE, CHECKS = stage, []
    required_by_stage = {
        '08': [
            '04_random_removal_orders.csv', '05_network_manifest.csv',
            '06_network_outcomes.csv', '06_intact_baselines.csv',
        ],
        '09': [
            '02_clustering_vs_transitivity.csv', '02_additional_structure.csv',
            '03_kcore_summary.csv', '03_louvain_binary_summary.csv',
            '04_null_modularity_by_network.csv',
            '04_null_structural_measures_and_intact_baselines.csv',
        ],
        '10': ['07_single_airport_outcomes.csv'],
    }
    if stage not in required_by_stage:
        raise ValueError(f'Unknown analysis section: {stage}')
    for filename in required_by_stage[stage]:
        check(f'Stage {stage}: required {filename}', (ROOT/'Results'/'Tables'/filename).is_file(), str(ROOT))
    if stage == '09':
        for filename in ['08_auc.csv', '08_combined_outcomes.csv']:
            check(f'Stage 09: required early-resilience {filename}', (TABLES/filename).is_file(), str(OUT))
    metadata = dict(stage=stage,seed=SEED,Python=platform.python_version(),NumPy=np.__version__,pandas=pd.__version__,NetworkX=nx.__version__,SciPy=scipy.__version__,Matplotlib=matplotlib.__version__,input_root=str(ROOT),output_root=str(OUT),status='running')
    (VALIDATION/f'{stage}_run_metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')

def check(name, condition, detail=''):
    passed=bool(condition)
    CHECKS.append({'Check':name,'Result':'PASS' if passed else 'FAIL','Detail':str(detail)})
    if not passed:
        pd.DataFrame(CHECKS).to_csv(VALIDATION/f'{STAGE}_checks.csv',index=False)
        raise AssertionError(f'{name}: {detail}')

def finish():
    pd.DataFrame(CHECKS).to_csv(VALIDATION/f'{STAGE}_checks.csv',index=False)
    p=VALIDATION/f'{STAGE}_run_metadata.json'
    metadata=json.loads(p.read_text());metadata['status']='passed';metadata['checks']=len(CHECKS)
    p.write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    print(f'{STAGE}: {len(CHECKS)} checks passed',flush=True)

def read(name): return pd.read_csv(ROOT/'Results/Tables'/name,keep_default_na=False)
def save(frame,name): frame.to_csv(TABLES/name,index=False)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rng_for(*key): return np.random.default_rng(np.random.SeedSequence(SEED,spawn_key=tuple(key)))
def removal_count(n,p): return (2*n*p+100)//200
def matrix(s,t,n): return csr_matrix((np.ones(len(s)),(s,t)),shape=(n,n))

def connectivity(A,n):
    d=shortest_path(A,method='D',unweighted=True,directed=True)
    reachable=np.isfinite(d)&(d>0)
    labels=connected_components(A,directed=True,connection='strong')[1]
    return np.array([(1/d[reachable]).sum()/(n*(n-1)),reachable.sum()/(n*(n-1)),np.bincount(labels).max()/n])

def after_removal(A,removed,n):
    keep=np.ones(n,dtype=bool);keep[removed]=False
    return connectivity(A[keep,:][:,keep],n)

def observed(a):
    nodes=pd.read_csv(ROOT/f'Data/Processed/{a}_nodes.csv')
    edges=pd.read_csv(ROOT/f'Data/Processed/{a}_edges.csv')
    ids=np.sort(nodes.airport_id.to_numpy(np.int64))
    return ids,np.searchsorted(ids,edges.source),np.searchsorted(ids,edges.target)

def network_files(a,model):
    if model=='observed': return [ROOT/f'Data/Processed/{a}_nodes.csv',ROOT/f'Data/Processed/{a}_edges.csv']
    files=[ROOT/f'Data/Processed/Nulls/{a}_{model}_null_networks.npz']
    if model=='directed': files.append(ROOT/f'Data/Processed/Nulls/{a}_directed_null_networks_expansion_chains_100_199.npz')
    return files

def networks(a,model):
    ids,s,t=observed(a)
    if model=='observed': return ids,[(0,s,t)]
    result=[]
    for file in network_files(a,model):
        with np.load(file,allow_pickle=False) as z:
            check(f'{a}/{model}/{file.name}: airport IDs',np.array_equal(ids,z['airport_ids']))
            ns=z['chain_ids'] if 'chain_ids' in z.files else np.arange(len(z['source']))
            for i,net in enumerate(ns):
                check(f'{a}/{model}/{net}: route endpoint membership',np.isin(z['source'][i],ids).all() and np.isin(z['target'][i],ids).all())
                result.append((int(net),np.searchsorted(ids,z['source'][i]),np.searchsorted(ids,z['target'][i])))
    check(f'{a}/{model}: network count and IDs',[v[0] for v in result]==list(range(200 if model=='directed' else 100)))
    return ids,result

def rankings(a,model):
    ids,_,_=observed(a)
    with np.load(ROOT/f'Data/Processed/Removal_Plans/{a}_{model}_targeted_rankings.npz') as z:
        check(f'{a}/{model}: ranking airport IDs',np.array_equal(ids,z['airport_ids']))
        result={int(net):{'Degree':np.searchsorted(ids,z['degree_order'][i]),'Betweenness':np.searchsorted(ids,z['betweenness_order'][i]),'Betweenness values':z['betweenness_values'][i].copy()} for i,net in enumerate(z['network_ids'])}
    for net,r in result.items():
        check(f'{a}/{model}/{net}: ranking permutations',all(np.array_equal(np.sort(r[s]),np.arange(len(ids))) for s in STRATEGIES[:2]))
    return result

def random_orders(a):
    ids,_,_=observed(a); rows=read('04_random_removal_orders.csv').query('Airline == @a').sort_values('Trial')
    orders=np.array([np.searchsorted(ids,np.fromstring(text,sep=' ',dtype=np.int64)) for text in rows['Airport order (BTS IDs)']])
    check(f'{a}: 100 complete random permutations',orders.shape==(100,len(ids)) and np.all(np.sort(orders,axis=1)==np.arange(len(ids))))
    for i,order in enumerate(orders):
        expected=np.random.default_rng(np.random.SeedSequence(20250401,spawn_key=(5,AIRLINES.index(a),9,i))).permutation(len(ids))
        check(f'{a}: replay random order {i}',np.array_equal(order,expected))
    return orders

def graph_undirected(ids,s,t):
    g=nx.Graph();g.add_nodes_from(ids.tolist())
    g.add_edges_from(sorted({(int(min(ids[u],ids[v])),int(max(ids[u],ids[v]))) for u,v in zip(s,t)}))
    return g

def figure(name):
    plt.savefig(FIGURES/f'{name}.png',dpi=180,bbox_inches='tight')
    plt.savefig(FIGURES/f'{name}.pdf',bbox_inches='tight')
    plt.close()

def variability(v):
    v=np.asarray(v,float);v=v[np.isfinite(v)];r=np.round(v,12)
    if not len(v): return dict(N=0,Unique=0,Mean=np.nan,SD=np.nan,Range=np.nan,Modal_share=1.,Status='missing')
    unique,counts=np.unique(r,return_counts=True);span=np.ptp(v);modal=counts.max()/len(v)
    status='constant' if len(unique)==1 else 'near-constant' if span<=1e-8*max(1,abs(v.mean())) or modal>=.95 else 'usable'
    return dict(N=len(v),Unique=len(unique),Mean=v.mean(),SD=v.std(ddof=1),Range=span,Modal_share=modal,Status=status)

def normalized_ranks(v):
    r=stats.rankdata(np.round(np.asarray(v,float),12),axis=0);r-=r.mean(axis=0)
    norm=np.sqrt((r*r).sum(axis=0));return np.divide(r,norm,out=np.zeros_like(r),where=norm>0)

# NumPy >= 2.0 provides trapezoid(); older NumPy provides only trapz(), which recent NumPy 2.x no longer has.
_trapezoid = getattr(np, 'trapezoid', None) or np.trapz

def auc(x,y,limit):
    x=np.asarray(x);y=np.asarray(y)
    assert x[0]==0 and limit<=x[-1]+1e-14 and np.all(np.diff(x)>0)
    mask=x<limit
    xx=np.r_[x[mask],limit];yy=np.r_[y[mask],np.interp(limit,x,y)]
    return float(_trapezoid(yy,xx)/limit)
