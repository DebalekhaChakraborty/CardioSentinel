# J1 — Local Origin Diagnostic for `incident-management==0.1.0`

# `LOCAL OBSERVATION — NOT REPOSITORY-PROVEN PROVENANCE`

# `THIS DOES NOT ESTABLISH THAT THE PACKAGE MAY BE REMOVED`

**Date:** 2026-09-05
**Companion to:** `J1_ENV_BUILDER_AUTH_003_POSTCLAIM_FAILURE_RECEIPT.md`

Run `33984680149` failed because `incident-management==0.1.0` cannot be resolved
from the configured index. This document records what was observed **on one
machine's filesystem** about how that distribution came to be present.

It is kept separate from the failure receipt deliberately. The receipt records
facts the provider and the repository can both attest. **Everything below is a
local observation of a mutable development environment**, and promoting it into
canonical provenance on the strength of prose is exactly the move this
separation prevents.

**The package was not imported and not executed. Nothing was modified.**

---

## 1. What is repository- or provider-proven

These facts do **not** depend on this document:

```text
incident-management==0.1.0 is present in all three frozen establishing locks
  B4B_cnn_transformer_v1   index 127
  P1B_phys_fusion_v1       index 127
  M1L_long_memory_v2       index 127

the V2 generator emits it to requirements.pypi.txt, at line 126 of 332

both controlled builds independently failed to resolve it from the index,
with "from versions: none"

the build-source classification recognises only `cardiosentinel`
as first-party for this authority
```

## 2. What is local-only

Everything in §3–§5. It was observed once, on the machine that runs this
programme, in an environment that is not under version control and can change.

---

## 3. Observation environment

```text
interpreter : /home/AI_POC/venvs/tactics/bin/python
python      : 3.12.6

sys.path:
  (empty)
  /usr/local/python312/lib/python312.zip
  /usr/local/python312/lib/python3.12
  /usr/local/python312/lib/python3.12/lib-dynload
  /home/AI_POC/venvs/tactics/lib/python3.12/site-packages
  /home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal/src
  /home/AI_POC/adk-incident-mgmt-agent
```

The last entry is contributed by the `.pth` file recorded below.

---

## 4. The `.pth` files

Two `.pth` files, byte-identical to each other, one in each virtual environment:

```text
path   : /home/AI_POC/venvs/tactics/lib/python3.12/site-packages/incident_management.pth
sha256 : 932993476c98d54372180e3ce0b48bec52c712065460ef45853917680d0ed7c6
bytes  : 37
content: '/home/AI_POC/adk-incident-mgmt-agent'
target : /home/AI_POC/adk-incident-mgmt-agent   exists=True  is_dir=True
```

```text
path   : /home/AI_POC/venvs/debalekha/lib/python3.12/site-packages/incident_management.pth
sha256 : 932993476c98d54372180e3ce0b48bec52c712065460ef45853917680d0ed7c6
bytes  : 37
content: '/home/AI_POC/adk-incident-mgmt-agent'
target : /home/AI_POC/adk-incident-mgmt-agent   exists=True  is_dir=True
```

`venvs/tactics` is the scientific interpreter this programme uses.
`venvs/debalekha` is the application interpreter it is required never to use.

---

## 5. Distribution metadata

```text
importlib.metadata.distribution("incident-management")

version        : 0.1.0
metadata Name  : incident-management
dist-info path : /home/AI_POC/venvs/tactics/lib/python3.12/site-packages/
                 incident_management-0.1.0.dist-info

direct_url.json:
  {"dir_info": {"editable": true},
   "url": "file:///home/AI_POC/adk-incident-mgmt-agent"}

INSTALLER      : poetry
WHEEL          : Wheel-Version: 1.0
                 Generator: poetry-core 2.2.1
                 Root-Is-Purelib: true
                 Tag: py3-none-any
top_level.txt  : absent
```

### Installed files, as `RECORD` and `locate_file` report them

```text
/home/AI_POC/venvs/debalekha/lib/python3.12/site-packages/incident_management.pth
/home/AI_POC/venvs/debalekha/lib/python3.12/site-packages/incident_management-0.1.0.dist-info/METADATA
/home/AI_POC/venvs/debalekha/lib/python3.12/site-packages/incident_management-0.1.0.dist-info/WHEEL
/home/AI_POC/venvs/debalekha/lib/python3.12/site-packages/incident_management-0.1.0.dist-info/INSTALLER
/home/AI_POC/venvs/debalekha/lib/python3.12/site-packages/incident_management-0.1.0.dist-info/direct_url.json
/home/AI_POC/venvs/debalekha/lib/python3.12/site-packages/incident_management-0.1.0.dist-info/RECORD
```

**The `RECORD` read through the tactics dist-info names paths inside the
`debalekha` environment.**

---

## 6. What the observation is consistent with

`direct_url.json` carries `"editable": true` with a `file://` URL. That is
**an editable installation sourced from a local filesystem path**.

**This local observation does not establish whether the same distribution
name/version exists, existed, or was obtainable through any package index or
other repository.** It records how *this* environment came to hold the
distribution, and nothing about its publication history anywhere else.

The directory it points at, `/home/AI_POC/adk-incident-mgmt-agent`, is not part
of the CardioSentinel repository.

## 7. What this does NOT establish

- **It does not establish that the package is extraneous to CardioSentinel.**
  Nothing here was checked against CardioSentinel's imports, and no scientific
  code was read or executed to find out.
- **It does not establish that removing it is safe.** Its scientific necessity
  has not been assessed, and this document does not assess it.
- **It does not establish when or by whom it entered the environment**, only
  what the environment looks like now.
- **It is not durable evidence.** Both virtual environments are mutable and
  outside version control. A later reader may find none of this, which is why the
  digests and contents above are transcribed here rather than referenced.

# The question "may `incident-management` be removed from the V2 environment?" is the next audit's, and it is not answered here.
