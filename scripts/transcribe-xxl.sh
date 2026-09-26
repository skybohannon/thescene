#!/usr/bin/env bash
# Transcribe episodes with Purfview's Faster-Whisper-XXL, separating the vocals
# from the score first.
#
#     FWXXL=/path/to/faster-whisper-xxl.exe scripts/transcribe-xxl.sh <outdir> <video> [<video> ...]
#
# This is the configuration to use. Under a loud score, stock VAD decides there
# is no speech and drops whole scenes without marking the loss: season 1's
# episode 14 came back as 11 subtitles from medium.en and 61 from this. mdx_kim2
# strips the music, pyannote finds the speech that is left, large-v2 reads it.
#
# Get the binary from https://github.com/Purfview/whisper-standalone-win
# (release "Faster-Whisper-XXL"). It fetches the model on first use.
#
# FWXXL_COMPUTE defaults to int8_float16, which fits large-v2 into 4 GB of VRAM;
# set it to float16 on a bigger card, and FWXXL_DEVICE=cpu if you have none.
# Episodes with an existing .srt in <outdir> are skipped, so a run can be resumed.
set -euo pipefail

[ $# -ge 2 ] || { sed -n '2,17p' "$0"; exit 1; }
outdir=$1; shift
exe=${FWXXL:-faster-whisper-xxl}
mkdir -p "$outdir"

for v in "$@"; do
  name=$(basename "${v%.*}")
  if [ -s "$outdir/$name.srt" ]; then
    echo "skip $name (exists)"
    continue
  fi
  echo "=> $name"
  "$exe" "$v" -o "$outdir" --output_format srt -l en -m large-v2 \
    --ff_vocal_extract mdx_kim2 --vad_method pyannote_v3 --standard \
    --compute_type "${FWXXL_COMPUTE:-int8_float16}" --device "${FWXXL_DEVICE:-cuda}"
done
