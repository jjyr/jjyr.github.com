#!/usr/bin/env bash

set -euo pipefail

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

hugo --minify --destination "$tmp_dir" >/dev/null

check_file() {
  local file="$1"

  if [[ ! -f "$file" ]]; then
    echo "missing file: $file" >&2
    return 1
  fi

  rg -q '<footer[^>]*site-footer' "$file"
  rg -q '>EOF<' "$file"
}

check_file "$tmp_dir/index.html"
check_file "$tmp_dir/posts/index.html"

first_post="$(find "$tmp_dir/posts" -mindepth 2 -maxdepth 2 -name index.html | head -n 1)"
if [[ -z "$first_post" ]]; then
  echo "missing post output" >&2
  exit 1
fi

check_file "$first_post"
