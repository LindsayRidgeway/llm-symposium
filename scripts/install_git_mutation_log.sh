#!/bin/sh
# Install hooks that write down every checkout in this clone (Desi, 2026-11-27).
#
# Why. On 2026-11-27 four files edited in this checkout were destroyed between `git add` and
# `git commit`, and two committed blocks were reverted out of the working tree an hour later. The
# lander's `_undo` is careful and scoped (it restores the pre-state per path and refuses when someone
# edited after it), and the reset path rescues work to a branch — so *something else* moved the tree,
# and the honest position is that I cannot name it. A lost paragraph with no log is a story; with a
# log it is a culprit.
#
# What it does not do: it cannot stop anything. A checkout that fires these hooks has already
# happened. It records when, which refs, and whether it was a path checkout (flag 0) or a branch
# switch (flag 1) — the distinction that matters, because `git checkout -- .` is a path checkout and
# is the shape that silently reverts a session's edits while leaving untracked files alone.
#
# The log lives inside the git dir, so writing it can never make the tree dirty and never needs a
# .gitignore entry. Install: sh scripts/install_git_mutation_log.sh [clone-path]
set -eu

REPO="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
# --path-format=absolute matters: without it this prints ".git", and the installer then
# writes hooks into whatever directory it happens to be standing in (found by its own test).
GITDIR="$(git -C "$REPO" rev-parse --path-format=absolute --git-common-dir)"
HOOKS="$GITDIR/hooks"
mkdir -p "$HOOKS"

cat > "$HOOKS/post-checkout" <<'EOF'
#!/bin/sh
# installed by scripts/install_git_mutation_log.sh — see that file for why
# $1 previous HEAD, $2 new HEAD, $3 1 = branch switch, 0 = path checkout
printf '%s %-9s %s -> %s branch=%s pid=%s\n' \
  "$(date -u +%FT%TZ)" "checkout" "$1" "$2" "$3" "$$" \
  >> "$(git rev-parse --path-format=absolute --git-common-dir)/mutation.log"
EOF
chmod +x "$HOOKS/post-checkout"

cat > "$HOOKS/post-merge" <<'EOF'
#!/bin/sh
# installed by scripts/install_git_mutation_log.sh — see that file for why
printf '%s %-9s %s pid=%s\n' "$(date -u +%FT%TZ)" "merge" "$*" "$$" \
  >> "$(git rev-parse --path-format=absolute --git-common-dir)/mutation.log"
EOF
chmod +x "$HOOKS/post-merge"

cat > "$HOOKS/post-rewrite" <<'EOF'
#!/bin/sh
# installed by scripts/install_git_mutation_log.sh — see that file for why
printf '%s %-9s %s pid=%s\n' "$(date -u +%FT%TZ)" "rewrite" "$*" "$$" \
  >> "$(git rev-parse --path-format=absolute --git-common-dir)/mutation.log"
EOF
chmod +x "$HOOKS/post-rewrite"

echo "installed in $HOOKS; log: $GITDIR/mutation.log"
