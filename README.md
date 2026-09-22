# The Scene (2004–2006) — reconstruction

*The Scene* is a 20-episode web series produced by Jun Group Entertainment, released free online and seeded onto P2P networks. Roughly 90% of it is told through on-screen text — IRC channels, instant messages, FTP and application windows that the viewer reads rather than hears — with an opening narration, phone calls, and two entirely spoken episodes carrying the rest.

No episode-by-episode synopsis of the series existed anywhere. This repository is one, plus the working material it was built from.

## Contents

| Path | What it is |
| --- | --- |
| `The-Scene-S01-Episode-Synopses.md` | The synopsis: all 20 episodes, POV per episode, character notes, and the threads that pay off across the season |
| `data/screen-logs/` | Reconstructed on-screen text per episode, recovered by sampling video frames and OCRing the windows |
| `data/transcripts/` | Subtitle files for the spoken audio, generated locally with Whisper |
| `scripts/` | The small pipeline used to produce the above |

## Method

Frames were extracted at a fixed interval (`ocr2.sh`), upscaled, and read with Tesseract. `chatlog2.py` pulls chat-style lines out of the raw OCR and collapses the duplicates that come from the same line persisting across many frames. `newlines.py` diffs a denser pass against a coarser one to find content the first pass missed.

Sampling interval matters more than it looks. An 8-second interval is dense enough for the IRC channel, because chat scrolls slowly and lines stay on screen. It is *not* dense enough for short-lived windows: a private IM open for thirty seconds, or a background conversation in another language, can fall entirely between frames. Several significant story beats were recovered only on a second pass at 3 seconds.

## Known limits

- OCR is imperfect on 640×480 source. Character names and nicks are reliable; individual words are sometimes mangled, and the logs preserve those errors rather than guessing.
- The two names spoken in episode 17 are written on the whiteboard in that episode (Ed Koenig, Timothy Brudiger); Koenig is independently confirmed by the From header of the email trooper reads in episode 6.
- Text rendered in lighter colors — often one side of an IM conversation — reads less reliably than dark text, so some exchanges are captured mostly from one participant.
- Music segments are omitted from the transcripts; where Whisper produced lyrics under a score, those lines are noise rather than dialogue.
- Not everything in this series is chat. Email windows, browser tabs, file listings and desktop icons carry real information, and a sweep for chat-style lines alone will miss them — the tuition letter in episode 1, teflon's note to his boss in episode 5 and the "access issue" mail in episode 6 were all recovered by looking for `From:`/`Subject:` headers rather than nicks.

## A note on the material

`data/` contains the series' dialogue: the screen text and the spoken audio together amount to most of its script. The series was distributed under a Creative Commons license, but the specific terms are worth confirming before publishing this repository publicly.
