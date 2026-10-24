# GitHub Pages deployment

The portfolio is published at [https://kravet.github.io](https://kravet.github.io) from the `Kravet/Kravet.github.io` repository. GitHub Pages serves the repository root from the `main` branch; no build step is required.

## Update the live site

1. Edit the static files and run `python3 scripts/verify-site.py`.
2. Keep `content-sources.md`, local preview screenshots, and Playwright captures out of the public repository; `.gitignore` excludes them.
3. Commit and push the website files to `main`. GitHub Pages publishes from the repository root.
4. Confirm the HTTPS site and its local assets after deployment.

The site uses a canonical URL, an allowing `robots.txt`, and `sitemap.xml` for its published address. No paid service is needed.
