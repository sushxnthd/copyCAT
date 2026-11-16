"""Exact one-copy refinement extrema and explicit mass validation.

Intervals are tight enclosing hulls with attained endpoints; interior values
need not be attainable. Differences are A loss minus B loss (lower is better).
"""
from __future__ import annotations
import numbers
import numpy as np

def _vector(d):
    d=np.asarray(d,dtype=float)
    if d.ndim!=1 or not len(d) or not np.isfinite(d).all():
        raise ValueError('expected a nonempty finite one-dimensional vector')
    return d

def _budget(k,n):
    if isinstance(k,bool) or not isinstance(k,numbers.Integral) or not 0<=k<=n:
        raise ValueError('budget must be an integer in [0,n]')

def _all(d):
    d=_vector(d);s=np.sort(d);n=len(d);k=np.arange(n+1)
    prefix=np.r_[0.,np.cumsum(s)];D=float(np.sum(d))
    return (D+prefix)/(n+k),(D+prefix[-1]-prefix[n-k])/(n+k)

def exact_k_interval(d,k:int):
    d=_vector(d);_budget(k,len(d));lo,hi=_all(d)
    return float(lo[k]),float(hi[k])

def at_most_interval(d,budget:int):
    d=_vector(d);_budget(budget,len(d));lo,hi=_all(d)
    kl=int(np.argmin(lo[:budget+1]));ku=int(np.argmax(hi[:budget+1]))
    return (float(lo[kl]),kl),(float(hi[ku]),ku)

def minimum_flip_budget(d,*,strict=False):
    """First k reaching a tie or reversal; strict=True requires opposite sign."""
    d=_vector(d);base=float(d.mean())
    if base==0:return None if strict else 0
    lo,hi=_all(d)
    feasible=(lo<0 if strict else lo<=0) if base>0 else (hi>0 if strict else hi>=0)
    ks=np.flatnonzero(feasible)
    return int(ks[0]) if len(ks) else None

def ria_score(losses,masses):
    losses=_vector(losses);masses=_vector(masses)
    if losses.shape!=masses.shape or (masses<0).any() or masses.sum()<=0:
        raise ValueError('masses must match losses, be nonnegative, and have positive total')
    return float(np.dot(losses,masses)/masses.sum())

def check_lineage(root_masses,leaves,tolerance=1e-12):
    """Validate declared raw masses. Does not infer semantic correctness."""
    if not root_masses:return {'status':'unverified','reason':'missing root specification'}
    if any(not isinstance(k,str) or not k for k in root_masses):
        raise ValueError('root identifiers must be nonempty strings')
    masses=_vector(list(root_masses.values()))
    if (masses<0).any() or masses.sum()<=0:raise ValueError('invalid root masses')
    totals=dict.fromkeys(root_masses,0.);seen=set()
    for leaf in leaves:
        root=leaf.get('root_id')
        if root not in totals:return {'status':'unverified','reason':'missing or unknown root lineage'}
        mass=float(leaf['mass']);loss=float(leaf['loss'])
        if not np.isfinite([mass,loss]).all() or mass<0:raise ValueError('invalid leaf mass/loss')
        totals[root]+=mass;seen.add(root)
    if seen!=set(root_masses):return {'status':'unverified','reason':'root has no descendants'}
    failed={root:{'expected':float(mass),'observed':totals[root]} for root,mass in root_masses.items() if not np.isclose(totals[root],mass,rtol=0,atol=tolerance)}
    return {'status':'failed' if failed else 'verified_declared_masses','failures':failed,'semantic_lineage_independently_verified':False}
