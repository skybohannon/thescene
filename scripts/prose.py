"""Recover the non-chat screen text: emails, confirmations, web pages.

Not everything in this series happens in a chat window. Season 1 hid a tuition
letter, an apology to a boss and an "access issue" mail in ordinary email
windows, and season 2 does the same -- episode 16's whole emotional payload is
a long email, not an IM. A sweep that looks only for chat lines misses all of
it, so this is the other half of the pass.

The problem here is the opposite of chat's. A message being typed or scrolled
is captured many times, each a slightly longer or shorter fragment of the same
sentence, interleaved with toolbar noise. So: keep anything that reads like
prose, group the fragments by their opening, and emit the longest version of
each -- which is the sentence at its most complete.

    python3 prose.py <raw_ocr.txt> > <documents.txt>
"""
import re, sys, collections

COMMON = set(("the a an and or but if of to in on at for with from by as is are was were "
              "be been being have has had do does did will would can could should may might "
              "i you he she it we they me him her us them my your his our their this that "
              "these those not no yes so all any some what when where who how why there here "
              "about after again before down get just know like make now only out over than "
              "then think time up want way well back come day give good great even much must "
              "need new other people right said say see still take tell thing told too two "
              "very want week work year your don't i'm it's you're that's can't didn't").split())

CHROME = re.compile(
    r'(file\s+edit\s+view|conversation\s+options|send\s+as|warn\s+block|start\s+menu|'
    r'copyright\s*[@(]|all\s+rights\s+reserved|terms\s+of\s+service|bookmarks\s+tools|'
    r'firefox\s+(help|support)|mozilla\s+firefox|internet\s+explorer|'
    r'save\s+as\s+a\s+draft|check\s+mail|sign\s+out|my\s+(yahoo|account)|'
    r'^\s*(re|fwd|cc|bcc)\s*:\s*$)', re.I)

# Records are not prose and the test below rejects them, but an address, an amount or
# a confirmation number is often the single most load-bearing thing on the screen --
# episode 16's delivery address is the answer to the whole season. Keep those too.
RECORD = re.compile(
    r'(\b[A-Z][a-z]+,\s*(China|Japan|Korea|Iran|Estonia|Switzerland|Suisse|England)\b'
    r'|\b[A-Z][a-z]+,\s*(NJ|NY|PA|CA|VA|MD|DC)\b'
    r'|\bNo\.\s*\d+|\b\d{1,5}\s+\w+\s+(Lu|Street|St|Ave|Avenue|Road|Rd)\b'
    r'|confirmation\s*#\s*\d|routing (number|#)|router number\s*\d'
    r'|\$\s?[\d,]+\.\d{2}|\$\s?\d{2,3}[,kK]\b'
    r'|SIGNED BY|\bRECEIVED [A-Z]{3,}|\b\d{4}-\d{2}-\d{2}\b'
    r'|[A-Za-z0-9._-]+@(yahoo|gmail|hotmail)\.com)')

def prosey(s):
    if len(s) < 22:
        return False
    words = re.findall(r"[A-Za-z][A-Za-z'\-]+", s)
    if len(words) < 4:
        return False
    letters = sum(c.isalpha() or c.isspace() for c in s)
    if letters / len(s) < 0.72:
        return False
    hits = sum(1 for w in words if w.lower() in COMMON)
    return hits >= 2 and hits / len(words) >= 0.2

# Lines the chat pass already has; they are not documents.
CHAT = re.compile(r'<[A-Za-z0-9_\[\]\\^{}|`-]{2,16}>'
                  r'|[A-Za-z0-9._!-]{2,24}[@\u00ae\u00a9\u00b0][A-Za-z0-9.-]{3,30}(?:[/,]\s?\w{1,12})?\s*[:;]'
                  r'|\b[A-Za-z][A-Za-z0-9_]{2,15}?[0-9][A-Za-z0-9_]{0,6}\s*[:;]\s')

# OCR reads | as I and vice versa constantly in body text; fold for keying only.
def fold(s):
    return re.sub(r'[^a-z0-9 ]', '', s.lower().replace('|', 'i')).strip()

# For grouping the many partial captures of one sentence, fold the glyph pairs
# OCR swaps most often, so "hall from" and "hall trorn" land in the same bucket.
def gkey(s):
    k = fold(s).replace(' ', '')
    for a, b in (('rn', 'm'), ('t', 'f'), ('i', 'l'), ('0', 'o'), ('5', 's'), ('1', 'l')):
        k = k.replace(a, b)
    return k[:16]

t = None
best = {}           # opening-of-sentence -> (longest text, first timestamp)
for line in open(sys.argv[1], encoding='utf-8', errors='replace'):
    s = ' '.join(line.split())
    m = re.match(r'### t=(\d+):(\d+)', s)
    if m:
        t = int(m.group(1)) * 60 + int(m.group(2))
        continue
    if t is None or CHAT.search(s):
        continue
    if not (RECORD.search(s) or (not CHROME.search(s) and prosey(s))):
        continue
    f = fold(s)
    key = gkey(s)
    if key not in best or len(f) > len(fold(best[key][0])):
        best[key] = (s, best.get(key, (None, t))[1])

# A fragment whose opening is contained in a longer kept line is that line's
# earlier, shorter capture; drop it.
kept = sorted(best.values(), key=lambda x: x[1])
folded = [fold(s) for s, _ in kept]
out = []
for i, (s, ts) in enumerate(kept):
    if any(i != j and folded[i] in folded[j] for j in range(len(kept))):
        continue
    out.append('[%d:%02d] %s' % (ts // 60, ts % 60, s))
print('\n'.join(out))
