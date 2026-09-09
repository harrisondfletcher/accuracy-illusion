# Accuracy Illusion — Revision 4.1

## Authoritative documents

Use the three Version 4.1 files at this directory's top level: the revised manuscript, supplementary tables, and response to reviewers, each supplied as Markdown and editable Word. Figure captions and the change/verification report accompany them. The older drafts within scientific_archives are historical provenance only; do not substitute them for these revised documents.

## What changed

The requested reporting and proof corrections are applied. BCI model fits, predictions, and the original grid/power results are preserved. Missing uncertainty companions were recovered from the original 400 core runs per agent, not estimated or invented. The expanded BCI tables are exports of the frozen executed results. The trigger audit is now an actual supplied JSON artifact.

## Reproduce this reporting revision

Install the exact reporting dependencies in scripts/requirements-reporting.txt. Run:

```bash
python scripts/reproduce_revision.py
```

This replays the original core seeds to recover omitted fields, exports BCI tables, creates the timing audit, and rebuilds the Markdown documents. It does not refit either BCI decoder. To regenerate editable Word files, install Pandoc and run:

```bash
python scripts/reproduce_revision.py --word
```

Word files generated on another machine require a final visual layout check. The exact historical simulation and BCI archives are included under scientific_archives; they retain the original code, run records, environment information, and results. Raw EEG binaries are obtained from the official dataset source, not included in this reporting archive.

## Validate this reporting release

```bash
python scripts/validate_revision.py
```

The supplied validator checks the documents and recovered reporting evidence; it does not rerun EEG fitting or the original inferential streams.

## Evidence and scope

See REVISION_REPORT_v4_1.md and the JSON/CSV files under evidence. Source inputs and their hashes are included for traceability. The release manifest covers the delivered payload; it does not assert that the public GitHub repository has been updated.

## Remaining author-controlled submission details

Publish this revision and the supporting scientific release at a stable public release identifier before representing the project repository as containing it. The visible repository still describes the older release. Add the correspondence street address and telephone number required by the journal; these were not in the source materials. Confirm that the registration and declarations accurately reflect the author's records. No empirical BCI rerun is required for these administrative steps.
