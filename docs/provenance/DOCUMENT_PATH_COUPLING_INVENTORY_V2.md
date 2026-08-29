# Document path-coupling inventory, V2

**Captured before the V2 move on 2026-08-29 from commit
`61cc553473180ce68f33bf9c3002addc74b20340`.** The search covered all tracked
text file types, explicit `Path` construction, repository-root joins and the
ignored run-artifact tree. Binary DOCX/PDF/PNG files were covered separately by
the byte receipt.

The complete literal-path inventory below groups repeated occurrences only
when they have the same owner and classification. Line numbers describe the
pre-move tree. No dynamically constructed coupling beyond the two category-A
Python expressions was found. No immutable run artifact contained any of the
three directory paths.

| Source and pre-move lines | Classification | Disposition |
|---|---|---|
| `.gitignore:46-47` | A — live path consumer | update ignore root |
| `paper/figures/make_f3_f4.py:24` | A — live path consumer | update repository/output construction |
| `tests/reproducibility/test_literature_citation_extraction.py:179-181` | A — live path consumer | update asserted manuscript path |
| `README.md:17,21,79,87,90` | B — living document | update |
| `docs/README.md:10,12,13,82` | B — living document | update |
| `docs/control-plane/ARCHITECTURE.md:21` | B — living document | append the V2 delta without rewriting the frozen baseline |
| `docs/control-plane/CURRENT_STATE.md:14,76,99,155,157` | B — living document | update |
| `scripts/literature_search.py:29` | B — living CLI usage | update |
| `scripts/provenance/README.md:20,94-95` | B — living provenance index | update current opened paths |
| `paper/PAPER_S2_RELATED_WORK_DRAFT.md:37` | B — live, non-frozen draft command | update |
| `paper/PAPER_S9_DISCUSSION_DRAFT.md:408` | B — live, non-frozen draft reference | update |
| `paper/TACTICS_SUBMISSION_ASSET_INVENTORY.md:8,17-21,27-34,46,61,67-69` | B — living submission inventory | update current paths only |
| `paper/TACTICS_SUBMISSION_METADATA_TO_COMPLETE.md:9` | B — living submission checklist | update |
| `paper/figures/README.md:9-10` | B — living generator instructions | update |
| `handoffs/README.md:8,12,77` | C — historical handoff index | preserve bytes; resolve through V2 |
| `audits/CARDIOSENTIN_DOCUMENTATION_DEMO_RECONCILIATION_V1.md:32-34,52-54,59-61,175,267-268` | C — historical audit | preserve |
| `audits/CARDIOSENTIN_POST_PR129_WORK_RECOVERY_V1.md:177,191,202-204,209` | C — historical audit | preserve |
| `audits/CARDIOSENTIN_RUNTIME_TRUST_BOUNDARY_HARDENING_V1.md:48,167,170,197` | C — historical audit | preserve |
| `audits/CARDIOSENTIN_SUBMISSION_FORMAT_REVIEW_V1.md:68,77,291` | C — historical audit | preserve |
| `audits/CARDIOSENTIN_SUBMISSION_HANDOFF_FORMAT_PENDING_V1.md:19,25,44,99,148,162` | C — historical audit | preserve |
| `audits/TACTICS_2026_SUBMISSION_REQUIREMENTS_V1.md:16` | C — historical audit | preserve |
| `docs/provenance/COMMIT_PIN_TRANSLATION_V1.md:829-844` | C — historical translation | preserve |
| `docs/provenance/DOCUMENT_PATH_TRANSLATION_V1.md:4,129,131-132,161` | C — historical translation | preserve exactly |
| `handoffs/CARDIOSENTINEL_HANDOFF_ECG17.md:4` through `ECG22.md:4` | C — historical handoffs | preserve bytes |
| `handoffs/CARDIOSENTINEL_HANDOFF_ECG23.md:4,152,214` | C — historical handoff | preserve bytes |
| `handoffs/CARDIOSENTINEL_HANDOFF_ECG24.md:4,76,78,91,117,119-120,126` | C — historical handoff | preserve bytes |
| `audits/CARDIOSENTIN_RELATED_WORK_VERIFICATION_V2.md:5,627` | D — digest-frozen verification | preserve |
| `docs/experiments/b4/B4_IMPROVEMENT_INVESTIGATION_BRIEF_V1.md:39` | D — frozen scientific record | preserve |
| Final manuscript and all handbook versions | D — content-frozen sources | move only; no source occurrence required editing |
| `cardiosentinel-runs/` | E — immutable artifact-recorded path | no occurrences found; no artifact edit |
| Natural-language uses of “paper”, “handbook” or “handoff” without a filesystem construction | F — false positive | no action |

The pre-move relative-link audit found zero local Markdown links in the 45
moved Markdown files. Consequently none of the frozen sources requires a byte
change to preserve link resolution. Historical inline path strings are resolved
through `DOCUMENT_PATH_TRANSLATION_V1.md` followed by V2; they are not links and
are not rewritten.
