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

## Manual Publish (source -> master)

1. Work in `source` and verify locally.
2. Build with `hugo --minify`.
3. Copy `public/` output into `master` branch and commit there.
4. Ensure `CNAME` is present in published output.

## New Post

```bash
hugo new content/posts/my-post.md
```
