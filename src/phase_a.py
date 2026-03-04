#!/usr/bin/env python3
"""Build 2 Phase A: Engine + Core Data (Table 1, counterexamples, null models, MI comparison)"""
from __future__ import annotations
import json, math, os, time
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from scipy.stats import beta as beta_dist

SEED_OFFSETS = {
    "random":0,"class_biased":100000,"overproduction":200000,"memorizer":300000,
    "compositional":400000,"strategic_random":500000,"ce1":600000,"ce2":700000,
    "ce3":800000,"matched_mem":900000,"matched_comp":1000000,
}
OUTDIR = os.environ.get("BRM_OUTDIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data"))
JSONDIR = os.path.join(OUTDIR, "json")
FIGDIR = os.path.join(OUTDIR, "figures")
os.makedirs(JSONDIR, exist_ok=True)
os.makedirs(FIGDIR, exist_ok=True)

def _log2(x): return math.log(x, 2) if x > 0 else 0.0

def compute_mi_both(cm, n_intents):
    cm = cm.astype(float); N = cm.sum()
    if N <= 0: return 0.0, 0.0
    Pj = cm/N; Py = Pj.sum(axis=1); Pz = Pj.sum(axis=0)
    mi = 0.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            p = Pj[i,j]
            if p > 0 and Py[i] > 0 and Pz[j] > 0:
                mi += p * _log2(p / (Py[i]*Pz[j]))
    Ky = int(np.sum(Py > 0)); Kz = int(np.sum(Pz > 0))
    bs = ((Ky-1)*(Kz-1)) / (2.0*N*math.log(2))
    K = n_intents; bf = ((K*K - K)) / (2.0*N*math.log(2))
    return max(0.0, mi - bs), max(0.0, mi - bf)

def clopper_pearson(k, n, alpha=0.05):
    if n == 0: return (0.0, 1.0)
    lo = beta_dist.ppf(alpha/2, k, n-k+1) if k > 0 else 0.0
    hi = beta_dist.ppf(1-alpha/2, k+1, n-k) if k < n else 1.0
    return (float(lo), float(hi))

def compute_f1_per_class(cm):
    n = cm.shape[0]; f1 = np.zeros(n)
    for i in range(n):
        tp = cm[i,i]; fp = cm[:,i].sum()-tp; fn = cm[i,:].sum()-tp
        pr = tp/(tp+fp) if (tp+fp) > 0 else 0.0
        rc = tp/(tp+fn) if (tp+fn) > 0 else 0.0
        f1[i] = (2*pr*rc/(pr+rc)) if (pr+rc) > 0 else 0.0
    return f1

def compute_veff(cm, alpha, beta_min):
    f1 = compute_f1_per_class(cm); counts = cm.sum(axis=1)
    return int(sum(1 for i in range(len(f1)) if f1[i] >= alpha and counts[i] >= beta_min))

@dataclass
class Metrics:
    accuracy: float = 0.0
    mi_support: float = 0.0; mi_full_ontology: float = 0.0
    b_min_support: float = 0.0; b_min_full: float = 0.0
    veff_60: int = 0; veff_70: int = 0; veff_80: int = 0; veff_90: int = 0
    c2: Optional[float] = None; c2_ci_lo: Optional[float] = None; c2_ci_hi: Optional[float] = None
    c2_k: int = 0; c2_n: int = 0; c2_chance: float = 0.0
    r: Optional[float] = None; r_total: int = 0; r_recovered: int = 0
    repair_dist: Optional[Dict[str, int]] = None
    u: Optional[float] = None; u_unknown_total: int = 0; u_unknown_correct: int = 0
    mean_duration: float = 0.5; n_episodes: int = 0

def compute_metrics(episodes, n_intents, veff_beta=30):
    cm = np.zeros((n_intents, n_intents), dtype=int); durations = []
    for ep in episodes:
        gt, dec = int(ep["gt"]), int(ep["decoded"])
        if 0 <= gt < n_intents and 0 <= dec < n_intents: cm[gt, dec] += 1
        durations.append(max(0.01, float(ep.get("duration", 0.5))))
    N = cm.sum(); acc = float(np.trace(cm)/N) if N > 0 else 0.0
    mi_s, mi_f = compute_mi_both(cm, n_intents)
    md = float(np.mean(durations)) if durations else 0.5
    c2_k, c2_n = 0, 0
    for ep in episodes:
        if ep.get("type") == "comp" and not ep.get("is_training", True):
            c2_n += 1; c2_k += int(bool(ep.get("correct", False)))
    c2_val = (c2_k/c2_n) if c2_n > 0 else None
    c2_lo, c2_hi = clopper_pearson(c2_k, c2_n) if c2_n > 0 else (None, None)
    rt, rr = 0, 0; rdist = {"repeat":0,"modify":0,"escalate":0,"abandon":0}
    for ep in episodes:
        if ep.get("type") == "repair":
            rt += 1; rr += int(bool(ep.get("recovered", False)))
            o = ep.get("outcome","abandon")
            if o in rdist: rdist[o] += 1
    r_val = (rr/rt) if rt > 0 else None
    ut, uc = 0, 0
    for ep in episodes:
        if ep.get("type") == "uncertainty" and ep.get("signals_unknown", False):
            ut += 1; uc += int(bool(ep.get("correct", False)))
    u_val = ((uc/ut) - 0.5) if ut > 0 else None
    return Metrics(accuracy=acc, mi_support=mi_s, mi_full_ontology=mi_f,
        b_min_support=mi_s/md if md > 0 else 0, b_min_full=mi_f/md if md > 0 else 0,
        veff_60=compute_veff(cm,.60,veff_beta), veff_70=compute_veff(cm,.70,veff_beta),
        veff_80=compute_veff(cm,.80,veff_beta), veff_90=compute_veff(cm,.90,veff_beta),
        c2=c2_val, c2_ci_lo=c2_lo, c2_ci_hi=c2_hi, c2_k=c2_k, c2_n=c2_n,
        c2_chance=1.0/n_intents, r=r_val, r_total=rt, r_recovered=rr,
        repair_dist=rdist, u=u_val, u_unknown_total=ut, u_unknown_correct=uc,
        mean_duration=md, n_episodes=len(episodes))

class Agent:
    def __init__(self, atype, nz, pc=0.85, pcc=0.90, rng=None):
        self.atype=atype; self.nz=nz; self.pc=pc; self.pcc=pcc
        self.rng = rng or np.random.default_rng()
        if atype == "class_biased":
            self.favored = set(self.rng.choice(nz, size=min(3,nz), replace=False).tolist())
        if atype == "overproduction": self.dominant = 0
        if atype == "strategic_random":
            self.neighbors = {z: [(z-1)%nz, (z+1)%nz] for z in range(nz)}
    def respond_single(self, gt):
        r=self.rng; t=self.atype
        if t=="random": return int(r.integers(0,self.nz))
        if t=="class_biased":
            if gt in self.favored: return gt if r.random()<0.90 else int(r.integers(0,self.nz))
            return int(r.integers(0,self.nz))
        if t=="overproduction":
            return self.dominant if r.random()<0.70 else (gt if r.random()<self.pc else int(r.integers(0,self.nz)))
        if t=="memorizer": return gt if r.random()<self.pc else int(r.integers(0,self.nz))
        if t in ("compositional","ce2","ce3"):
            return gt if r.random()<self.pcc else int(r.integers(0,self.nz))
        if t=="ce1": return gt if r.random()<0.90 else int(r.integers(0,self.nz))
        if t=="strategic_random":
            return gt if r.random()<0.70 else int(r.choice(self.neighbors[gt]))
        if t in ("matched_mem","matched_comp"):
            return gt if r.random()<self.pc else int(r.integers(0,self.nz))
        return int(r.integers(0,self.nz))
    def respond_comp(self, is_training):
        r=self.rng; t=self.atype
        if t in ("random","class_biased","overproduction"): return r.random()<(1.0/self.nz)
        if t in ("memorizer","ce1"): return r.random()<self.pc if is_training else r.random()<(1.0/self.nz)
        if t=="compositional": return r.random()<self.pcc
        if t in ("ce2","ce3"): return r.random()<0.85
        if t=="strategic_random": return r.random()<0.70 if is_training else r.random()<(1.0/self.nz)
        if t=="matched_mem": return r.random()<self.pc if is_training else r.random()<(1.0/self.nz)
        if t=="matched_comp": return r.random()<self.pc
        return False
    def respond_repair(self):
        r=self.rng; t=self.atype
        if t=="random": return str(r.choice(["repeat","modify","escalate","abandon"])), r.random()<(1.0/self.nz)
        if t in ("class_biased","overproduction","strategic_random"):
            return str(r.choice(["repeat","modify","escalate","abandon"],p=[.3,.2,.1,.4])), r.random()<(1.0/self.nz)
        if t in ("memorizer","ce1","ce2","matched_mem","matched_comp"):
            return str(r.choice(["repeat","modify","escalate","abandon"],p=[.5,.1,.1,.3])), r.random()<0.10
        if t in ("compositional","ce3"):
            o=str(r.choice(["repeat","modify","escalate","abandon"],p=[.2,.45,.2,.15]))
            return o, r.random()<{"modify":0.55,"repeat":0.20,"escalate":0.35,"abandon":0.0}[o]
        return "abandon", False
    def respond_unc(self, is_hard):
        r=self.rng; t=self.atype
        if t=="random": return r.random()<0.30, r.random()<0.50
        if t in ("class_biased","overproduction","memorizer","strategic_random",
                  "ce1","ce2","ce3","matched_mem","matched_comp"):
            return False, r.random()<(0.55 if is_hard else 0.90)
        if t=="compositional":
            if is_hard: return r.random()<0.60, r.random()<0.75
            return r.random()<0.10, r.random()<0.95
        return False, r.random()<0.50

@dataclass
class SimConfig:
    n_intents:int=12; n_episodes:int=500; p_correct:float=0.85; p_correct_comp:float=0.90
    class_imbalance:float=0.0; comp_split:float=0.80; comp_test_sample_frac:float=0.50
    hard_fraction:float=0.30; single_frac:float=0.50; comp_frac:float=0.15; repair_frac:float=0.20

def _zipf(n,s):
    if s<=0: return np.ones(n)/n
    ranks=np.arange(1,n+1,dtype=float); p=1.0/(ranks**s); return p/p.sum()

def run_sim(agent_type, cfg, seed):
    rng=np.random.default_rng(seed)
    agent=Agent(agent_type, cfg.n_intents, cfg.p_correct, cfg.p_correct_comp, rng=rng)
    probs=_zipf(cfg.n_intents, cfg.class_imbalance)
    ns=int(round(cfg.n_episodes*cfg.single_frac))
    nc=int(round(cfg.n_episodes*cfg.comp_frac))
    nr=int(round(cfg.n_episodes*cfg.repair_frac))
    nu=max(0, cfg.n_episodes-ns-nc-nr)
    eps=[]
    for _ in range(ns):
        gt=int(rng.choice(cfg.n_intents,p=probs)); dec=agent.respond_single(gt)
        dur=float(np.clip(rng.lognormal(np.log(0.5),0.4),0.05,3.0))
        eps.append({"type":"single","gt":gt,"decoded":dec,"duration":dur})
    nsl=min(cfg.n_intents//2, max(2, cfg.n_intents//3))
    sa=list(range(nsl)); sb=list(range(nsl, min(2*nsl, cfg.n_intents)))
    if not sb: sb=list(range(1, min(nsl+1, cfg.n_intents)))
    combos=[(a,b) for a in sa for b in sb]; rng.shuffle(combos)
    nt=max(1, int(round(len(combos)*cfg.comp_split)))
    tr_set=combos[:nt]; te_set=combos[nt:]
    if not te_set: te_set=[combos[-1]]; tr_set=combos[:-1]
    for _ in range(nc):
        if te_set and rng.random()<cfg.comp_test_sample_frac:
            combo=te_set[int(rng.integers(0,len(te_set)))]; is_tr=False
        else: combo=tr_set[int(rng.integers(0,len(tr_set)))]; is_tr=True
        correct=agent.respond_comp(is_tr); gt=int(combo[0])
        dec=gt if correct else int(rng.integers(0,cfg.n_intents))
        dur=float(np.clip(rng.lognormal(np.log(0.6),0.4),0.05,3.0))
        eps.append({"type":"comp","gt":gt,"decoded":dec,"duration":dur,"is_training":is_tr,"correct":bool(correct)})
    for _ in range(nr):
        gt=int(rng.choice(cfg.n_intents,p=probs)); dec=agent.respond_single(gt)
        outcome,recovered=agent.respond_repair()
        dur=float(np.clip(rng.lognormal(np.log(0.7),0.4),0.05,3.0))
        eps.append({"type":"repair","gt":gt,"decoded":dec,"duration":dur,"outcome":outcome,"recovered":bool(recovered)})
    for _ in range(nu):
        is_hard=rng.random()<cfg.hard_fraction; su,correct=agent.respond_unc(is_hard)
        gt=int(rng.choice(cfg.n_intents,p=probs))
        dec=gt if (su and correct) else (int(rng.integers(0,cfg.n_intents)) if su else agent.respond_single(gt))
        dur=float(np.clip(rng.lognormal(np.log(0.5),0.4),0.05,3.0))
        eps.append({"type":"uncertainty","gt":gt,"decoded":dec,"duration":dur,
                     "signals_unknown":bool(su),"correct":bool(correct),"is_hard":bool(is_hard)})
    return eps

def _sf(s0,at,i): return s0+SEED_OFFSETS.get(at,0)+i

def summarize(vals):
    if not vals: return {"mean":None,"std":None,"ci_lo":None,"ci_hi":None,"n":0}
    a=np.array(vals,dtype=float)
    return {"mean":round(float(np.mean(a)),6),"std":round(float(np.std(a)),6),
            "ci_lo":round(float(np.percentile(a,2.5)),6),"ci_hi":round(float(np.percentile(a,97.5)),6),"n":len(vals)}

def run_batch(atype, cfg, s0, nr, vb=30):
    keys=["accuracy","mi_support","mi_full_ontology","b_min_support","b_min_full",
          "veff_60","veff_70","veff_80","veff_90"]
    data={k:[] for k in keys}
    for k in ["c2","r","u","c2_ci_widths"]+[f"repair_dist_{c}" for c in ["repeat","modify","escalate","abandon"]]:
        data[k]=[]
    for i in range(nr):
        ep=run_sim(atype, cfg, _sf(s0,atype,i))
        m=compute_metrics(ep, cfg.n_intents, vb)
        for k in keys: data[k].append(float(getattr(m,k)))
        if m.c2 is not None:
            data["c2"].append(m.c2)
            if m.c2_ci_lo is not None and m.c2_ci_hi is not None:
                data["c2_ci_widths"].append(m.c2_ci_hi-m.c2_ci_lo)
        if m.r is not None: data["r"].append(m.r)
        if m.u is not None: data["u"].append(m.u)
        if m.repair_dist:
            rt=max(1,sum(m.repair_dist.values()))
            for c in ["repeat","modify","escalate","abandon"]:
                data[f"repair_dist_{c}"].append(m.repair_dist.get(c,0)/rt)
    return {k:summarize(v) for k,v in data.items()}

def _save(d, name):
    with open(os.path.join(JSONDIR,name),"w") as f: json.dump(d,f,indent=2,default=str)
    print(f"    -> {name}")

def main():
    s0=42; vb=30; n_t1=400; n_null=400; n_ce=400
    cfg=SimConfig()
    print("="*60); print("BUILD 2 PHASE A: Engine + Core Data"); print("="*60)
    t0=time.time()

    print("\n[REPRO]")
    e1=run_sim("memorizer",cfg,_sf(s0,"memorizer",0))
    e2=run_sim("memorizer",cfg,_sf(s0,"memorizer",0))
    m1=compute_metrics(e1,cfg.n_intents,vb); m2=compute_metrics(e2,cfg.n_intents,vb)
    assert m1.mi_support==m2.mi_support and m1.c2==m2.c2, "FAIL"
    print("  PASS")

    print(f"\n[TABLE 1] {n_t1} runs x 5 agents")
    t1={}
    for a in ["random","class_biased","overproduction","memorizer","compositional"]:
        t1[a]=run_batch(a,cfg,s0,n_t1,vb)
        print(f"  {a:20s} B={t1[a]['b_min_support']['mean']:.3f} C2={t1[a]['c2']['mean']!s:8s} "
              f"R={t1[a]['r']['mean']!s:8s} U={t1[a]['u']['mean']!s}")
    t1["config"]=asdict(cfg)
    _save(t1,"table1.json")

    print(f"\n[NULL MODELS] {n_null} runs")
    cb,op={},{}
    for s in [0.0,0.5,1.0,1.5]:
        c=SimConfig(**{**asdict(cfg),"class_imbalance":s})
        cb[str(s)]=run_batch("class_biased",c,s0,n_null,vb)
        op[str(s)]=run_batch("overproduction",c,s0,n_null,vb)
        print(f"  s={s}: CB acc={cb[str(s)]['accuracy']['mean']:.3f} B={cb[str(s)]['b_min_support']['mean']:.3f} | "
              f"OP acc={op[str(s)]['accuracy']['mean']:.3f} B={op[str(s)]['b_min_support']['mean']:.3f}")
    sr=run_batch("strategic_random",cfg,s0,n_null,vb)
    print(f"  strategic_random: B={sr['b_min_support']['mean']:.3f}")
    _save({"class_biased":cb,"overproduction":op,"strategic_random":sr},"null_models.json")

    print(f"\n[COUNTEREXAMPLES] {n_ce} runs")
    ce={}
    for c in ["ce1","ce2","ce3"]:
        ce[c]=run_batch(c,cfg,s0,n_ce,vb)
        print(f"  {c}: MI={ce[c]['mi_support']['mean']:.3f} C2={ce[c]['c2']['mean']!s:8s} "
              f"R={ce[c]['r']['mean']!s:8s} U_n={ce[c]['u']['n']}")
    chance=1.0/cfg.n_intents
    ce["verification"]={
        "ce1_high_mi_low_c2": (ce["ce1"]["mi_support"]["mean"] or 0)>1.5
            and (ce["ce1"]["c2"]["mean"] is None or ce["ce1"]["c2"]["mean"]<chance+0.10),
        "ce2_high_c2_low_r": (ce["ce2"]["c2"]["mean"] or 0)>0.50
            and (ce["ce2"]["r"]["mean"] or 1)<0.25,
        "ce3_high_r_no_u": (ce["ce3"]["r"]["mean"] or 0)>0.30 and ce["ce3"]["u"]["n"]==0,
    }
    for k,v in ce["verification"].items(): print(f"  {k}: {'PASS' if v else 'FAIL'}")
    _save(ce,"counterexamples.json")

    print("\n[MI COMPARISON]")
    mc={}
    for a in ["random","class_biased","overproduction","memorizer","compositional"]:
        ms=t1[a]["mi_support"]["mean"]; mf=t1[a]["mi_full_ontology"]["mean"]
        if ms is not None and mf is not None:
            d=abs(ms-mf); mc[a]={"support":ms,"full":mf,"diff":round(d,6)}
            print(f"  {a}: diff={d:.4f} {'OK' if d<0.05 else 'DIVERGES'}")
    _save(mc,"mi_comparison.json")

    elapsed=time.time()-t0
    print(f"\nPHASE A COMPLETE in {elapsed:.0f}s ({elapsed/60:.1f} min)")
    print(f"Files: {sorted(os.listdir(JSONDIR))}")

if __name__=="__main__":
    main()
