#!/usr/bin/env python3
"""Transcribe episodes to SRT with faster-whisper.

Prefer transcribe-xxl.sh. This script cannot strip the score before detecting
speech, and under music it drops whole scenes without marking the loss; it is
kept as the minimal pure-Python equivalent.

    pip install faster-whisper
    python3 transcribe.py <outdir> <video> [<video> ...]

Writes <outdir>/<name>.srt, one per input, and skips any that already exist
so an interrupted run can be restarted. Set WHISPER_MODEL to change the
model (default large-v3); set WHISPER_DEVICE=cuda if you have the VRAM.

This series is mostly read rather than heard, so the audio is sparse: long
silences, music between scenes, and a handful of phone calls. Whisper
hallucinates in silence, so VAD is on and the usual repetition guards are
set. Music still comes back as invented lyrics -- treat anything under a
score as noise, not dialogue.
"""
import os, sys

def ts(t):
    ms = int(round(float(t) * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)

def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    outdir, videos = sys.argv[1], sys.argv[2:]
    os.makedirs(outdir, exist_ok=True)

    from faster_whisper import WhisperModel
    model_name = os.environ.get("WHISPER_MODEL", "large-v3")
    device     = os.environ.get("WHISPER_DEVICE", "cpu")
    compute    = os.environ.get("WHISPER_COMPUTE", "int8" if device == "cpu" else "float16")
    print("loading %s on %s (%s)" % (model_name, device, compute), flush=True)
    model = WhisperModel(model_name, device=device, compute_type=compute)

    for v in videos:
        name = os.path.splitext(os.path.basename(v))[0]
        out  = os.path.join(outdir, name + ".srt")
        if os.path.exists(out) and os.path.getsize(out) > 0:
            print("skip %s (exists)" % name, flush=True)
            continue
        print("=> %s" % name, flush=True)
        segments, info = model.transcribe(
            v,
            language="en",
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=700),
            condition_on_previous_text=False,   # stops one hallucination seeding the next
            no_speech_threshold=0.5,
            compression_ratio_threshold=2.2,    # drops looping repeats
        )
        n = 0
        tmp = out + ".part"
        with open(tmp, "w", encoding="utf-8") as f:
            for seg in segments:
                text = seg.text.strip()
                if not text:
                    continue
                n += 1
                f.write("%d\n%s --> %s\n%s\n\n" % (n, ts(seg.start), ts(seg.end), text))
                if n % 25 == 0:
                    print("   %4d  %s" % (n, ts(seg.start)), flush=True)
        os.replace(tmp, out)
        print("   %s -- %d segments" % (out, n), flush=True)

if __name__ == "__main__":
    main()
