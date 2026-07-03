#!/usr/bin/env bash
set -euo pipefail

IMAGE_VERSION="cba/openedx-discovery:21.0.4-production"
IMAGE_LATEST="custom-openedx-discovery:latest"

echo "==> Syncing catalog-extensions"
./scripts/sync_catalog_extensions.sh

echo
echo "==> Building Discovery image"
docker build \
    -t "$IMAGE_VERSION" \
    .

echo
echo "==> Tagging Discovery image as latest"
docker tag "$IMAGE_VERSION" "$IMAGE_LATEST"

echo
echo "==> Built images"
docker images | grep -E 'cba/openedx-discovery|custom-openedx-discovery' || true

echo
echo "Build complete."
