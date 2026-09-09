# Revision 4.1 — Change and verification report

## Scope

This package applies the outstanding manuscript, supplement, proof, and rendering corrections to the latest uploaded Version 4 documents. It preserves the completed BCI model fits and frozen predictions. It does not claim a new BCI experiment, a new 480-cell grid, or a new power study.

## Source-derived versus newly generated material

The primary and FBCSP-style empirical results, original simulation profile values, grid summaries, and power cells are source-derived and retained. New numerical material consists of (a) missing uncertainty companions recovered by replaying the exact original core-run seeds, (b) table exports from the already executed BCI JSON, and (c) a trigger-schedule comparison derived from the archived ledger. Mathematical repairs and their scope qualifiers are revisions to exposition/proofs; they are not new empirical findings.

## Completed corrections

- Abstract shortened to 228 whitespace-delimited words, including corrected decoder-specific threshold language.
- Propositions 1, 3, and 4 clarified; set difference represented as editable mathematics.
- S1b–S1c now contain actual core-run conditional abstention rates, coverage, and error/non-error denominator summaries.
- Readable ITR comparison, both decoder threshold curves, and subject-specific MI corrections added to S8.
- Existing power sensitivities at uncertainty error fractions .10 and .35 and the presence-contrast intervals now displayed in S7e–S7g.
- Stale execution-gated/unpopulated language removed; no reference to nonexistent remaining subjects.
- Open Practices Statement added immediately before References, without an invented public registration claim.
- Response letter updated with all reviewer points and explicit disclosures of the inert split, cross-channel contamination, Class-Biased mismatch, and common-random-number correction.
- Word generation uses one-inch margins, double-spaced main prose, upper-right page numbers, editable equations, repeating table headers, and non-splitting data rows. The supplement uses landscape pages for readable wide tables.

## Verification performed for this revision

The original 400 runs for each of five core agents were replayed with the unchanged archived engine and identical seed offsets. All 510 compared fields of the original summaries matched within 1e-11; actual maximum difference is recorded in CORE_UNCERTAINTY_REPORT.json. The recovery adds fields, not independent replications or increased sample size.

All 18 saved subject/decoder confusion matrices were reconstructed from their clean prediction CSVs and matched the final BCI JSON. Prediction hashes were checked. Independent point-metric arithmetic reproduces MI components, accuracy, B_min, and ITR; every exported threshold count matches class F1 and support. Confidence intervals and permutation exceedances were retained from the frozen executed outputs, not rerun in this edit.

All 18 ledger-derived source-file trigger schedules contain six runs with 48 triggers each, yielding 282 within-run intervals per file. The exact six trigger vectors match across files, and evaluation intervals match the result JSON. The audit explicitly states that raw MAT binaries were not reread in this reporting revision.

The numerical equal-MI construction and 100 intermediate-noise kernel identities were checked. Algebraic justification appears in the manuscript; numerical fixtures are corroboration only.

## Additional local precision changes, disclosed explicitly

- Reference-design population scope, support eligibility, and explicit behavioral-channel assumptions in Proposition 4.
- Arbitrary intermediate-noise channel composition in Proposition 1.
- Population MI separated from corrected finite-sample estimators throughout.
- Exchangeability conditions on permutation inference; no assertion that equal scalar MI or rate alone makes labels exchangeable.
- Nondifferential-labeling Markov condition and no universal accuracy-attenuation claim in Section 9.
- Comparison table scoped to aggregate base-channel scores; MI is not claimed to identify intended-label correctness under a bijective relabeling.

These changes resolve overbroad wording while preserving the four-channel measurement architecture and reported experimental outcomes.

## Detailed edit log

1. Version identifier changed to 4.1; empirical analyses retained.
2. Replaced the execution-status box with a concise availability statement; kept withdrawn-analysis history in the response letter.
3. Abstract shortened to 228 whitespace-delimited words; corrected threshold counts and scoped the population proof.
4. Scoped introductory nonrecoverability claim to the construction actually proved.
5. Narrowed the introductory accuracy example to the information supplied by its design, without an unsupported claim about all standard metrics.
6. Distinguished population MI in proofs from sample estimates and their corrections.
7. Clarified design-respecting resampling and permutation-null assumptions.
8. Repaired the set-difference expression using editable mathematical markup.
9. Separated the held-out-set symbol from uncertainty selectivity U.
10. Qualified the compositional chance baseline to its actual null model.
11. Completed the uncertainty reporting contract.
12. Replaced Proposition 4 with the demonstrated nondegenerate reference-design population theorem; added explicit witnesses, assumptions, and estimator distinction.
13. Removed a misleading characterization of the synthetic covariance design.
14. Completed Proposition 1 with the arbitrary intermediate-noise comparison.
15. Aligned the C_k bounds paragraph with the explicit chance model.
16. Defined exact equality through the entropy root while preserving the displayed numerical example.
17. Aligned Section 4.3 with the restricted population theorem.
18. Distinguished the generator correctness parameter from realized accuracy.
19. Clarified that total support alone does not guarantee per-class support under random allocation.
20. Pointed Table 1 to the recovered core-run uncertainty companion tables, not the separate S2 example.
21. Moved revision history and implementation fingerprint out of the main BCI opening; retained explicit replacement-run scope.
22. Added evaluation exclusion totals and class-support range; shortened main-text implementation prose.
23. Kept explicit executed covariance regularization and tuning while removing log-style prose.
24. Corrected the ITR cross-reference to a newly populated readable table.
25. Removed the nonexistent remaining-subjects phrase and preserved the exploratory pair-selection disclosure.
26. Replaced residual editing instructions about pooling with the executed reporting statement.
27. Added explicit reference to both decoder threshold tables.
28. Clarified decoder-specific threshold results and separated descriptive contrasts from confirmatory within-subject tests.
29. Removed the conflict between population matrices and the blanket correction statement.
30. Clarified the null required by system-label permutation without changing any executed test.
31. Propagated the theorem scope into the discussion.
32. Removed obsolete future-tense execution language and retained domain-validity limits.
33. Removed rhetorical revision-history wording from the discussion.
34. Replaced an untested interpolated R planning threshold with the actual tested cells.
35. Made the existing measurement-error argument mathematically explicit; removed unsupported universal accuracy attenuation. No empirical calculation changed.
36. Scoped the comparison table to base-channel scalar reporting.
37. Corrected the MI-versus-label-correctness row without changing the proposed suite.
38. Added structured declarations and the Open Practices Statement immediately before References; did not invent a public registration or claim the new release was uploaded.
39. Updated supplement inventory for the recovered uncertainty tables.
40. Updated supplement inventory to the actual completed contents.
41. Removed obsolete after-execution language from figure inventory.
42. Removed obsolete future execution phrase from confusion-figure inventory.

## External submission guidance checked

Behavior Research Methods' official instructions were checked on September 9, 2026: abstract no more than 250 words; main text double spaced with one-inch margins and upper-right page numbers; Open Practices Statement immediately before References. Source: https://link.springer.com/journal/13428/submission-guidelines.

The public project page at https://github.com/harrisondfletcher/accuracy-illusion was accessible, but its visible README still described older settings, including 20 power experiments and 50 bootstrap samples. The current reporting package has not been uploaded to that repository by this edit. The Open Practices Statement therefore does not claim that the unversioned project page already contains this release.

## Author-controlled release details

The source files do not provide a correspondence street address or telephone number; neither was invented. Those title-page details and the definitive public repository/release identifier remain author-controlled. No public preregistration is claimed because the available evidence establishes a local freeze, not a public registration record. Authors should ensure the eventual submission record describes their actual registration and tool-use history.

This change report is a scoped verification record, not a guarantee of editorial acceptance or a claim that every possible methodological criticism has been eliminated.

## Final document and portable-reproduction verification

The portable reporting pipeline was executed successfully from a separate copy of the package. All three Markdown manuscripts and four principal numerical/reporting outputs reproduced byte-for-byte (seven comparisons). The reporting consistency validator passed 59 checks. The three Word files were rendered and all 69 pages were visually inspected (43 manuscript, 16 supplementary tables, 10 response letter). The missing set-difference operator is now visible; table data rows are not split. Automated text-bound and error-glyph scans found no candidates. All 12 existing figure files were verified unchanged against the uploaded figure archive. See PORTABLE_REPRODUCTION_TEST.json, FINAL_VALIDATION_REPORT.json, WORD_RENDER_QA.json, and FIGURE_PRESERVATION.json.
