# Reading the paper

The [GitHub reading edition](../manuscript/report.md) displays the complete paper directly in the repository, including theorems, numbered equations, proof appendices, and references.

The HTML edition provides a dedicated academic reading layout. Its vector formulas are rendered during the build, so reading does not require a math service or a JavaScript download. Keep `index.html` and `assets/style.css` together when opening the edition locally.

From the repository root, a local preview can be served with:

```sh
python -m http.server 8000 --directory docs
```

Then open `http://localhost:8000`.

The included **Publish research website** workflow can serve this same edition through GitHub Pages. In repository **Settings → Pages**, select **GitHub Actions** as the source, then run that workflow from **Actions**.

The [content manifest](content-manifest.json) records source identities, formula coverage, equation tags, and rendering checks. The [presentation builder](../scripts/build_site.py) regenerates the edition from the structured manuscript.
