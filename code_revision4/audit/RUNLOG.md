# BCI execution run log

- run_id: bci_20260909T031855Z
- utc_start: 2026-09-09T03:18:55Z
- machine: Darwin Harrys-MacBook-Air.local 24.5.0 Darwin Kernel Version 24.5.0: Tue Apr 22 19:54:43 PDT 2025; root:xnu-11417.121.6~2/RELEASE_ARM64_T8132 arm64
- operator agent: Claude Code (Opus 5)
- project_root: /Users/harrydog/Desktop/Accuracy Illusion/Accuracy_Illusion_Revision_v4
- raw MAT dir: /Users/harrydog/Desktop/Accuracy Illusion/raw_data/001-2014 (18 files, existing_local_file, downloaded from official BNCI URLs 2026-09-08 by this session)
- package zip: /Users/harrydog/Desktop/Accuracy_Illusion_Revision_v4.zip sha256=567c45a3bbb7067dc606c098bc1638be9366eac61f1aabc4c3dab80fa11d35cb bytes=1043670
- handoff: /Users/harrydog/Desktop/BCI_Completion_Handoff_Claude_Code_Codex.md
- runbook (audit reference): /Users/harrydog/Downloads/CLAUDE_CODE_BCI_RUNBOOK.md sha256=d345f06e2f07c7b4da04d6a94f657557c002be232d5dc31b69b7bf3fee50b169 (matches handoff §1.1)
- git baseline commit: 3fa8077a203cf6618dbd60f0a5690c7355576b12

## Package identity discrepancy (handoff §1.1)
Handoff-inspected zip: Accuracy_Illusion_Revision_v4_Package.zip bytes=1016133 sha256=0e91e64f117419c0260c5566ad191fc8852c7c6982defd8c72e64333bf3e548a
Supplied zip differs (name, 27,537 bytes larger, different hash). File tree matches handoff §1.2 listing; CLI surfaces match handoff §4.3 audit (verified: pipeline lacks --seed/--phase/--resume/--mat-dir; validator positional-only). Difference inventory: full per-file SHA-256 recorded at baseline git commit; no reference hashes for the inspected package's individual files are available, so the discrepancy is recorded as unresolvable to file granularity. Proceeding under documented assumption that this is a same-generation variant; every executed script's hash is logged.

## Pinned MOABB source verification (2026-09-08, pre-execution)
Fetched from raw.githubusercontent.com/NeuroTechX/moabb/v1.7.1:
- datasets/bnci/base.py sha256=920e327b8131bd6f63a6991863b4b69eff67a18075ea13da916aa09712cf5f5d
- datasets/bnci/bnci_2014.py sha256=ec4b3ce868bb839f6cc070de6e4ad1896e2c441dc127d89c4081b187da005d91
- paradigms/base.py sha256=355641c0aa4090760b17d06f9a5bd34565975c5d219fe0b3662a10602bac0dda
- datasets/preprocessing.py sha256=1556a29f8ff967241d477030ce06833cefec92d25e1e46bce305a20b2dd61bc0
Verified: label at trial-1 (trigger onset); interval=[2,6]; SetRawAnnotations shifts class annotations +interval[0]; artifact_handling="ignore" creates no annotations; "reject" with artifact_interval=None creates zero-duration BAD at trigger (outside 2.5-4.5s epoch => rejects nothing). Installed-package diff pending venv creation.

## Command log
(appended per command)

## Acquisition (utc 2026-09-09T03:24:10Z)
tools/acquire_bnci_mat.py: 18/18 validated by full MAT parse + schema audit.
A03E.mat: pre-existing local copy FAILED deep parse (zlib truncation from the
2026-09-08 disk-full interruption; 39,030,784 bytes, valid MAT header) and was
re-downloaded from the official URL; now passes. All other 17 reused as
existing_local_file. audit/raw_data_sha256.txt regenerated.

## Preflight audit finding (2026-09-09T03:36:13Z)
All 18 MAT files share one byte-identical within-run trigger-interval sequence
(282 intervals per session, 43 unique values, 7.580-8.480 s, mean 8.043149 s).
Verified independently of the adapter by direct scipy reads of A01T/A01E/
A05E/A09E. Interpretation: the Graz paradigm used a fixed pre-generated
randomized ITI schedule reused across subjects and sessions. Dataset property,
not an extraction defect; per handoff 7.2 recorded as an audit flag with
evidence. Consequence: tau_mean (B_min denominator) is identical for all
subjects.

## Completion (2026-09-09T04:01:16Z)
- Final evaluate: 9 subjects x 2 decoders, 10k/5k, seed 42; run 2026-09-09; final-mode validation PASS (713 checks).
- Documents populated (manuscript S6/abstract/15.4, S8 supplement, response letter + revision audit addenda); figures 2/4/S8 regenerated from validated JSON.
- Tests after: 39 passed. R4 simulation-artifact hash check: PASS.
- Release: bci_runs/bci_20260909T031855Z/release_staging (89 payload files), archive BCI_Completion_Release_bci_20260909T031855Z.zip sha256 de0f5e054c47f0051042bde24854cb27fe640a22390535075cb6710b86080bc0 (external sidecar).
- Status: BCI_COMPLETE_VALIDATED.

## Raw data relocated (2026-09-09)
raw_data/001-2014 MOVED to "/Users/harrydog/Desktop/Accuracy Illusion - Data
and reproduction/raw_data/001-2014" (disk constraint; single copy). All 18
hashes re-verified after the move. Future reruns: point --mat-dir there.

## Reviewer-response pass v2 (2026-09-09T15:52:48Z)
External review holes closed without touching pipeline/config/frozen design:
covariance clause + artifact counts + beta=30 statement in 6.1 (all classes
>=53); Table 1 abstention-rate row from archived table1.json (no sim rerun,
R4 PASS); Table 3b caption -> S8 per-subject curves; index arithmetic moved
to S8 methods note; abstract "by construction"; 2.2 stratified wording;
response letter past-tense with citations + three-defect disclosure block;
per-file trigger-schedule audit (18 files, ONE distinct interval vector,
audit/TRIGGER_SCHEDULE_AUDIT.json). Tests 39 pass. Release v2:
BCI_Completion_Release_bci_20260909T031855Z_v2.zip sha256 bddafc15... (v1 archive
retained unmodified). Reproduction package synced.

## v5 PUBLICATION sync (2026-09-09T16:02:19Z)
Merged the parallel 04:30 finalization pass's six documentary corrections
(all verified against the final JSON: FBCSP V_eff(.90)=3/9; sensitivity
V_eff shifts max 1 in 5 cells; stale pre-abstract execution-gate note found
and replaced) with the morning reviewer-pass v2 fixes. FINAL docs written to
Accuracy_Illusion_v5_PUBLICATION_FINAL_DOCS/ (manuscript, letter, audit,
new supplement FINAL); their runbook/protocol/finalization-audit FINALs
retained and copied into final/docs/. Merge note appended to
FINALIZATION_README.md. Tests 39 pass after merge.
