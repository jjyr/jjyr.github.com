# JJy Minimal Hugo Site

## Branch Strategy

- `archive`: frozen legacy Jekyll snapshot
- `source`: default branch, Hugo source only
- `master`: legacy generated static output snapshot

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

## Deploy

Push `source` to trigger GitHub Actions deployment:

```bash
git push origin source
```

The workflow builds Hugo, checks that `public/CNAME` exists, uploads `public/` as a GitHub Pages artifact, and deploys it. Do not commit `public/` or update `master` for deployment.

Manual dispatch is also available from the `Deploy GitHub Pages` workflow in GitHub Actions.

## GitHub Pages

Repository Pages source should be set to `GitHub Actions`, not a branch.

## New Post

```bash
hugo new content/posts/my-post.md
```
