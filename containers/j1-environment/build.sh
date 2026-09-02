#!/usr/bin/env bash
# One controlled build of the J1 environment artifact.
#
# NOT AUTHORIZED. This script is invoked only after the builder-authorization
# gate has already passed; it performs no permission check of its own, because
# a second check here would invite the two to disagree.
#
# The artifact is written as an OCI layout archive rather than pushed. The
# digest J1 freezes is over the canonical single-platform image manifest bytes,
# and an archive contains exactly those bytes, so the digest is recomputed from
# the artifact instead of read from a registry response. No credentials are
# needed, which is why none exist.
set -euo pipefail

BUILD_ID="${1:?build id required}"
CONTEXT="${2:?source context required}"
OUTPUT="${3:?output archive path required}"
BASE_IMAGE_DIGEST="${BASE_IMAGE_DIGEST:?base image digest required}"

# Single platform, no attestations: both would turn the output into an index,
# whose digest identifies a list rather than the image J1 would execute.
docker buildx build \
  --file "${CONTEXT}/containers/j1-environment/Containerfile" \
  --platform linux/amd64 \
  --build-arg "BASE_IMAGE_DIGEST=${BASE_IMAGE_DIGEST}" \
  --build-arg "SOURCE_DATE_EPOCH=0" \
  --provenance=false \
  --sbom=false \
  --no-cache \
  --output "type=oci,dest=${OUTPUT},rewrite-timestamp=true" \
  "${CONTEXT}"

echo "build ${BUILD_ID} wrote ${OUTPUT}"
