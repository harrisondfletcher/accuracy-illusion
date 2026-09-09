# The Accuracy Illusion: Measuring What Accuracy Cannot in Communicative Behavior

**Harrison D. Fletcher**
Revision 4.1 for *Behavior Research Methods*, September 2026.

> DOI of this versioned release: [assigned upon OSF/Zenodo publication]

---

## Version history

| Version | Date | Status |
|---|---|---|
| Original submission (Supplementary Code S1) | March 2026 | Superseded. Its BCI results were **withdrawn** during revision; the original tree is preserved in this repository's git history (commit `73ce0bc`). |
| Revision 4 | September 2026 | Executed replacement BCI analysis (9 subjects, 2 decoders, frozen pre-evaluation design) plus rebuilt simulation/power program. Code in `code_revision4/`. |
| **Revision 4.1 (this release)** | September 2026 | Reporting/proof corrections on top of the frozen Revision-4 results. Package in `release_v4_1/`. **This is the release cited by the manuscript's Open Practices Statement.** |

The withdrawn original figures (including the former "compression" figure) and the
original engine remain available only in git history for provenance; they are not
part of the current release and must not be cited as current results.

## Layout

```
release_v4_1/    The Version 4.1 package: revised manuscript, supplement, response
                 letter (MD + DOCX), figures, reporting scripts, evidence
                 (recovered uncertainty summaries, BCI table exports,
                 TRIGGER_SCHEDULE_AUDIT.json, proof fixtures, diffs), source
                 inputs, release manifest, and the archived Revision-4
                 scientific packages (simulation package + executed BCI run) in
                 release_v4_1/scientific_archives/.
code_revision4/  The executed Revision-4 analysis code: simulation engine and
                 archived simulation results, BCI pipeline (direct local-MAT
                 adapter, explicit organizer artifact masks, six-fold
                 leave-one-source-run-out tuning), recomputing validator,
                 population scripts, tests, pinned requirements, and the audit
                 trail (protocol amendments, design freeze, claim-to-field map).
```

## Reproduce the Version 4.1 reporting revision

```bash
cd release_v4_1
pip install -r scripts/requirements-reporting.txt
python scripts/reproduce_revision.py     # replays core seeds, exports tables, rebuilds documents
python scripts/validate_revision.py      # 59-check validation of the shipped package
```

This does not refit either BCI decoder; the executed results are frozen.

## Reproduce the Revision-4 BCI analysis from raw data

See `code_revision4/` (pinned environment in `requirements-bci.txt`; moabb 1.7.1,
mne 1.12.1, scikit-learn 1.8.0, numpy 2.3.5, scipy 1.17.0, Python 3.12).
Raw EEG is not redistributed here; the 18 official MAT files are available from
https://bnci-horizon-2020.eu/database/data-sets/001-2014/ and are validated by
full parse + schema audit (`code_revision4/tools/acquire_bnci_mat.py`). The
evaluate phase verifies the archived pre-evaluation design fingerprint before
running.

## License

MIT (see LICENSE).
