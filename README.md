# Andrii Kravets — portfolio

A small, static portfolio for a Senior Android / Kotlin Engineer. It uses semantic HTML, CSS and vanilla JavaScript; there is no build step, analytics, external font, or paid service.

Live site: [https://kravet.github.io](https://kravet.github.io)

## Preview on macOS

From this folder, run:

```sh
python3 -m http.server 4173
```

Then open [http://localhost:4173](http://localhost:4173). Stop the server with `Ctrl+C`.

The portfolio also works by opening `index.html` directly. The local server is recommended for consistent link and download behavior.

## Update content

- Edit copy, work history and links in `index.html`.
- Replace or add local images under `assets/` and update their relative paths in the page.
- The CV is stored in `assets/cv/` and can be replaced without changing the page structure.
- Run `python3 scripts/verify-site.py` after content or asset changes.

## Preview privacy

The portfolio is public and allows search indexing. Its canonical URL and sitemap point to `https://kravet.github.io/`.
