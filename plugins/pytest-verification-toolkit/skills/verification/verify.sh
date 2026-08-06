#!/usr/bin/env bash
set -e
echo "--- pytest ---"
pytest -q
echo "--- git diff --stat ---"
git diff --stat
