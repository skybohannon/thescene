# The Scene (2004–2006) — reconstruction

*The Scene* is a 20-episode web series about warez groups and the people in them. Roughly 90% of it is told through on-screen text — IRC channels, instant messages, FTP and application windows that the viewer reads rather than hears — with an opening narration, phone calls, and two entirely spoken episodes carrying the rest.

No episode-by-episode synopsis of it appears to exist: the databases that list the series leave their plot fields blank. This repository is one — for season 1 and for *The Scene 2.0*, the 20-episode sequel released in 2006 — plus the pipeline that produced it.

## Contents

| Path | What it is |
| --- | --- |
| `The-Scene-S01-Episode-Synopses.md` | Season 1: all 20 episodes, POV per episode, character notes, and the threads that pay off across the season |
| `The-Scene-S02-Episode-Synopses.md` | *The Scene 2.0*: all 20 episodes, the cold-open narration, the infrastructure the season is built on, and the personal thread underneath it |
| `The-Scene-Characters.md` | Both seasons: every handle, who it belongs to, who plays them, and which episodes they're in |
| `index.html` | The landing page for the GitHub Pages edition |
| `stills/s01/` | Nine frames from season 1, referenced by that synopsis |
| `stills/s02/` | Ten frames from season 2, likewise |
| `scripts/` | The pipeline that recovered the text it was written from |
| `LICENSE` | CC BY 4.0, covering the writing here — not the series |

Each synopsis, and the character index, also ships as a single self-contained `.html` file with the frames embedded, so it can be read anywhere — including next to the episodes themselves. The same files are published at **[skybohannon.github.io/thescene](https://skybohannon.github.io/thescene/)**.

The recovered screen text and the audio transcripts themselves are **not** published here — see *A note on the material* below.

## Method

Every episode was sampled at **one frame every 3 seconds** (`ocr2.sh`), upscaled 2×, and read with Tesseract. `chatlog.py` pulls chat-style lines out of the raw OCR and collapses the duplicates that come from the same line persisting across many frames; `chatlog.py --all` keeps everything rather than just chat, and `chatlog.py --new-vs` diffs two passes against each other to surface lines one of them missed.

The spoken material — the narration, the phone calls, and episode 17, the one episode with no screens in it — is transcribed separately with `transcribe.py`, which runs faster-whisper over the episodes and writes one SRT each. The audio here is unusually sparse, so that script turns on voice-activity detection and the repetition guards; without them Whisper invents dialogue in the silences.

The interval is the decision that matters, and it should be set by the shortest-lived window rather than the busiest one. The IRC channel is forgiving, because chat scrolls slowly and lines sit on screen for a long time. A private IM open for thirty seconds is not, and neither is a background conversation in another language — at a coarser setting either can fall entirely between frames. Several of the season's turning points happen in windows that are open for only a few seconds.

### Season 2

*The Scene 2.0* was recovered the same way, but it is a different series technically. Season 1 lives in mIRC, so a chat extractor that knows `<nick>` gets most of it. Season 2's characters are on Gaim talking Jabber (`user@jabber.org/Resource:`) and on AIM (`DisplayName99:`), with mIRC appearing in only two of the twenty (episodes 1 and 8) — a season 1 extractor returns a line or two per episode and looks like a failed OCR run rather than the wrong tool.

Two things follow from that, and both cost time before they were noticed. `chatlog.py` reads all three forms — it handles mIRC too, so season 1 can be re-derived with it, and the earlier passes it replaced are no longer in the repository. Handles have to be clustered across spellings, because OCR reads the same JID a dozen ways and the differences are exactly the confusable glyphs (`0`/`o`, `1`/`l`/`!`, `rn`/`m`); that is `normalize.py`, and the survivors are checked against frames rather than trusted, with `handles.txt` overriding the statistics where a frame settles it. And the chat is not where the season's answers are — the delivery address, the shipment confirmation and the letter that explains the whole thing are in a mail window and a PDF, in plain prose and in lines too short to look like prose at all — `prose.py` and `chrome.py` are the two sweeps that pick those up.

### The scripts

| Script | What it does |
| --- | --- |
| `ocr2.sh` | Samples an episode at one frame every 3 seconds, upscales 2×, runs Tesseract |
| `chatlog.py` | Chat lines: mIRC, Jabber and AIM in one pass, with the duplicate collapsing. `--all` keeps every line instead, timestamped; `--new-vs old new` prints what a second OCR pass gained |
| `normalize.py`, `handles.txt` | Cluster the spellings OCR produces for one handle down to a single name |
| `prose.py` | The non-chat screen text — emails, letters, confirmations, addresses |
| `chrome.py` | The data-bearing window furniture: IPs, paths, ports, URLs, clocks |
| `transcribe.py` | faster-whisper over the episodes, one SRT each |
| `mkhtml.py` | Builds a self-contained HTML edition from a synopsis or the character index: `python3 scripts/mkhtml.py <file>.md` (needs `markdown-it-py`) |

## Known limits

- OCR is imperfect on 640×480 source video. Nicks and character names come through reliably; individual words are sometimes mangled, and the logs preserve those errors rather than guessing at them.
- Text rendered in light colors — often one side of an IM conversation — reads less reliably than dark text, so some exchanges are captured mostly from one participant.
- Handwriting is beyond it entirely. The whiteboard in episode 17 is perfectly legible to a viewer — it reads `Top Down`, `Leader - Drosan`, `Encoder - Pyro`, `Affil - slipknot`, and a boxed `Ed Koenig / Teflon` — but Tesseract recovers none of it. Anything handwritten has to be read by eye.
- The transcripts are machine-generated and mishear things, particularly under music. Where Whisper produced lyrics beneath a score, those lines are noise rather than dialogue.
- Worse, at the wrong settings they drop whole scenes with nothing in the output to mark the loss. `medium.en` with stock VAD rendered a four-and-a-half-minute confrontation in season 1's episode 14 as one subtitle containing two sentences — the rest of it, including the only time the series says the encoder's name aloud, was simply not in the SRT. The score is mixed loud enough that the detector finds no speech beneath it.
- The fix is to separate the vocals from the music first. Re-running that episode with Purfview's Faster-Whisper-XXL — `--ff_vocal_extract mdx_kim2 -m large-v2 --vad_method pyannote_v3 --standard` — returned 61 subtitles where the first pass gave 11. Use that configuration rather than the one `transcribe.py` defaults to, which is kept as the minimal Python equivalent.
- Not everything in this series is chat. Email windows, browser tabs, file listings and desktop icons carry real information, and a sweep for chat-style lines alone will miss them — the tuition letter in episode 1, teflon's note to his boss in episode 5 and the "access issue" mail in episode 6 were all recovered by looking for `From:` and `Subject:` headers rather than nicks.

## The series

Produced by Jun Group Entertainment, directed by Mitchell Reichgut, and released free on the web and onto P2P networks. Season 1 ran 20 episodes from November 2004; a second season, *The Scene 2.0*, followed in 2006.

- [Wikipedia](https://en.wikipedia.org/wiki/The_Scene_(miniseries)) — production background, cast, format, and the parody series *Teh Scene*
- [IMDb](https://www.imdb.com/title/tt2201890/) — [full credits](https://www.imdb.com/title/tt2201890/fullcredits/), [episode list](https://www.imdb.com/title/tt2201890/episodes/?year=2004)
- [Internet Archive — The Scene Season 1](https://archive.org/details/the_scene_season_1) — all 20 episodes in several formats, plus torrents
- [Internet Archive — The Scene 2.0](https://archive.org/details/welcometothescene_version2.0_xvid) — the 2006 sequel, all 20 episodes
- [Internet Archive — Welcome to the Scene](https://archive.org/details/welcome-to-the-scene) — an alternate upload under the original release name
- [The Movie Database](https://www.themoviedb.org/tv/91461-the-scene) — episode metadata

## A note on the material

The recovered screen text and the audio transcripts are deliberately left out of this repository. Together they amount to most of the series' script.

The license is printed on screen at the end of episode 1: *Copyright (c) 2004 Jun Group, Inc. This work may be redistributed under the Creative Commons Attribution-NoDerivs license*, linking to `creativecommons.org/licenses/by-nd/2.0/`. That is **CC BY-ND 2.0** — share it freely, commercially or not, but don't distribute derivative works. (Secondary sources get this wrong: the Internet Archive upload's metadata adds a NonCommercial term the series never claimed.) Season 2 prints no licence card in any of its twenty episodes, so its terms rest on the Archive's metadata alone, which season 1 shows to be unreliable; it is treated here as season 1 is. A complete transcript would not obviously fall inside *NoDerivatives*, which is why it isn't here.

The synopsis is original writing and quotes only short passages, so that term doesn't reach it. The frames in `stills/` are reproduced alongside commentary on what each one shows; they remain Jun Group's. The `scripts/` directory will regenerate the screen logs and transcripts from your own copy of the episodes, which are freely available from the Internet Archive links above.
