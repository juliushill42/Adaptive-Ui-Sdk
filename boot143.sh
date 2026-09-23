#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cmd="${1:-verify}"
case "$cmd" in
  doctor) uname -a; python3 --version; echo workspace=$ROOT ;;
  test|verify|smoke|status) cd "$ROOT" && python3 "$ROOT/tests/test_proof.py" ;;
  up) PORT="${PORT:-8765}" python3 "$ROOT/services/api/server.py" ;;
  *) echo "usage: boot143.sh doctor|verify|up"; exit 2 ;;
esac
