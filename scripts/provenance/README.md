# Document provenance scripts

The scripts in this directory generated published documents in `docs/`. They are
kept so that each document's derivation is auditable and re-runnable, rather than
existing only as prose about how it was made.

They are **archival**, not maintained code. Each file is byte-identical to the copy
that produced the merged document. That byte-identity is the point: it is what
makes the reproduction check below meaningful. Reformatting them would trade a
reproduction proof for a style convention, so this directory is listed in
`extend-exclude` under `[tool.ruff]`, alongside the existing `legacy/v0`
entry.

## Contents

| Script | Produces | Merged in |
|---|---|---|
| `gen_t1_descriptive_report.py` | `docs/T1_DESCRIPTIVE_REPORT_V1.md` | #61, corrected §9.2 in #62 |
| `gen_t1_post_hoc_analysis.py` | `docs/T1_POST_HOC_ANALYSIS_V1.md` | #62 |
| `render_handbook_docx.py` | `handbook/CardioSentinel_Research_Execution_Handbook_v1.2.docx` | #66 |
| `gen_t2_arm_comparison_report.py` | `docs/experiments/t2/T2_ARM_COMPARISON_REPORT_V1.md` | this PR |

Source digests, as tracked:

```
178e16c08798cf6f811e1d762785a772a635a7f4e1edf0845ac2bf30f0343853  gen_t1_descriptive_report.py
c90954403382a884823d110e5fec089fcdacefc4caaf07de65e0f61e7dbb13fe  gen_t1_post_hoc_analysis.py
5b8104b42a0430d60302ef810318028c7e970689142f2797b250951e5d4c2487  render_handbook_docx.py
a516095b7686124dc879250bb184a5d5c425d88782111440d846cd8465d25daa  gen_t2_arm_comparison_report.py
```

**`gen_t2_arm_comparison_report.py`'s digest was stale on arrival, and stayed
that way.** It was recorded at `4faaf13`, and the generator was then amended
twice **inside the same pull request** -- `5c1da8a` (report descriptively rather
than omit) and `f06040b` (state the interval's post-selection boundary) --
without the record being refreshed. All three commits merged together in #72, so
the digest has been wrong on `master` from the moment it first appeared there.
Both amendments were intended; only the digest beside them was wrong.

The 2026-08-28 document relocation changed the generator source once more. It
kept the historical `AMENDMENT` string emitted into the frozen report and added
`AMENDMENT_PATH` for the current file that is opened. The report content stayed
unchanged; the source digest above records that intentional distinction.

**Nothing detected it, and the reason is worth recording.** No test asserts
these four digests, and `scripts/provenance/` is excluded from ruff, so no
automated reader visits this directory at all. **A provenance record that
nothing checks degrades exactly like the preservation guarantee in §47 does:
silently, with no failure to notice.** Refreshing the digest is a manual step in
any change to a generator until something asserts it.

## Reproducing

`gen_t2_arm_comparison_report.py` reads the promoted outer-validation artifacts
under `cardiosentinel-runs/phase8-t2-development-v1/t2-v1-outer-validation/` and
takes an optional run root as `argv[2]`, so it can be pointed at the evidence
from a worktree that does not contain it. It runs the plan's one authorized
derived analysis, which is 1,000 subject resamples scored twice over 473,897
rows -- **about nine minutes**, single-threaded. That cost is inherent to the
registered design, not a defect.

Unlike the T1 generators it is not byte-reproducible into an identical file on a
second run: it stamps the commit it was executed at. Every measured value is
deterministic (seed 2026) and was verified identical across two independent
runs; only the provenance line differs.


The two T1 generators read the promoted continuation artifacts under
`cardiosentinel-runs/phase9-t1-continuation-v1/t1-v1-measurement-continuation/`.
That tree is gitignored (`.gitignore`, `/cardiosentinel-runs/`), so **a fresh
checkout cannot run them**; they reproduce only on a machine holding the evidence,
or from the S3 evidence snapshot. They read JSON only. They open no `.npz` store,
no test partition, and write nothing into any run directory.

Both take the output path as `argv[1]` — write to a scratch path outside the repo
and diff, rather than overwriting the tracked document.

```bash
PY=/home/AI_POC/venvs/tactics/bin/python      # the scientific interpreter, 335 packages
cd <repo root>                                # gen_t1_post_hoc_analysis.py uses a RELATIVE run path

$PY scripts/provenance/gen_t1_descriptive_report.py  /tmp/r.md && diff /tmp/r.md docs/T1_DESCRIPTIVE_REPORT_V1.md
$PY scripts/provenance/gen_t1_post_hoc_analysis.py   /tmp/p.md && diff /tmp/p.md docs/T1_POST_HOC_ANALYSIS_V1.md
```

Both diffs are empty as of 2026-08-22. `gen_t1_descriptive_report.py` hardcodes an
absolute run path; `gen_t1_post_hoc_analysis.py` uses a path relative to the repo
root. This asymmetry is preserved rather than fixed, for the reason above.

`render_handbook_docx.py` takes `<source.md> <style-template.docx> <output.docx>`:

```bash
$PY scripts/provenance/render_handbook_docx.py \
    handbook/CardioSentinel_Research_Execution_Handbook_v1.2.md \
    handbook/CardioSentinel_Research_Execution_Handbook_v1.1.docx \
    /tmp/v12.docx
```

A regenerated `.docx` is **not** byte-identical to the tracked one — a `.docx` is a
zip, and the container records per-entry metadata. All 18 **parts** are byte-identical,
including `word/document.xml`, `word/styles.xml`, `word/theme/theme1.xml` and
`docProps/core.xml`. Compare parts, not zip bytes:

```python
import zipfile, hashlib
a, b = zipfile.ZipFile(regenerated), zipfile.ZipFile(tracked)
assert set(a.namelist()) == set(b.namelist())
for n in sorted(a.namelist()):
    assert hashlib.sha256(a.read(n)).hexdigest() == hashlib.sha256(b.read(n)).hexdigest(), n
```

The renderer keeps the template's styles, theme and `sectPr` and replaces only body
content, which is why fonts and theme are inherited rather than recreated. There is
no `pandoc` or `libreoffice` on the build host.

## Scope

These scripts render already-promoted values into prose. They compute no new
scientific quantity, with one exception that was authorized in advance: the
subject-macro mean of `episode_f1` in `gen_t1_descriptive_report.py`, per
`docs/T1_EVIDENCE_ANALYSIS_PLAN_V1.md` §7.7. Nothing here may be used to derive a
new metric, sweep a threshold, or read a partition a plan has not opened.
