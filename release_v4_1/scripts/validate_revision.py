"""Validate the reporting release, not the original model fitting or inference."""
from pathlib import Path
import csv, hashlib, json, re, zipfile
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
checks = []
def check(name, condition, detail=None):
    checks.append({'name': name, 'passed': bool(condition), 'detail': detail})
    if not condition:
        raise AssertionError(f'{name}: {detail}')
def load(name):
    return json.loads((ROOT/'evidence'/name).read_text())
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

m=(ROOT/'The_Accuracy_Illusion_v4_1_REVISED.md').read_text()
s=(ROOT/'Supplementary_Tables_S0_S8_v4_1_REVISED.md').read_text()
r=(ROOT/'Response_to_Reviewers_v4_1_REVISED.md').read_text()
a=m.split('## Abstract',1)[1].split('**Keywords:',1)[0].strip()
check('abstract_word_limit',len(a.split())<=250,{'words':len(a.split()),'limit':250})
heads=re.findall(r'^## (.+)$',m,re.M)
check('open_practices_before_references',heads[heads.index('References')-1]=='Open Practices Statement')
for phrase in ['after its execution gates pass','execution-gated BCI shell','non-rejection for the remaining subjects','This table is not populated in the pre-execution revision']:
    check('stale_text_absent:'+phrase, phrase not in m+s)
check('set_difference_editable_markup',r'\smallsetminus' in m)
check('proposition_reference_scope','population' in m and 'reference-design' in m)
check('intermediate_noise_step',r'\epsilon_2-\epsilon_1' in m or r'\epsilon_2 - \epsilon_1' in m)
check('readable_ITR_table','S8d' in s and 'ITR' in s)
check('both_decoder_curves','FBCSP-style' in s and 'S8e' in s)
check('uncertainty_companions','S1b' in s and 'S1c' in s)
check('reviewer_defect_disclosures', all(x in r.lower() for x in ['contamination','class-biased','partition','common random']))

u=load('CORE_UNCERTAINTY_REPORT.json')
check('core_original_510_fields',u['provenance']['original_summary_fields_compared']==510)
check('core_original_fields_reproduced',u['provenance']['max_absolute_difference']<=1e-11,u['provenance']['max_absolute_difference'])
check('core_recovery_2000_original_runs',u['provenance']['run_count']==2000)
b=load('BCI_REPORTING_CHECKS.json')
check('BCI_108_point_checks',len(b['checks'])==108)
check('BCI_point_tolerance',max(x['absolute_difference'] for x in b['checks'])<1e-10)
check('BCI_18_prediction_hashes',b['prediction_hashes_verified']==18)
check('BCI_18_reconstructed_matrices',len(b['prediction_matrix_reconstruction'])==18)
t=load('TRIGGER_SCHEDULE_AUDIT.json')
check('timing_18_files_5184_trials',t['n_files']==18 and t['n_trials']==5184)
check('timing_identical_vectors',t['all_trigger_vectors_identical'])
check('timing_six_runs_48_trials',all(len(f['runs'])==6 and all(x['n_trials']==48 for x in f['runs']) for f in t['files']))
p=load('PROOF_FIXTURES.json')
check('displayed_equal_MI',p['absolute_difference']<1e-10)
check('noise_fixtures',p['intermediate_noise_kernel_identities_tested']==100)
p=load('PORTABLE_REPRODUCTION_TEST.json')
check('portable_reproduction_pass',p['exit_code']==0 and len(p['comparisons'])==7 and all(x['sha256_identical'] for x in p['comparisons']))
for item in p['comparisons']:
    check('portable_output_current:'+item['file'],sha(ROOT/item['file'])==item['sha256'])

ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
for doc in ROOT.glob('*.docx'):
    with zipfile.ZipFile(doc) as z:
        xml=ET.fromstring(z.read('word/document.xml'))
        rows=xml.findall('.//w:tr',ns)
        check(doc.stem+':no_split_table_rows',all(x.find('w:trPr/w:cantSplit',ns) is not None for x in rows),len(rows))
        tables=xml.findall('.//w:tbl',ns)
        check(doc.stem+':repeating_headers',all(x.find('w:tr/w:trPr/w:tblHeader',ns) is not None for x in tables),len(tables))
        raw=z.read('word/document.xml').decode()
        check(doc.stem+':no_tool_citation_tokens','filecite' not in raw and '' not in raw)
        check(doc.stem+':no_tracked_edits',not xml.findall('.//w:ins',ns) and not xml.findall('.//w:del',ns))
        if doc.name.startswith('The_Accuracy'):
            check(doc.stem+':editable_equations',len(xml.findall('.//m:oMath',ns))>=8)

# Compare every numerical cell from original main-text tables to the revised tables.
def tables(text):
    groups=[]; current=[]
    for line in text.splitlines()+['']:
        if line.startswith('|'):
            current.append(line)
        elif current:
            groups.append(current);current=[]
    return groups
old=(ROOT/'source_inputs/documents/manuscript_original.md').read_text()
num=lambda lines:re.findall(r'(?<![A-Za-z])[-+−]?\d+(?:\.\d+)?', '\n'.join(lines[2:]))
ot=tables(old);nt=tables(m)
# Table0 and comparisonTable4 are textual. All original numerical main tables have same order.
for idx in range(1,len(ot)-1):
    check(f'main_numerical_table_{idx}_preserved',num(ot[idx])==num(nt[idx]))

for srcname,dstname in [('manuscript_original.md','The_Accuracy_Illusion_v4_1_REVISED.md'),('supplement_original.md','Supplementary_Tables_S0_S8_v4_1_REVISED.md'),('response_original.md','Response_to_Reviewers_v4_1_REVISED.md')]:
    check(dstname+':not_identical_to_old',sha(ROOT/'source_inputs/documents'/srcname)!=sha(ROOT/dstname))

out={'scope':'Reporting and document consistency checks; not a claim of rerunning EEG fitting or inferential streams.', 'status':'PASS', 'checks':checks,'checks_passed':len(checks)}
(ROOT/'evidence/FINAL_VALIDATION_REPORT.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'status':'PASS','checks_passed':len(checks),'abstract_words':len(a.split())}))
