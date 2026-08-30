# Audits

A review that was **run**, kept as it was written.

An audit here answers a question about the repository's own state — is the
manuscript ready, do the cited works exist, does the runtime hold its trust
boundary, did a migration move what it claimed to move. Each names its date, its
branch and the commits it read, so a reader can check it rather than believe it.

**They are not edited afterwards.** An audit tidied to match what was learned
later stops being evidence of what was known at the time. Where a later audit
changes a finding it supersedes the earlier one and says so in its own header;
the earlier one stays where it is.

This index is the one file here that changes.

## The records

### 2026-08-28 — the submission run

| Record | Subject | Outcome |
|---|---|---|
| [`CARDIOSENTINEL_PAPER_READINESS_AUDIT_V1.md`](CARDIOSENTINEL_PAPER_READINESS_AUDIT_V1.md) | paper readiness, read only from frozen reports and receipts | partly superseded — see below |
| [`CARDIOSENTIN_RELATED_WORK_VERIFICATION_V1.md`](CARDIOSENTIN_RELATED_WORK_VERIFICATION_V1.md) | related work and gap stress-test | **superseded by V2** |
| [`CARDIOSENTIN_RELATED_WORK_VERIFICATION_V2.md`](CARDIOSENTIN_RELATED_WORK_VERIFICATION_V2.md) | related work, and literature-provenance hardening | current |
| [`TACTICS_2026_SUBMISSION_REQUIREMENTS_V1.md`](TACTICS_2026_SUBMISSION_REQUIREMENTS_V1.md) | what the venue actually requires | **no official rule could be verified**; nothing was inferred |
| [`CARDIOSENTIN_SUBMISSION_FORMAT_REVIEW_V1.md`](CARDIOSENTIN_SUBMISSION_FORMAT_REVIEW_V1.md) | submission format and final reviewer gate | scientifically final, and **cannot** be made format-final |
| [`CARDIOSENTIN_SUBMISSION_HANDOFF_FORMAT_PENDING_V1.md`](CARDIOSENTIN_SUBMISSION_HANDOFF_FORMAT_PENDING_V1.md) | handoff to the owner | blocked on official author instructions; requires a human action |

### 2026-08-29 — the hardening and migration run

| Record | Subject | Outcome |
|---|---|---|
| [`CARDIOSENTIN_RUNTIME_TRUST_BOUNDARY_HARDENING_V1.md`](CARDIOSENTIN_RUNTIME_TRUST_BOUNDARY_HARDENING_V1.md) | four runtime trust-boundary findings | all four **CLOSED** |
| [`CARDIOSENTIN_POST_PR129_WORK_RECOVERY_V1.md`](CARDIOSENTIN_POST_PR129_WORK_RECOVERY_V1.md) | recovering work stranded by PR #129 | salvaged and promoted |
| [`CARDIOSENTIN_DOCUMENTATION_DEMO_RECONCILIATION_V1.md`](CARDIOSENTIN_DOCUMENTATION_DEMO_RECONCILIATION_V1.md) | documentation relocation, demo contract reconciliation | reconciled |
| [`CARDIOSENTIN_DOCUMENT_HIERARCHY_MIGRATION_V2.md`](CARDIOSENTIN_DOCUMENT_HIERARCHY_MIGRATION_V2.md) | the controlled move of `paper/`, `handbook/`, `handoffs/` under `docs/` | migrated, with a byte receipt |

## Supersession

**`RELATED_WORK_VERIFICATION_V1` → `V2`.** V2 states the supersession in its own
header and keeps V1 rather than replacing it: V1's findings still stand wherever
V2 does not change them. Read V2 first.

**`PAPER_READINESS_AUDIT_V1` records its own partial supersession.** Its §2 gap
statement was refuted by the literature search merged in PR #127 on 2026-08-25,
which was discovered *after* the audit was written. The audit says so in place
rather than being corrected — which is the point of the rule above.

**`SUBMISSION_HANDOFF_FORMAT_PENDING_V1` names a state in its filename.** That
state was true when it was written. The filename is not re-checked when the
state changes, so confirm against the document, not the name.

## A note on the filenames

Eight records are prefixed `CARDIOSENTIN_`, one `CARDIOSENTINEL_`, and one
`TACTICS_2026_`. The truncation is historical drift, not a distinction.

**They are not renamed.** Nine documents under `docs/` reference these paths,
`CARDIOSENTIN_RELATED_WORK_VERIFICATION_V2.md` is digest-pinned in three places,
and a renamed audit is a broken citation in a record that cannot be edited to
follow it. The inconsistency is cheaper than the repair.
