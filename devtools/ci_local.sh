#!/usr/bin/env bash
# Run the jobs of .github/workflows/gates.yml on this machine, as CI runs them: on a fresh
# clone of HEAD (committed files only), with PYTHONDONTWRITEBYTECODE unset and GND pinned.
#
#   devtools/ci_local.sh [job ...]
#
# Jobs: macos-3.14 (on a Mac, directly), linux-3.11 and linux-3.14 (in a container, with
# podman or docker; CONTAINER=docker picks docker). With no job named, it runs every job this
# machine can run, at the same time. Each job's log, and the clone, are kept in a new folder
# under $TMPDIR, which the summary names. Exits 0 only when every job it ran exited 0.
#
# The base the index is checked against is origin/main as this checkout last fetched it:
# run `git fetch origin` first. The tests that need the claude CLI run here when it is on
# PATH; CI skips them.
#
# Keep the gate commands below in step with gates.yml; tests/test_ci_local.py checks it.
set -uo pipefail

GND_PIN='get-nick-done[synth]==0.4.0'
GATES='set -e
python3 devtools/build_plugins.py --check
python3 plugins/dvt-milestone/skills/components/scripts/components_index.py --check --strict
python3 plugins/dvt-milestone/skills/components/scripts/components_index.py changed --base origin/main
uv run --no-project --python "$PY" --with pytest python -m pytest tests -q -rs -p no:cacheprovider'

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
HEAD=$(git rev-parse HEAD) || exit 2
BASE=$(git rev-parse --verify -q origin/main) || { echo "ci_local: no origin/main here: git fetch origin" >&2; exit 2; }
[ -n "$(git status --porcelain)" ] && echo "ci_local: uncommitted changes are not in the run; CI sees commits only"

RUNTIME=${CONTAINER:-}
if [ -z "$RUNTIME" ]; then
  if command -v podman >/dev/null; then RUNTIME=podman; elif command -v docker >/dev/null; then RUNTIME=docker; fi
fi

JOBS="$*"
if [ -z "$JOBS" ]; then
  [ "$(uname)" = Darwin ] && JOBS="macos-3.14"
  if [ -n "$RUNTIME" ]; then JOBS="$JOBS linux-3.11 linux-3.14"
  else echo "ci_local: no podman or docker here: the Linux jobs are not run"; fi
fi

OUT=$(mktemp -d "${TMPDIR:-/tmp}/dev-tools-ci.XXXXXX")
echo '{}' > "$OUT/auth.json"  # pull public images anonymously, past any credential helper
git clone -q --no-hardlinks "$ROOT" "$OUT/src"
git -C "$OUT/src" checkout -q --detach "$HEAD"
git -C "$OUT/src" update-ref refs/remotes/origin/main "$BASE"
echo "ci_local: head $(git rev-parse --short "$HEAD"), base origin/main $(git rev-parse --short "$BASE"), in $OUT"

mac() {
  [ "$(uname)" = Darwin ] || { echo "macos-3.14 runs on a Mac only"; return 2; }
  cp -a "$OUT/src" "$OUT/macos"
  UV_TOOL_DIR="$OUT/tools" UV_TOOL_BIN_DIR="$OUT/bin" uv tool install -q --python 3.14 "$GND_PIN" || return 2
  cd "$OUT/macos" && env -u PYTHONDONTWRITEBYTECODE -u GND_COMMAND PATH="$OUT/bin:$PATH" PY=3.14 bash -c "$GATES"
}

linux() {  # $1: the Python version
  [ -n "$RUNTIME" ] || { echo "no podman or docker here"; return 2; }
  local auth=()
  [ "$RUNTIME" = podman ] && auth=(--authfile "$OUT/auth.json")  # docker reads DOCKER_CONFIG
  DOCKER_CONFIG="$OUT/docker" "$RUNTIME" run --rm ${auth[@]+"${auth[@]}"} -v "$OUT/src:/src:ro" \
    -e PY="$1" -e GATES="$GATES" -e GND_PIN="$GND_PIN" "docker.io/library/python:$1" bash -c '
      set -e; cp -a /src /work; cd /work
      pip install -q --root-user-action=ignore uv
      uv tool install -q --python "$PY" "$GND_PIN"; export PATH="$HOME/.local/bin:$PATH"
      apt-get -qq update >/dev/null && apt-get -qq install -y rsync >/dev/null
      git config --global user.name "dev-tools CI"; git config --global user.email ci@example.invalid
      git config --global init.defaultBranch main; git config --global --add safe.directory "*"
      bash -c "$GATES"'
}

PIDS=()
for name in $JOBS; do
  case $name in
    macos-3.14) mac ;;
    linux-3.11|linux-3.14) linux "${name#linux-}" ;;
    *) echo "unknown job $name (macos-3.14, linux-3.11, linux-3.14)"; false ;;
  esac > "$OUT/$name.log" 2>&1 &
  PIDS+=("$name:$!")
done

FAIL=0
for job in ${PIDS[@]+"${PIDS[@]}"}; do
  name=${job%%:*}
  wait "${job##*:}"; code=$?
  [ "$code" -ne 0 ] && FAIL=1
  echo "$name: exit $code, $(grep -E '[0-9]+ (passed|failed)' "$OUT/$name.log" | tail -1) ($OUT/$name.log)"
done
exit $FAIL
