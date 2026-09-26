#!/usr/bin/env bash
# Build the GitHub Pages edition into _site/ (or the directory given).
#
#     scripts/build-site.sh [outdir]
#
# The synopses and the character index are built with their frames linked
# rather than embedded; the self-contained editions committed at the top of
# the repo go in unchanged under offline/.
set -euo pipefail
out=${1:-_site}
rm -rf "$out"
mkdir -p "$out/offline"
for f in The-Scene-S01-Episode-Synopses.md The-Scene-S02-Episode-Synopses.md The-Scene-Characters.md; do
  python3 scripts/mkhtml.py --web "$out" "$f"
  cp "${f%.md}.html" "$out/offline/"
done
cp index.html 404.html sitemap.xml "$out/"
cp -r stills "$out/"
