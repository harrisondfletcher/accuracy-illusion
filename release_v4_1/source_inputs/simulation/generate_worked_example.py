"""Generate Supplementary Data S2 and its manuscript summary from one deterministic source."""
from __future__ import annotations
import csv, json, math, os
from pathlib import Path
import numpy as np
from scipy.stats import fisher_exact
from engine_v2 import mi_plugin_and_mm, f1_per_class, veff, clopper_pearson
from metrics_u import u_selectivity, u_newcombe_ci

HERE = Path(__file__).resolve().parent
OUT = HERE / "data"
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(42)
K = 12
rows = []

# Base channel: exactly 50 trials/intent with deliberately heterogeneous reliability.
p_correct = np.array([.94,.92,.90,.88,.86,.84,.82,.80,.78,.74,.70,.66])
episode = 0
for y in range(K):
    for _ in range(50):
        correct = rng.random() < p_correct[y]
        z = y if correct else (y + rng.integers(1, K)) % K
        duration = float(np.clip(rng.lognormal(np.log(.45), .18), .20, .90))
        rows.append(dict(episode_id=episode, channel="base", ground_truth=y, decoded_intent=z,
                         duration_min=duration, is_training="", correct=int(correct), repair_outcome="",
                         recovered="", abstained="", forced_commit_error=""))
        episode += 1

# Compositional channel: 16 training (14 correct), 4 held-out (3 correct).
train_correct = [1]*14 + [0]*2; held_correct = [1]*3 + [0]
rng.shuffle(train_correct); rng.shuffle(held_correct)
for is_training, values in [(1, train_correct), (0, held_correct)]:
    for j, correct in enumerate(values):
        rows.append(dict(episode_id=episode, channel="compositional", ground_truth=f"combo_{is_training}_{j}",
                         decoded_intent="", duration_min="", is_training=is_training, correct=correct,
                         repair_outcome="", recovered="", abstained="", forced_commit_error=""))
        episode += 1

# Repair: fixed secondary distribution and exactly 42/120 recovered.
outcomes = ["repeat"]*54 + ["modify"]*36 + ["escalate"]*12 + ["abandon"]*18
rng.shuffle(outcomes)
recovered = np.array([1]*42 + [0]*78); rng.shuffle(recovered)
for outcome, rec in zip(outcomes, recovered):
    rows.append(dict(episode_id=episode, channel="repair", ground_truth="intent_known", decoded_intent="",
                     duration_min="", is_training="", correct="", repair_outcome=outcome,
                     recovered=int(rec), abstained="", forced_commit_error=""))
    episode += 1

# Uncertainty: 40 forced-commit errors; 18/40 abstained. 7/160 abstained among correct.
err = np.array([1]*40 + [0]*160)
abst = np.zeros(200, dtype=int)
err_idx = np.flatnonzero(err); ok_idx = np.flatnonzero(~err.astype(bool))
abst[rng.choice(err_idx, 18, replace=False)] = 1
abst[rng.choice(ok_idx, 7, replace=False)] = 1
perm = rng.permutation(200)
for e, a in zip(err[perm], abst[perm]):
    rows.append(dict(episode_id=episode, channel="uncertainty", ground_truth="forced_choice", decoded_intent="",
                     duration_min="", is_training="", correct="", repair_outcome="", recovered="",
                     abstained=int(a), forced_commit_error=int(e)))
    episode += 1

fields = ["episode_id","channel","ground_truth","decoded_intent","duration_min","is_training","correct",
          "repair_outcome","recovered","abstained","forced_commit_error"]
with (OUT / "S2_worked_example.csv").open("w", newline="") as f:
    w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

base=[r for r in rows if r["channel"]=="base"]
cm=np.zeros((K,K),int)
for r in base: cm[int(r["ground_truth"]),int(r["decoded_intent"])]+=1
mi_plugin, mi, _=mi_plugin_and_mm(cm)
tau=float(np.mean([r["duration_min"] for r in base]))
f1=f1_per_class(cm)
comp_held=[r for r in rows if r["channel"]=="compositional" and r["is_training"]==0]
k=sum(int(r["correct"]) for r in comp_held); n=len(comp_held)
rep=[r for r in rows if r["channel"]=="repair"]
unc=[r for r in rows if r["channel"]=="uncertainty"]
a=np.array([int(r["abstained"]) for r in unc]); e=np.array([int(r["forced_commit_error"]) for r in unc])
u=u_selectivity(a,e); uci=u_newcombe_ci(a,e)
summary={
    "seed":42,"n_total":len(rows),"n_base":len(base),"confusion_matrix":cm.tolist(),
    "mi_plugin_bits":mi_plugin,"mi_corrected_bits":mi,"tau_mean_min":tau,"b_min_bpm":mi/tau,
    "f1_per_class":f1.tolist(),"veff_curve":{str(x):veff(cm,x,30) for x in (.60,.70,.80,.90)},
    "c2":k/n,"c2_n":n,"c2_ci":clopper_pearson(k,n),
    "r":sum(int(r["recovered"]) for r in rep)/len(rep),"r_n":len(rep),
    "repair_distribution":{o:sum(r["repair_outcome"]==o for r in rep)/len(rep) for o in ("repeat","modify","escalate","abandon")},
    "u":u,"u_ci":uci,"u_fisher_p":float(fisher_exact([[int(a[e==1].sum()),int((1-a[e==1]).sum())],[int(a[e==0].sum()),int((1-a[e==0]).sum())]])[1]),
    "abstain_rate":float(a.mean()),"u_n_error":int(e.sum()),"u_n_correct":int((1-e).sum()),
    "u_abstain_error":int(a[e==1].sum()),"u_abstain_correct":int(a[e==0].sum())
}
with (OUT / "S2_worked_example_summary.json").open("w") as f: json.dump(summary,f,indent=1)
print(json.dumps(summary,indent=2))
