# AGENTS.md

This file defines project-level operating rules for agents working in this repository.

## 1. Project Scope

- Build and maintain a minimal static personal site + blog.
- Stack is `Hugo`.
- No migration of old Jekyll content into the new site.

## 2. Branch Strategy

- `archive`: frozen legacy Jekyll site snapshot.
- `source`: default branch, Hugo source only.
- `master`: generated static output only.

Rules:

- Do not merge `master` back into `source`.
- Do not commit build artifacts to `source`.
- Preserve `CNAME` in published output.

## 3. Site Structure Requirements

- Home page (`/`): short bio + GitHub link + Email + RSS + latest posts.
- No dedicated Projects section for now; project info stays in bio.
- Posts index (`/posts/`): all posts in reverse chronological order, no pagination.
- Post detail (`/posts/<slug>/`): narrow reading width.

## 4. Design Constraints

- Keep the interface minimal and text-first.
- Style target: plain, 80s-like simplicity.
- Avoid decorative UI elements (cards, shadows, heavy effects).
- Prefer HTML + minimal CSS; avoid unnecessary JavaScript.
- Typography:
  - Body text uses serif font.
  - Code block and inline code use monospace.
- Post list style: title-first, date in small/light color.
- Date format: `YYYY-MM-DD`.

## 5. Content Model

Use minimal front matter for posts:

```yaml
---
title: "Post title"
date: 2026-02-25T10:00:00+08:00
draft: false
---
```

Do not add tags/categories unless explicitly requested.

## 6. Local Workflow

In `source` branch:

1. Preview locally: `hugo server -D`
2. Build output: `hugo --minify`
3. Publish by updating `master` with generated files from `public/`

## 7. Non-goals (until explicitly requested)

- Comments system
- Search
- Tags/categories taxonomy pages
- JS-heavy components
- CI/CD automation for deployment
