#!/usr/bin/env bash
set -euo pipefail

SOURCE_BRANCH="source"
PUBLISH_BRANCH="master"

timestamp() {
  date +"%Y-%m-%d %H:%M:%S %z"
}

log() {
  printf '[release] %s\n' "$1"
}

fail() {
  printf '[release] ERROR: %s\n' "$1" >&2
  exit 1
}

if ! command -v git >/dev/null 2>&1; then
  fail "git is required"
fi

if ! command -v hugo >/dev/null 2>&1; then
  fail "hugo is required"
fi

if ! command -v rsync >/dev/null 2>&1; then
  fail "rsync is required"
fi

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

current_branch="$(git branch --show-current)"
if [[ "$current_branch" != "$SOURCE_BRANCH" ]]; then
  fail "run this command on '$SOURCE_BRANCH' branch (current: '$current_branch')"
fi

source_message="${1:-chore: release $(timestamp)}"
deploy_message="${2:-Deploy $(timestamp)}"

log "building source branch '$SOURCE_BRANCH'"

if [[ -n "$(git status --porcelain)" ]]; then
  git add -A
  git commit -m "$source_message"
  log "committed source changes"
else
  log "no source changes to commit"
fi

git push origin "$SOURCE_BRANCH"
log "pushed source to origin/$SOURCE_BRANCH"

hugo --minify --cleanDestinationDir
log "built site to public/"

publish_dir="$(mktemp -d "${TMPDIR:-/tmp}/jjyr-master-publish.XXXXXX")"

cleanup() {
  set +e
  if git worktree list | grep -Fq "$publish_dir"; then
    git worktree remove --force "$publish_dir" >/dev/null 2>&1
  fi
  rm -rf "$publish_dir"
}
trap cleanup EXIT

git fetch origin "$PUBLISH_BRANCH"

if git show-ref --verify --quiet "refs/heads/$PUBLISH_BRANCH"; then
  git worktree add "$publish_dir" "$PUBLISH_BRANCH" >/dev/null
  git -C "$publish_dir" reset --hard "origin/$PUBLISH_BRANCH" >/dev/null
else
  git worktree add -b "$PUBLISH_BRANCH" "$publish_dir" "origin/$PUBLISH_BRANCH" >/dev/null
fi

rsync -a --delete --exclude=".git" public/ "$publish_dir"/

if [[ ! -f "$publish_dir/CNAME" ]]; then
  fail "CNAME not found in publish output"
fi

if [[ -n "$(git -C "$publish_dir" status --porcelain)" ]]; then
  git -C "$publish_dir" add -A
  git -C "$publish_dir" commit -m "$deploy_message"
  git -C "$publish_dir" push origin "$PUBLISH_BRANCH"
  log "published to origin/$PUBLISH_BRANCH"
else
  log "no publish changes on $PUBLISH_BRANCH"
fi

log "done"
