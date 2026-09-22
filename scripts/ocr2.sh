#!/bin/bash
# usage: ocr2.sh <video> <outdir> <interval>
V="$1"; D="$2"; I="${3:-8}"
rm -rf "$D/frames"; mkdir -p "$D/frames"
ffmpeg -v error -i "$V" -vf "fps=1/$I,scale=iw*2:ih*2:flags=bilinear" -q:v 2 "$D/frames/f%04d.jpg" -y
ls "$D/frames"/*.jpg | xargs -P 2 -I{} sh -c 'tesseract "{}" "${1%.jpg}" --psm 6 2>/dev/null' _ {}
: > "$D/raw_ocr.txt"
for t in "$D/frames"/*.txt; do
  n=$(basename "$t" .txt); idx=$((10#${n#f} - 1)); s=$((idx*I))
  printf '### t=%d:%02d\n' $((s/60)) $((s%60)) >> "$D/raw_ocr.txt"
  cat "$t" >> "$D/raw_ocr.txt"
done
rm -f "$D/frames"/*.jpg
