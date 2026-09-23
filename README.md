# The Scene (2004–2006) — reconstruction

*The Scene* is a 20-episode web series about warez groups and the people in them. Roughly 90% of it is told through on-screen text — IRC channels, instant messages, FTP and application windows that the viewer reads rather than hears — with an opening narration, phone calls, and two entirely spoken episodes carrying the rest.

No episode-by-episode synopsis of it appears to exist: the databases that list the series leave their plot fields blank. This repository is one, plus the pipeline that produced it.

## Contents

| Path | What it is |
| --- | --- |
| `The-Scene-S01-Episode-Synopses.md` | The synopsis: all 20 episodes, POV per episode, character notes, and the threads that pay off across the season |
| `stills/` | Nine frames from the episodes, referenced by the synopsis |
| `scripts/` | The pipeline that recovered the text it was written from |
| `LICENSE` | CC BY 4.0, covering the writing here — not the series |

The recovered screen text and the audio transcripts themselves are **not** published here — see *A note on the material* below.

## Method

Every episode was sampled at **one frame every 3 seconds** (`ocr2.sh`), upscaled 2×, and read with Tesseract. `chatlog2.py` pulls chat-style lines out of the raw OCR and collapses the duplicates that come from the same line persisting across many frames. `newlines.py` diffs two passes against each other to surface lines one of them missed.

The spoken material — the narration, the phone calls, and the two episodes with no screens in them — is transcribed separately with `transcribe.py`, which runs faster-whisper over the episodes and writes one SRT each. The audio here is unusually sparse, so that script turns on voice-activity detection and the repetition guards; without them Whisper invents dialogue in the silences.

The interval is the decision that matters, and it should be set by the shortest-lived window rather than the busiest one. The IRC channel is forgiving, because chat scrolls slowly and lines sit on screen for a long time. A private IM open for thirty seconds is not, and neither is a background conversation in another language — at a coarser setting either can fall entirely between frames. Several of the season's turning points happen in windows that are open for only a few seconds.

## Known limits

- OCR is imperfect on 640×480 source video. Nicks and character names come through reliably; individual words are sometimes mangled, and the logs preserve those errors rather than guessing at them.
- Text rendered in light colors — often one side of an IM conversation — reads less reliably than dark text, so some exchanges are captured mostly from one participant.
- Handwriting is beyond it entirely. The whiteboard in episode 17 is perfectly legible to a viewer — it reads `Top Down`, `Leader - Drosan`, `Encoder - Pyro`, and a boxed `Ed Koenig / Teflon` — but Tesseract recovers none of it. Anything handwritten has to be read by eye.
- The transcripts are machine-generated and mishear things, particularly under music. Where Whisper produced lyrics beneath a score, those lines are noise rather than dialogue.
- Not everything in this series is chat. Email windows, browser tabs, file listings and desktop icons carry real information, and a sweep for chat-style lines alone will miss them — the tuition letter in episode 1, teflon's note to his boss in episode 5 and the "access issue" mail in episode 6 were all recovered by looking for `From:` and `Subject:` headers rather than nicks.

## The series

Produced by Jun Group Entertainment, directed by Mitchell Reichgut, and released free on the web and onto P2P networks. Season 1 ran 20 episodes from November 2004; a second season, *The Scene 2.0*, followed in 2006.

- [Wikipedia](https://en.wikipedia.org/wiki/The_Scene_(miniseries)) — production background, cast, format, and the parody series *Teh Scene*
- [IMDb](https://www.imdb.com/title/tt2201890/) — [full credits](https://www.imdb.com/title/tt2201890/fullcredits/), [episode list](https://www.imdb.com/title/tt2201890/episodes/?year=2004)
- [Internet Archive — The Scene Season 1](https://archive.org/details/the_scene_season_1) — all 20 episodes in several formats, plus torrents
- [Internet Archive — Welcome to the Scene](https://archive.org/details/welcome-to-the-scene) — an alternate upload under the original release name
- [The Movie Database](https://www.themoviedb.org/tv/91461-the-scene) — episode metadata

## A note on the material

The recovered screen text and the audio transcripts are deliberately left out of this repository. Together they amount to most of the series' script.

The license is printed on screen at the end of episode 1: *Copyright (c) 2004 Jun Group, Inc. This work may be redistributed under the Creative Commons Attribution-NoDerivs license*, linking to `creativecommons.org/licenses/by-nd/2.0/`. That is **CC BY-ND 2.0** — share it freely, commercially or not, but don't distribute derivative works. (Secondary sources get this wrong: the Internet Archive upload's metadata adds a NonCommercial term the series never claimed.) A complete transcript would not obviously fall inside *NoDerivatives*, which is why it isn't here.

The synopsis is original writing and quotes only short passages, so that term doesn't reach it. The nine frames in `stills/` are reproduced alongside commentary on what each one shows; they remain Jun Group's. The `scripts/` directory will regenerate the screen logs and transcripts from your own copy of the episodes, which are freely available from the Internet Archive links above.
