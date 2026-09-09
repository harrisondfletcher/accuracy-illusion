from pathlib import Path
import sys, json, hashlib, csv, math, shutil
import numpy as np
import tempfile, zipfile
OUT=Path(__file__).resolve().parents[1]
# The verification and data export use frozen input archives; no internet or EEG refit.
TMP=tempfile.TemporaryDirectory(prefix="accuracy-v41-")
ROOT=Path(TMP.name)
for archive, dest in [("Accuracy_Illusion_Revision_v4_Package.zip", "simulation"), ("bci_20260909T031855Z.zip", "bci")]:
    with zipfile.ZipFile(OUT/"scientific_archives"/archive) as z:
        for name in z.namelist():
            if name.endswith("/") or name.endswith(".zip") or "__MACOSX" in name or name.endswith(".DS_Store"):
                continue
            target=(ROOT/dest/name).resolve()
            if not target.is_relative_to((ROOT/dest).resolve()):
                raise ValueError("Unsafe archive member")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(name))
SIM=ROOT/'simulation/Accuracy_Illusion_Revision_v4'
BCI=ROOT/'bci/bci_20260909T031855Z/release_staging' 
for sub in ['evidence','scripts','figures','source_inputs/simulation','source_inputs/bci']:
 (OUT/sub).mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(SIM))
from engine_v2 import SimConfig, run_sim, SEED_OFFSET
sha=lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=json.loads((SIM/'results/table1.json').read_text())
cfg=SimConfig(**old['config'])
core=['random','class_biased','overproduction','memorizer','compositional']
records=[]; summaries={}; compared=[]
keys=['accuracy_base','accuracy_pooled','mi_plugin','mi','b_min','c2','r','u','abstain_rate']
extra=['u_tpr','u_fpr','u_n_err','u_n_ok']
for agent in core:
 off=old['paired_base_seed_offset'] if agent in ['memorizer','compositional'] else SEED_OFFSET[agent]
 rows=[]
 for i in range(400):
  seed=42+off+i; r=run_sim(agent,cfg,seed)
  row={'agent':agent,'run_index':i,'seed':seed,**{k:getattr(r,k) for k in keys+extra}}
  row['commitment_coverage']=1-r.abstain_rate
  row['uncertainty_trials']=r.n_alloc[3]
  for a in [.6,.7,.8,.9]: row[f'veff_{int(a*100)}']=r.veff[a]
  for outcome,value in r.repair_dist.items(): row['repair_'+outcome]=value
  assert r.u_n_err+r.u_n_ok==row['uncertainty_trials']
  if np.isfinite(r.u): assert abs(r.u-r.u_tpr+r.u_fpr)<1e-14
  rows.append(row)
 records.extend(rows)
 d={}
 for k in keys+extra+['commitment_coverage','uncertainty_trials']+[f'veff_{a}' for a in [60,70,80,90]]+['repair_'+x for x in ['repeat','modify','escalate','abandon']]:
  a=np.asarray([r[k] for r in rows],float); good=a[np.isfinite(a)]
  vals={'mean':float(good.mean()),'sd':float(good.std(ddof=1)),
    'ci_lo':float(np.percentile(good,2.5)),'ci_hi':float(np.percentile(good,97.5)),
    'min':float(good.min()),'max':float(good.max()),'n':len(good),'n_nan':len(a)-len(good)}
  d[k]=vals
  if k in old[agent] and isinstance(old[agent][k],dict):
   for f in ['mean','sd','ci_lo','ci_hi','n','n_nan']:
    err=abs(vals[f]-old[agent][k][f])
    assert err<1e-11,(agent,k,f,err,vals[f],old[agent][k][f])
    compared.append({'agent':agent,'metric':k,'field':f,'absolute_difference':err})
 summaries[agent]=d
 print(agent, 'U',d['u']['mean'],'n_error',d['u_n_err']['mean'],'n_correct',d['u_n_ok']['mean'],'tpr',d['u_tpr']['mean'],'fpr',d['u_fpr']['mean'])
with (OUT/'evidence/core_uncertainty_runs.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=records[0].keys());w.writeheader();w.writerows(records)
res={'provenance':{'description':'Deterministic replay of the original 400 core runs per agent using the archived engine and exact original seed offsets. Only previously unreported summaries added; source engine unchanged.', 'engine_sha256':sha(SIM/'engine_v2.py'),'source_table1_sha256':sha(SIM/'results/table1.json'),'seed0':42,'config':old['config'],'paired_seed_offset':old['paired_base_seed_offset'],'run_count':2000,'original_summary_fields_compared':len(compared),'max_absolute_difference':max(x['absolute_difference'] for x in compared)},'summaries':summaries,'comparison':compared}
(OUT/'evidence/CORE_UNCERTAINTY_REPORT.json').write_text(json.dumps(res,indent=2))
for f in ['engine_v2.py','run_simulations.py','requirements-simulation.txt']:
 shutil.copy2(SIM/f,OUT/'source_inputs/simulation'/f)
shutil.copy2(SIM/'results/table1.json',OUT/'source_inputs/simulation/table1.json')
# BCI point-metric and interval-source export, not model refitting or resampling.
j=json.loads((BCI/'results/bci_real_application_v4.json').read_text())
classes=j['class_order']
checks=[]; bro=[]; reconstructed=[]
for s,sj in j['subjects'].items():
 for dec,d in sj['decoders'].items():
  if dec not in ['primary','fbcsp']:continue
  pred=BCI/'predictions'/Path(d['prediction_file']).name
  assert sha(pred)==d['prediction_sha256']
  with pred.open() as f: ps=list(csv.DictReader(f))
  rebuilt=np.zeros((4,4),int)
  class_index={label:i for i,label in enumerate(classes)}
  for row in ps: rebuilt[class_index[row['true_class']],class_index[row['predicted_class']]] += 1
  assert rebuilt.tolist()==d['confusion_matrix']
  reconstructed.append({'subject':s,'decoder':dec,'n':len(ps),'matrix_exact_match':True})
  cm=rebuilt;N=cm.sum()
  P=cm/N; py=P.sum(1);pz=P.sum(0);mask=P>0
  plugin=float((P[mask]*np.log2((P/(py[:,None]*pz[None,:]))[mask])).sum())
  correction=((cm>0).sum()-(cm.sum(1)>0).sum()-(cm.sum(0)>0).sum()+1)/(2*N*np.log(2))
  corrected=plugin-correction;acc=float(np.trace(cm)/N)
  f1=np.divide(2*np.diag(cm),cm.sum(1)+cm.sum(0),out=np.zeros(4),where=(cm.sum(1)+cm.sum(0))>0)
  b=corrected*60/d['tau_mean_sec']
  itr=60/d['tau_mean_sec']*(2+acc*math.log2(acc)+(1-acc)*math.log2((1-acc)/3))
  for field,v in [('mi_plugin_bits',plugin),('mi_mm_correction_bits',correction),('mi_corrected_bits',corrected),('accuracy',acc),('b_min_bpm',b),('itr_bpm',itr)]:
   er=abs(d[field]-v);assert er<1e-10,(s,dec,field,er)
   checks.append({'subject':s,'decoder':dec,'field':field,'absolute_difference':er})
  for a in [.4,.5,.6,.7,.8,.9]:
   val=int(np.sum((f1>=a)&(cm.sum(1)>=30)));assert val==d['veff_curve'][str(a)]
  bro.append({'subject':s,'decoder':dec,'n':int(N),'accuracy':acc,'kappa':d['kappa'],'mi_plugin_bits':plugin,'mm_correction_bits':correction,'mi_corrected_bits':corrected,'tau_sec':d['tau_mean_sec'],'b_min_bpm':b,'itr_bpm':itr,**{'veff_'+str(a):d['veff_curve'][str(a)] for a in [.4,.5,.6,.7,.8,.9]}})
# source ledger timing audit per file and run, with exact integer comparisons
with (BCI/'results/trial_ledger.csv').open() as f: ledger=list(csv.DictReader(f))
assert len(ledger)==5184
byfile={}
for row in ledger: byfile.setdefault(row['source_file'],[]).append(row)
assert len(byfile)==18
reference=None;file_audits=[]
for file,rows in sorted(byfile.items()):
 byrun={}
 for r in rows:byrun.setdefault(int(r['task_run_index']),[]).append(r)
 assert len(byrun)==6
 rr=[];all_int=[]; vectors=[]
 for run,rs in sorted(byrun.items()):
  rs.sort(key=lambda r:int(r['within_run_trial_index']))
  assert len(rs)==48
  tr=[int(r['trial_sample_zero_based']) for r in rs]
  dif=np.diff(tr).tolist();vectors.append(tr);all_int+=dif
  assert all(int(r['cue_sample_zero_based'])-int(r['trial_sample_zero_based'])==500 for r in rs)
  assert all(int(r['epoch_start_sample'])-int(r['trial_sample_zero_based'])==625 for r in rs)
  assert all(int(r['epoch_stop_sample_inclusive'])-int(r['trial_sample_zero_based'])==1125 for r in rs)
  rr.append({'task_run_index':run,'n_trials':48,'trigger_samples_zero_based':tr,'within_run_intervals_samples':dif})
 if reference is None:reference=vectors
 assert vectors==reference,file
 interval=np.array(all_int)/250.;assert len(interval)==282
 file_audits.append({'source_file':file,'source_sha256':rows[0]['source_file_sha256'],'session':rows[0]['session_T_or_E'],'matches_reference_trigger_vectors':vectors==reference,'runs':rr,'n_intervals':282,'mean_interval_sec':float(interval.mean()),'sample_sd_sec':float(interval.std(ddof=1)),'min_interval_sec':float(interval.min()),'max_interval_sec':float(interval.max())})
 if rows[0]['session_T_or_E']=='E':
  sid='S'+str(int(rows[0]['subject'].lstrip('S')))
  assert np.allclose(interval,j['subjects'][sid]['evaluation_within_run_intervals_sec'],atol=0,rtol=0)
audit={'scope':'Post-execution comparison of all 18 source-file trigger schedules using the archived 5,184-trial ledger. MAT binaries were not reread in this reporting revision. File identifiers and source hashes are inherited from the executed acquisition audit.','source_ledger_sha256':sha(BCI/'results/trial_ledger.csv'),'source_result_sha256':sha(BCI/'results/bci_real_application_v4.json'),'n_files':18,'n_trials':5184,'reference_file':file_audits[0]['source_file'],'all_trigger_vectors_identical':True,'sampling_rate_hz':250,'files':file_audits}
(OUT/'evidence/TRIGGER_SCHEDULE_AUDIT.json').write_text(json.dumps(audit,indent=2))
(OUT/'evidence/BCI_REPORTING_CHECKS.json').write_text(json.dumps({'scope':'Point-metric reconstruction and export; no new decoder fitting or bootstrap/permutation replay.','checks':checks,'prediction_hashes_verified':18,'prediction_matrix_reconstruction':reconstructed,'source_result_sha256':sha(BCI/'results/bci_real_application_v4.json')},indent=2))
with (OUT/'evidence/BCI_EXTENDED_TABLES.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=bro[0]);w.writeheader();w.writerows(bro)
for name in ['bci_real_application_v4.json','trial_ledger.csv','source_inventory.json']:
 shutil.copy2(BCI/'results'/name,OUT/'source_inputs/bci'/name)
for name in ['DESIGN_FREEZE.json','PROTOCOL_AMENDMENTS.md']:
 shutil.copy2(BCI/'audit'/name,OUT/'source_inputs/bci'/name)
# Copy all frozen prediction records for a self-contained reporting comparison.
shutil.copytree(BCI/'predictions',OUT/'source_inputs/bci/predictions',dirs_exist_ok=True)

print('PASS',len(compared),'original core summary fields preserved;',len(checks),'BCI point comparisons; 18 schedules match.')
