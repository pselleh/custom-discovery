#!/usr/bin/env bash
set -euo pipefail

echo "Syncing catalog-extensions..."

./scripts/sync_catalog_extensions.sh

echo

echo "Building Discovery..."

docker build \
    -t cba/openedx-discovery:21.0.4-production .

echo

echo "Done."
