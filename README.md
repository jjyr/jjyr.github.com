# JJy Minimal Hugo Site

## Branch Strategy

- `archive`: frozen legacy Jekyll snapshot
- `source`: default branch, Hugo source only
- `master`: generated static output only

Do not merge `master` back into `source`.

## Local Development (source)

```bash
hugo server -D
```

## Build

```bash
hugo --minify
```

Generated files are written to `public/`.

## One-Command Release

Run from `source` branch:

```bash
./scripts/release.sh "your source commit message" "Deploy YYYY-MM-DD HH:MM:SS +0800"
```

Arguments are optional:

```bash
./scripts/release.sh
```

This command will:

1. Commit all source changes on `source` (if any)
2. Push `source` to `origin/source`
3. Build with `hugo --minify --cleanDestinationDir`
4. Sync `public/` output to `master`
5. Commit and push `master`

## Manual Publish (source -> master)

1. Work in `source` and verify locally.
2. Build with `hugo --minify`.
3. Copy `public/` output into `master` branch and commit there.
4. Ensure `CNAME` is present in published output.

## New Post

```bash
hugo new content/posts/my-post.md
```
