#!/usr/bin/env bash
# Verify a produced artifact is the object the frozen protocol names.
#
# The digest is recomputed from the manifest bytes inside the archive. A build
# tool's summary line is a claim about the artifact; the bytes are the artifact.
set -euo pipefail

ARCHIVE="${1:?oci archive required}"
python -m cardiosentinel.journal_extension.j1.controlled_build \
  artifact-digest --oci-archive "${ARCHIVE}"
