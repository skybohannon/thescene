"""Pull chat lines out of raw OCR, for every client this series uses.

Season 1 is mIRC throughout and writes      <nick> text
Season 2 is mostly Gaim talking Jabber:     user@server[/Resource]: text
and also has AIM/Yahoo windows:             DisplayName99: text
with a few mIRC scenes still in mIRC form.

The bare-display-name form is the awkward one, because window chrome
("Conversation Options Send As") and stray OCR look just like it. Those vary
from frame to frame while a real conversant recurs, so a bare name is only
accepted once it has been seen MIN_SIGHTINGS times in the episode.

Each line is emitted once; a line that sits on screen across many frames would
otherwise repeat dozens of times.

    python3 chatlog.py <raw_ocr.txt> > <chat.txt>

Two other things you want often enough that they live here rather than in
scripts of their own:

    python3 chatlog.py --all <raw_ocr.txt>          every deduped line, timestamped
    python3 chatlog.py --new-vs <old> <new>         lines the second pass found

--all keeps everything, not just chat, with the frame time each line first
appeared at; it is the net to use before you know what a season looks like.
--new-vs answers "did re-running the OCR actually gain anything", which is the
only honest way to decide whether a second pass was worth it.
"""
import re, sys, collections

IRC    = re.compile(r'<([A-Za-z0-9_\[\]\\^{}|`-]{2,16})>\s*(.*)')
# OCR turns @ into (R)/(C) and : into ; often enough to lose whole exchanges,
# so the separators are matched loosely and rewritten to their real form.
JABBER = re.compile(r'([A-Za-z0-9._!-]{2,24})[@\u00ae\u00a9\u00b0]([A-Za-z0-9.-]{3,30}(?:[/,]\s?\w{1,12})?)\s*[:;]\s*(.+)')
# Every IM screen name in this series carries a digit (MikeyD5550, DanikaLi99,
# jimbrandon993), and requiring one is what keeps window chrome and mid-word
# OCR breaks ("R esponse:", "f rind:") out of the speaker column.
NAME   = re.compile(r'(?:^|[|\]}>)\s])\s*([A-Za-z][A-Za-z0-9_]{2,15}?[0-9][A-Za-z0-9_]{0,6})\s*[:;]\s+(.+)')

CHROME = re.compile(r'^(conversation|options|send|warn|block|file|edit|view|help|tools|'
                    r'buddies|accounts|format|insert|people|actions|window|commands|'
                    r'favorites|status|address|subject|from|to|cc|bcc|inbox|search|date|sent|'
                    r'time|size|name|type|phone|fax|tel|url|id|reply|forward|'
                    r'http|https|www|re|fwd|note|error|warning|password|user|login)$', re.I)
MIN_SIGHTINGS = 4

# The window border and scrollbar land inside the line as a short run of
# nonsense; strip trailing tokens no English line would end on.
KEEP = {'a','i','no','ok','so','to','up','us','we','he','it','is','my','on','in','of',
        'be','do','go','if','me','or','at','as','by','an','id','ip','pm','am','hi',
        'the','and','you','but','are','for','not','was','her','him','his','out','get',
        'got','all','can','did','yes','job','day','now','how','why','who','one','two',
        'ten','off','own','new','why','say','see','try','let','man','yet','far','bad'}
def strip_edge(t):
    for _ in range(4):
        m = re.search(r'\s+([^\s]{1,3})$', t)
        if not m:
            break
        tok = m.group(1).lower().strip('.,?!:;')
        if tok in KEEP or re.fullmatch(r'[0-9]{1,3}', tok):
            break
        t = t[:m.start()].rstrip()
    return t.strip()

def extract(path):
  raw = [l.strip() for l in open(path, encoding='utf-8', errors='replace')]
  raw = [l for l in raw if l and not l.startswith('### t=')]

  # first pass: which bare names recur often enough to be real?
  cand = collections.Counter()
  for s in raw:
      if IRC.search(s) or JABBER.search(s):
          continue
      m = NAME.search(s)
      if m and not CHROME.match(m.group(1).strip()):
          cand[m.group(1).strip()] += 1
  real = {n for n, c in cand.items() if c >= MIN_SIGHTINGS}

  # ---- pass 2: collect every candidate message -------------------------------
  msgs = []
  for s in raw:
      m = IRC.search(s)
      if m:
          who, what = '<%s>' % m.group(1), m.group(2)
      else:
          m = JABBER.search(s)
          if m:
              who, what = '%s@%s:' % (m.group(1), m.group(2).replace(', ', '/')), m.group(3)
          else:
              m = NAME.search(s)
              if not m or m.group(1).strip() not in real:
                  continue
              who, what = '%s:' % m.group(1).strip(), m.group(2)
      what = strip_edge(what)
      if what:
          msgs.append((who, what))

  # ---- pass 3: strip trailing junk using the episode's own vocabulary ---------
  # A line that sits on screen for a minute is captured twenty times, each with a
  # different scrap of window border on the end. Real words recur across those
  # captures; the scraps do not. So treat a token seen VOCAB_MIN times anywhere
  # as a word, and drop trailing tokens that never earned that.
  VOCAB_MIN = 3
  vocab = collections.Counter()
  for _, what in msgs:
      vocab.update(w.lower().strip('.,?!:;"\'') for w in what.split())
  words = {w for w, c in vocab.items() if c >= VOCAB_MIN and w}

  def strip_junk(t):
      toks = t.split()
      while len(toks) > 1:
          last = toks[-1].lower().strip('.,?!:;"\'')
          if last in words or last in KEEP or re.fullmatch(r'[0-9$.,]+', last):
              break
          toks.pop()
      t = ' '.join(toks)
      # A question mark ends an IM line. Anything after the last one that is only
      # a word or three is the next window showing through, not a reply.
      m = re.search(r'[?!]', t[::-1])
      if m:
          cut = len(t) - m.start()
          tail = t[cut:].split()
          if 0 < len(tail) <= 4:
              t = t[:cut]
      return t.strip()

  seen, out = set(), []
  for who, what in msgs:
      what = strip_junk(what)
      if not what:
          continue
      text = '%s %s' % (who, what)
      key = (re.sub(r'[^a-z0-9]', '', who.lower()),
             re.sub(r'[^a-z0-9]', '', what.lower())[:22])
      if len(key[1]) < 6 or key in seen:
          continue
      seen.add(key)
      out.append(text)
  return out

if __name__ == '__main__':
    if sys.argv[1] == '--all':
        # Every line the OCR found, deduped, tagged with the frame time it first
        # appeared at. No chat filter: emails, dialogs and window furniture too.
        seen, out, cur = set(), [], '0:00'
        for line in open(sys.argv[2], encoding='utf-8', errors='replace'):
            line = line.rstrip()
            if line.startswith('### t='):
                cur = line[6:]
                continue
            t = line.strip()
            key = re.sub(r'[^a-z0-9]', '', t.lower())[:45]
            if len(key) < 8 or key in seen:
                continue
            seen.add(key)
            out.append('[%s] %s' % (cur, t))
        print('\n'.join(out))
    elif sys.argv[1] == '--new-vs':
        old = {re.sub(r'[^a-z0-9]', '', l.lower())[:34] for l in extract(sys.argv[2])}
        for l in extract(sys.argv[3]):
            if re.sub(r'[^a-z0-9]', '', l.lower())[:34] not in old:
                print(l)
    else:
        print('\n'.join(extract(sys.argv[1])))
