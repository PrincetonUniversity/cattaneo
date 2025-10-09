# cattaneo — site source for https://pubino.github.io/cattaneo

This repository contains the Jekyll source for the site hosted at https://pubino.github.io/cattaneo.

This README gives concise guidance for someone comfortable editing HTML and GitHub but new to Jekyll/GitHub Pages.

## Quick summary
- Edit site pages: top-level files like `index.html`, `publications.html`, `research.html`, etc. Each file has YAML front-matter at the top.
- Partials/includes: reusable fragments live in `_includes/` (header, footer, head, scripts).
- Layouts: page shells are in `_layouts/` (the default layout is `default.html`).
- Site data: `_data/navigation.yml` controls the main and utility menus.
- Assets: CSS, JS, and images are under `assets/`.
- Local dev: a Docker-based workflow is provided; you can also use a Ruby environment if you prefer.
- Deployment: the site is built with Jekyll and published via GitHub Pages from the `main` branch.

---

## Editing pages and content
- Pages are plain HTML (or Markdown) with a YAML front-matter block at the top. Example front-matter:

```
---
layout: default
title: "Publications"
permalink: /publications/
redirect_from:
  - /publications.html
---
```

- To edit site navigation, update `_data/navigation.yml`. Use directory-style URLs (ending with a trailing slash), e.g. `/publications/`.
- Reusable fragments: change `_includes/header.html` or `_includes/footer.html` to edit the global header/footer.
- Use Liquid helpers for asset/link paths when adding new references:
  - Prefer `{{ 'assets/js/foo.js' | relative_url }}` or `{{ 'assets/images/logo.svg' | relative_url }}` so Jekyll injects the correct `baseurl` for GitHub Pages.

## Asset conventions
- Place images under `assets/images/` and reference them with `{{ 'assets/images/your.png' | relative_url }}` or `{{ '/assets/images/your.png' | relative_url }}`.
- Stylesheets and scripts live under `assets/css/` and `assets/js/` respectively.

## Base URL and GitHub Pages
- The site is served from `https://pubino.github.io/cattaneo` (repository site). The production `_config.yml` includes:

```
baseurl: "/cattaneo"
```

- Local development uses `_config.local.yml` to override `baseurl` and `url` so the site builds and serves from `http://localhost:4000` without `/cattaneo` in the path.
- When editing templates, prefer `relative_url` so links behave correctly both locally and on GitHub Pages.

## Local development (recommended: Docker)
A Docker workflow is available so you don't need to install Ruby/Gems locally.

1. Build the image (optional if prebuilt):

```bash
docker build -t cattaneo-site:dev .
```

2. Serve locally with the repository mounted (live-reload disabled in the default Dockerfile to avoid host binding issues):

```bash
docker run --rm -v "$(pwd)":/srv/jekyll -p 4000:4000 cattaneo-site:dev bundle exec jekyll serve --config _config.yml,_config.local.yml --host 0.0.0.0
```

3. Visit `http://localhost:4000` to preview the site. `_config.local.yml` makes the generated absolute URLs point to `http://localhost:4000` for convenience.

If you prefer Ruby locally, install Ruby and Bundler, then run:

```bash
bundle install
bundle exec jekyll serve --config _config.yml,_config.local.yml
```

## Building for production locally
If you want to generate a production build (the same layout GitHub Pages will serve):

```bash
bundle exec jekyll build --config _config.yml
# built files will be in _site/
```

You can then preview `_site/` with a static server, e.g. `python3 -m http.server 4001` inside `_site/`.

## Deploying
- This repo is configured to publish from `main` via GitHub Pages. Pushing to `main` triggers GitHub Pages to rebuild the site.
- After a push, wait a minute and check `https://pubino.github.io/cattaneo`.

## Troubleshooting
- 404s for assets on GitHub Pages: first check that `baseurl` is set in `_config.yml` and that templates use `relative_url`. Inspect the page source and confirm asset URLs begin with `/cattaneo/assets/...`.
- Absolute `0.0.0.0` in console warnings during local dev: use `_config.local.yml` (already in repo) so generated absolute links point to `http://localhost:4000`, avoiding 0.0.0.0 addresses the browser blocks.
- If a page needs to keep its old `/page.html` URL, add `redirect_from` to the page front-matter (the `jekyll-redirect-from` plugin is enabled).

## Helpful git workflow
- Create a branch for feature work:

```bash
git checkout -b fix/some-change
# edit files
git add .
git commit -m "Describe change"
git push -u origin fix/some-change
```

- Open a PR and merge when ready. GitHub Pages will publish from `main`.

## Contact / next steps
If you want, I can:
- Add a simple GitHub Action that builds the site and shows the generated files as an artifact before pushing to main.
- Make any remaining templates use `{{ '...path...' | relative_url }}` where I find hard-coded leading slashes.

---

Last updated: 2025-10-09
