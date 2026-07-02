#!/usr/bin/env bash
set -euo pipefail

SRC="/home/cbaadmin/src/catalog-extensions"
DST="/home/cbaadmin/src/custom-discovery/catalog-extensions"

echo "Syncing catalog-extensions from:"
echo "  $SRC"
echo "to:"
echo "  $DST"

rsync -av --delete \
  --exclude='.git' \
  --exclude='*.egg-info' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='build' \
  --exclude='dist' \
  "$SRC/" "$DST/"

echo "Sync complete."
