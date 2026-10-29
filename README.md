# Towards Sustainable Society – language choice (TSS-www)

The page at <https://www.towardssustainablesociety.org>: a choice between the English version ([tss-en](https://github.com/towardssustainablesociety/tss-en)) and the Swedish original ([tss-sv](https://github.com/towardssustainablesociety/tss-sv)), and a short description of how to read TSS in other languages with the browser's built-in translation.

- `site/index.html` is the language choice page. It is written by hand, except the hreflang links and the row of other languages, which `bygg-sprak.py` fills in between the markers.
- `sprak/<code>.html` holds the introduction in each of the other languages (Spanish, French, German, Portuguese, Chinese (simplified), Arabic, Hindi, Russian, Japanese and Indonesian). Each is a short home page for TSS written directly in that language, with AI support. The header in the HTML comment holds the page title, description and the fixed texts.
- `bygg-sprak.py` builds `site/<code>/index.html` from those files, writes hreflang on all pages and `site/sitemap.xml`. Run `python3 bygg-sprak.py` after any change in `sprak/` and commit the result. A new language: add `sprak/<code>.html` and the code in `ORDNING` in the script.
- `site/stil.css` is the shared style.
- `site/CNAME` gives the address. The bare domain `towardssustainablesociety.org` is forwarded to www by the domain registrar (Loopia).
- `.github/workflows/publicera.yml` publishes `site/` on GitHub Pages on every change in `main`.

Licence: CC BY-SA 4.0, see [LICENSE](LICENSE).
