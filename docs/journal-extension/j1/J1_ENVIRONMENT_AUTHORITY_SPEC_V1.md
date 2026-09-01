# J1 — Environment Authority Specification, V1

# `QUALIFICATION CANDIDATE — NOT AUTHORIZED`

**This task defines what an authoritative execution environment *is*. It does not
select one, and it does not authorize the machine it was written on.**

J1 remains `PRE-REGISTERED`. No authorization document exists, no attempt budget
is set, no environment has been submitted for qualification.

---

## 1. The question the digest must answer

> **What exact scientific runtime environment was approved?**

It must **not** answer only:

> What environment happened to exist when someone ran a command?

A mutable workstation snapshot is not an authority. Two people rebuilding the
same approved environment must obtain the same digest, and a digest that changes
because a laptop's hostname differs describes the laptop, not the science.

## 2. Environment authority identity

Every field is required. **No field silently defaults.**

| Field | In digest | Meaning |
|---|:--:|---|
| `environment_id` | ✓ | Stable name of the approved environment |
| `environment_version` | ✓ | Version of that environment |
| `creation_method` | ✓ | How it was built, reproducibly |
| `base_image_identity` | ✓ | The base it was built from |
| `operating_system_identity` | ✓ | OS and architecture |
| `python_runtime_identity` | ✓ | Implementation and version |
| `dependency_lock_identity` | ✓ | The lock that pinned the dependency set |
| `dependency_digest` | ✓ | Digest over the resolved dependency set |
| `hardware_profile` | ✓ | Hardware/runtime assumptions |
| `accelerator_identity` | ✓ | Accelerator, or `none` |
| `container_image_digest` | ✓ | Image digest, where applicable |
| `immutable_artifact_location` | ✓ | Where the immutable artifact lives |
| `runtime_dependencies` | ✓ | Name → version mapping |
| `creation_timestamp` | ✗ | Recorded for provenance |
| `owner_provenance_identity` | ✗ | Recorded for provenance |

**Why two fields are excluded.** A creation timestamp and an owner identity bind
the digest to *where and when the record was written* rather than to what it
describes. Two faithful rebuilds of the same environment would then disagree,
which defeats the point. They stay in the document, out of the hash.

## 3. `environment_sha256`, frozen

**SHA-256 over the canonical serialization of the Environment Authority
Record.** Explicitly **not**: live machine state, `pip freeze` output, a home
directory, untracked files, or environment variables.

### 3.1 Canonical serialization

Frozen so two independent implementations agree byte for byte:

- fields emitted in the table's order, **never dictionary order**;
- one `field=value` line per field;
- UTF-8, no BOM;
- `\n` line endings, **exactly one** terminating the payload;
- no leading or trailing whitespace on any line — a padded value is **refused**,
  not stripped, because silently stripping would hide two records that differ;
- strings as-is; integers in decimal; mappings as `key=value` joined by `,` in
  **sorted key order**, so mapping insertion order cannot change the digest;
- **the separators are refused as content, never escaped** — `\n` and `\r` in
  any field value, and `\n`, `\r`, `,` or `=` in any dependency name or
  version;
- the no-padding and no-separator rules apply to dependency names and versions
  on the same terms as to every other field;
- excluded fields omitted entirely.

**Why the separators are refused rather than escaped.** They carry the whole
meaning of this form, so a value free to contain one can impersonate a
different record. `{"numpy": "2.3.2,scipy=1.0.0"}` and `{"numpy": "2.3.2",
"scipy": "1.0.0"}` are two different environments that would serialize to
identical bytes, share one digest, and both qualify. That is the same failure
the no-padding rule exists to prevent — two records that differ silently
merging into one — reached by a different door. Escaping would close it too,
but an escaping scheme is a second thing two implementations must agree on byte
for byte, and this form exists so that they need not. Refusal has one rule and
no encoding to get wrong.

## 4. States

```text
CANDIDATE  ──►  QUALIFIED  ──►  AUTHORIZED
```

| State | Reached by |
|---|---|
| `CANDIDATE` | A record exists. A local machine may generate one. |
| `QUALIFIED` | It passed `verify_authority_record`. |
| `AUTHORIZED` | **A human authorization naming the digest.** |

**This task may reach `QUALIFIED` only.** There is no transition function to
`AUTHORIZED` anywhere in the package — that transition is not code's to make.
A local environment may *generate* a candidate; it cannot promote itself.

## 5. Verifier

Two separate questions, two functions, both refusing hard.

**`verify_authority_record`** — is this record admissible as authority? Schema
completeness, no blank fields, a non-empty dependency set, **no mutable local
state**, digest integrity against the declared value, and an immutable artifact
reference that exists.

Its caller is not trusted to have done this. **`run_preflight` requires a
`VerifiedEnvironmentAuthority`** — the object `verify_authority_record`
returns — and refuses anything else, because `verify_runtime_matches` compares
the runtime against the record the object carries. An object that merely
reports an `environment_sha256` would be checking itself against itself.

**`verify_runtime_matches`** — is the runtime executing now the approved one?
Python identity, OS identity, dependency digest.

`observe_runtime` reads platform facts **for comparison only**. Nothing it
returns is hashed, and no value from it can become an `environment_sha256`.

### 5.1 Rejected as authority

`localhost` · `/home/…` · `/Users/…` · `~` · `$HOME` · `current-machine` ·
`developer-laptop` · `workstation` · `unbound` · `unknown`

A record naming any of these is refused with the reason stated, rather than
accepted and quietly relied upon. **`runtime_dependencies` is scanned on the
same terms as every other digest-bearing field**: a dependency resolved from a
local wheel or a home directory is exactly the mutable local state this rule
keeps out of a digest, and it reaches the digest by the same route.

## 6. Preflight integration

Stage order, with the new gate in place:

```text
freeze binding
→ authorization verification
→ git identity verification
→ environment authority verification      ← new
→ negative-capability proof
→ execution-capability proof
→ provenance sink validation
→ attempt-budget validation
→ atomic attempt claim
→ ONLY THEN scientific data access
```

The preflight requires `environment_authority_verified == TRUE` **before the
attempt claim**, and refuses when the authority is absent, when its digest does
not match the one the authorization names, or when the runtime does not match
the authority.

**There is no `DEV_MODE`, `FORCE_ENVIRONMENT` or `SKIP_ENV_CHECK`.** Asserted by
test, not by intention.

## 7. Negative capability

A structural test walks the AST of every module in the package and fails if any
of `gethostname`, `getlogin`, `getuser`, `expanduser` or a filesystem `walk` is
called. Proven by **AST, not text scan** — a text scan would match this
specification, which necessarily names what it forbids.

`environment_sha256 = hash(current_machine)` is therefore not a shortcut
somebody can take later; it is a shape the package cannot express.

## 8. What this task did not do

No environment selected. No environment authorized. No `J1_AUTHORIZATION_V1`.
No attempt budget. No attempt claimed. No physiological data, annotation, fold,
calibrator, threshold, candidate selection or result. The frozen protocol,
pre-registration and freeze receipt are byte-unchanged.

## 9. Remaining before authorization

1. **An actual environment must be built and submitted** — reproducibly, with an
   immutable artifact location. Nothing is qualified yet.
2. The **provenance sink** value still comes from the authorization.
3. The **TRAIN subject manifest** is supplied by the authorization, not
   discovered by the instrument.
4. J1 **collaborator implementations remain qualification fixtures**.
