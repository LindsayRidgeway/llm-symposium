#!/bin/sh
# Install a `git` shim that writes down the operations no hook can see (Desi, 2026-11-27).
#
# Why a shim and not a hook. `scripts/install_git_mutation_log.sh` installs post-checkout, post-merge
# and post-rewrite hooks, and they demonstrably fire: the live clone's .git/mutation.log names file
# checkouts with pids. But the sweep that restored six files at 2026-11-27T20:51:25Z left no line of
# any kind. Dmitri measured why (channels/reports/2026-11-27-dmitri-the-2051-sweep-has-no-author-
# because-nothing-logs-restore.md): the operations that rewrite tracked files *from a commit* mostly
# run no hook at all — `git restore <paths>`, `git reset --hard` (outside the lander, which writes its
# own line), `git read-tree -u`, `git checkout-index -f -a`. The lander's `_tree_watch` samples the
# tree once per landing (land_runs.py:1042), so it can say *which paths* moved and *between which two
# samples*, and never which process did it or with what command — the item's closing condition.
#
# A hook cannot cover a verb that runs no hook. A shim stands in front of the binary, so it covers
# exactly the hookless set: for reset|restore|checkout|read-tree|checkout-index|stash|rebase it
# appends time, verb, pid, ppid, cwd and the argument vector to the same .git/mutation.log, then
# execs the real git found further along PATH.
#
# Two limits, stated here rather than discovered later:
#   1. It only fires for processes whose PATH has the shim directory ahead of the real git. This
#      clone's launcher is outside this checkout, so installing it here cannot bind the launcher;
#      `sh scripts/install_git_shim.sh --check` is the one-line proof of whether it binds a process.
#   2. It cannot see a copy-back (`cp`/`rsync`) from a worktree or a snapshot. Nothing git-shaped can.
#
# Usage: sh scripts/install_git_shim.sh [clone-path]          install
#        sh scripts/install_git_shim.sh --check [clone-path]  is the shim first on PATH here?
set -eu

CHECK=0
if [ "${1:-}" = "--check" ]; then CHECK=1; shift; fi
REPO="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
GITDIR="$(git -C "$REPO" rev-parse --path-format=absolute --git-common-dir)"
SHIMDIR="$GITDIR/shim"

if [ "$CHECK" = "1" ]; then
  if [ ! -x "$SHIMDIR/git" ]; then
    echo "NOT INSTALLED: $SHIMDIR/git does not exist; run sh scripts/install_git_shim.sh"
    exit 1
  fi
  # Resolve what `git` a plain lookup finds, and compare it to the shim's own directory.
  found="$(command -v git || true)"
  if [ -z "$found" ]; then
    echo "NOT BOUND: no git on PATH"
    exit 1
  fi
  # -P on both sides: on macOS /var is a symlink to /private/var, and a comparison of a logical path
  # against a physical one says NOT BOUND about an instrument that is bound.
  founddir="$(cd "$(dirname "$found")" && pwd -P)"
  if [ "$founddir" = "$(cd "$SHIMDIR" && pwd -P)" ]; then
    echo "BOUND: git resolves to the shim ($found); hookless writes are being logged"
    exit 0
  fi
  echo "NOT BOUND: git resolves to $found; the shim at $SHIMDIR is not first on PATH"
  exit 1
fi

mkdir -p "$SHIMDIR"

cat > "$SHIMDIR/git" <<'EOF'
#!/bin/sh
# installed by scripts/install_git_shim.sh — see that file for why. Do not edit: reinstall instead.
self_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)

# Find the first real `git` further along PATH, skipping this directory. Without this the shim
# execs itself, which looks like a hung machine rather than like a bug.
real=""
_oldifs=$IFS
IFS=:
for _d in $PATH; do
  [ -n "$_d" ] || continue
  # -P on both sides: on macOS /var is a symlink to /private/var, and a logical-vs-physical
  # comparison made the shim fail to recognise itself, find itself as "the real git", and
  # exec itself forever. That is not a theory: it hung this file's own test for five minutes.
  _abs=$(CDPATH= cd -- "$_d" 2>/dev/null && pwd -P) || continue
  [ "$_abs" = "$self_dir" ] && continue
  if [ -f "$_d/git" ] && [ -x "$_d/git" ]; then real="$_d/git"; break; fi
done
IFS=$_oldifs
if [ -z "$real" ]; then
  echo "git shim: no real git found after $self_dir on PATH" >&2
  exit 127
fi

# The verb is the first non-option argument, skipping the global options that take a value.
# -C is captured too: the log must land in the repository being mutated, not in whatever repo the
# caller happens to stand in. A shim that logs the wrong repo is worse than none, because the absence
# of a line then reads as evidence.
verb=""
cdir="."
pending=""
for a in "$@"; do
  if [ -n "$pending" ]; then
    [ "$pending" = "-C" ] && cdir="$a"
    pending=""; continue
  fi
  case "$a" in
    -C|-c|--git-dir|--work-tree|--namespace|--exec-path|--config-env|--super-prefix)
      pending="$a"; continue ;;
    -*) continue ;;
    *) verb="$a"; break ;;
  esac
done

case "$verb" in
  reset|restore|checkout|read-tree|checkout-index|stash|rebase)
    # The log lives in the git dir, so writing it can never make the tree dirty. rev-parse from the
    # caller's own cwd, because that is the repository being mutated — not $self_dir, which is
    # shared by every repo that installs a shim.
    _g=$("$real" -C "$cdir" rev-parse --path-format=absolute --git-common-dir 2>/dev/null) || _g=""
    if [ -n "$_g" ]; then
      printf '%s %-9s verb=%s pid=%s ppid=%s cwd=%s argv=%s\n' \
        "$(date -u +%FT%TZ)" "shim" "$verb" "$$" "$PPID" "$(pwd)" "$*" \
        >> "$_g/mutation.log" 2>/dev/null || true
    fi
    ;;
esac

exec "$real" "$@"
EOF
chmod +x "$SHIMDIR/git"

echo "installed $SHIMDIR/git"
echo "to bind it in a shell: PATH=$SHIMDIR:\$PATH  (then: sh $0 --check)"
