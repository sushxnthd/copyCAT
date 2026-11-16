"""Calibration functionals of a declared weighted empirical measure.

Weights and lineage are inputs, never inferred. Splits must preserve both
confidence and label. Weighted AUROC uses tie-aware mass pairing.
"""
import numpy as np

def metrics(c,y,w,bins=15):
 c=np.asarray(c,float);y=np.asarray(y,float);w=np.asarray(w,float)
 if c.ndim!=1 or not len(c) or c.shape!=y.shape or c.shape!=w.shape:raise ValueError('aligned nonempty vectors required')
 if not np.isfinite([c,y,w]).all() or (w<0).any() or w.sum()<=0:raise ValueError('finite values and positive total mass required')
 if ((c<0)|(c>1)).any() or not np.isin(y,[0,1]).all():raise ValueError('confidence in [0,1], binary outcomes required')
 w=w/w.sum();brier=float(np.sum(w*(c-y)**2))
 ix=np.minimum((c*bins).astype(int),bins-1)
 ece=float(sum(abs(np.sum(w[ix==b]*(y[ix==b]-c[ix==b]))) for b in range(bins)))
 order=np.argsort(c,kind='stable');c,y,w=c[order],y[order],w[order]
 pos=float(w[y==1].sum());neg=float(w[y==0].sum());wins=0.;below=0.
 for start in np.r_[0,np.flatnonzero(np.diff(c))+1]:
  stop=np.searchsorted(c,c[start],side='right');yy=y[start:stop];ww=w[start:stop]
  p=float(ww[yy==1].sum());n=float(ww[yy==0].sum());wins+=p*(below+.5*n);below+=n
 return {'brier':brier,'ece':ece,'auroc':wins/(pos*neg) if pos>0 and neg>0 else None}

def split(c,y,multiplicity):
 c=np.asarray(c);y=np.asarray(y);m=np.asarray(multiplicity)
 if m.shape!=c.shape or not np.issubdtype(m.dtype,np.integer) or (m<1).any():raise ValueError('positive integral multiplicities required')
 return np.repeat(c,m),np.repeat(y,m),np.repeat(1./m,m)
