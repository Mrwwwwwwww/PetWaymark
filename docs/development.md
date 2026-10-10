# Developer and research tools

These tools are retained for offline research and compatibility tests. The pet-owner page does not run the Python service, CLI, emergency/handover/planning modules, provider directory or correction panel.

- [Original rules](../data/rules/README.md), [source catalog](../data/sources/catalog.json), [coverage gaps](../data/coverage/)
- [Research archive](research/), [decisions](decisions/), [Chinese technical docs](zh/), [English technical docs](en/)
- [Offline reuse](../examples/offline/README.md), [release history](releases/v0.1.0.md)
- [Contributing](../CONTRIBUTING.md), [security](../SECURITY.md), [governance](../GOVERNANCE.md)

Use Python 3.11+ with `pip install -r requirements-dev.txt` in a virtual environment. Run:

```sh
python scripts/check_scaffold.py
python scripts/validate_data.py
python scripts/audit_coverage.py --check
python scripts/package_data.py --check
python -m unittest discover -s tests -v
python scripts/build_pages.py --check
python scripts/build_pages.py
```

Browser checks use Playwright as development tooling only:

```sh
npm --prefix /tmp/petwaymark-browser install --no-save --no-package-lock playwright@1.64.0
/tmp/petwaymark-browser/node_modules/.bin/playwright install chromium
NODE_PATH=/tmp/petwaymark-browser/node_modules node tests/pages_smoke.cjs
```

The legacy research form can still be started with `python -m apps.web.server --port 8766`; `tests/browser_smoke.cjs` tests it. It is not needed for the owner page. CLI examples and rule scope notes remain in the research archive.

Regenerate the checked-in offline data with `python scripts/build_pages.py --write-source` after reviewing rule or place changes. Build output uses only an allowlist of page files and data; no research cases, provider data or issue submission code is copied. The builder removes only the retired generated `examples.js`, `demo.js` and `correction.js` files in its output. Other generated data packages in `dist/` remain available to offline-reuse tests.
