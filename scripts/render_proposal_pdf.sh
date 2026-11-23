#!/bin/sh
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
# Render docs/PROPOSAL.md to docs/PROPOSAL.pdf: pandoc (Markdown -> HTML), then headless Chromium (HTML -> PDF) via Playwright.
# Needs: pandoc, node with the playwright package and a Chromium it can launch.
set -e
cd "$(dirname "$0")/.."
tmp=$(mktemp -d)
cat > "$tmp/style.css" <<'CSS'
body { font-family: "DejaVu Sans", Arial, sans-serif; font-size: 9.5pt; line-height: 1.35; max-width: 100%; }
table { border-collapse: collapse; font-size: 8pt; margin: 0.5em 0; }
th, td { border: 1px solid #999; padding: 2px 4px; vertical-align: top; }
th { background: #eee; }
code { font-size: 8pt; }
h1 { font-size: 15pt; } h2 { font-size: 12pt; margin-top: 1.2em; } h3 { font-size: 10.5pt; }
CSS
pandoc docs/PROPOSAL.md -s --metadata pagetitle="Chipalooza #4 proposal" --embed-resources --css "$tmp/style.css" -o "$tmp/proposal.html"
node -e "
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://$tmp/proposal.html');
  await p.pdf({ path: 'docs/PROPOSAL.pdf', format: 'A4', margin: { top: '15mm', bottom: '15mm', left: '12mm', right: '12mm' } });
  await b.close();
})();
"
rm -rf "$tmp"
echo "docs/PROPOSAL.pdf written"
