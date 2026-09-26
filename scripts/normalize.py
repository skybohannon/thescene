"""Collapse OCR variants of the same handle.

Both chat clients in this series defeat OCR in the same way. mIRC renders a
slashed zero that Tesseract reads as 0, 6 or 8 at random; Gaim's Jabber lines
are small and lose or double characters at the window edge. So one person
arrives as a family of spellings -- sng330/sng336/sng3360/s5ng330, or
tann3r@jabber.org/tannBr@jabber.org/tann3r@jabber.orq.

Confusable glyphs are mapped onto each other, the resulting keys are clustered
by similarity, and every member of a cluster is rewritten to its most frequent
spelling. Distinct handles that genuinely resemble each other would be merged
too, so the threshold is high and every merge is reported on stderr.

Handles the input, in either form:
    <nick> text
    user@server[/Resource]: text

    python3 normalize.py <chat.txt> > <out.txt>
"""
import re, sys, collections, difflib

SPEAKER = re.compile(r'^(<[^>]{2,16}>'
                     r'|[A-Za-z0-9._!-]{2,24}@[A-Za-z0-9.-]{3,30}(?:/\w{1,12})?:'
                     r'|[A-Za-z][A-Za-z0-9_]{2,20}:)(.*)')
CONF = str.maketrans({'0':'o','6':'o','8':'o','9':'g','5':'s','1':'l','7':'t','q':'g','|':'l'})

def core(sp):
    """The identifying part of a speaker token: nick, or the local part of a JID."""
    s = sp.strip('<>:')
    return s.split('@')[0] if '@' in s else s

def key(n):
    return re.sub(r'(.)\1+', r'\1', core(n).lower().translate(CONF))

# A spelling seen once or twice beside one seen often is almost certainly the
# same person misread, so it is allowed to fold in on weaker evidence.
RATIO, RARE_RATIO, RARE_MAX, ANCHOR_MIN = 0.78, 0.68, 3, 8

# Spellings confirmed by looking at the frames. Anything clustering close to
# one of these is rewritten to it. Add to this list rather than tuning the
# thresholds: reading the screen is evidence, and the thresholds are not.
ALIASES = [l.strip() for l in open(
    __import__('os').path.join(__import__('os').path.dirname(
        __import__('os').path.abspath(__file__)), 'handles.txt'),
    encoding='utf-8')] if __import__('os').path.exists(
    __import__('os').path.join(__import__('os').path.dirname(
        __import__('os').path.abspath(__file__)), 'handles.txt')) else []
ALIASES = [a for a in ALIASES if a and not a.startswith('#')]

lines = [l.rstrip('\n') for l in open(sys.argv[1], encoding='utf-8', errors='replace')]
counts = collections.Counter(m.group(1) for l in lines
                             for m in [SPEAKER.match(l)] if m)

clusters = []                       # [set of raw speaker tokens, representative key]
for sp in sorted(counts, key=lambda n: -counts[n]):
    k = key(sp)
    for c in clusters:
        r = difflib.SequenceMatcher(None, k, c[1]).ratio()
        anchor = max(counts[m] for m in c[0])
        limit = RARE_RATIO if (counts[sp] <= RARE_MAX and anchor >= ANCHOR_MIN) else RATIO
        # OCR also drops the first character or two, leaving a fragment of a
        # handle already seen ("Unman@" for "tinman@"). Containment catches
        # those, which similarity alone scores too low.
        contained = len(k) >= 4 and (k in c[1] or c[1] in k)
        # OCR misreads the first glyph or two more often than the rest, so two
        # handles sharing a long tail and differing only at the head are the
        # same handle ("unman" for "tinman"). Requiring the shared tail keeps
        # this from swallowing genuinely different names ("talisman").
        tail = (len(k) >= 5 and len(c[1]) >= 5 and abs(len(k) - len(c[1])) <= 2
                and k[-4:] == c[1][-4:] and r >= 0.70)
        if r >= limit or contained or tail:
            c[0].add(sp)
            break
    else:
        clusters.append([{sp}, k])

canon = {}
for members, _ in clusters:
    # The most frequent spelling is not always the right one -- OCR can land on
    # the same wrong reading repeatedly. Pick the medoid instead: the spelling
    # closest, on average, to every other spelling in the cluster, weighted by
    # how often each was seen. A true reading sits in the middle of its errors;
    # a systematic misreading sits off to one side.
    def centrality(n):
        kn = key(n)
        return sum(counts[m] * difflib.SequenceMatcher(None, kn, key(m)).ratio()
                   for m in members)
    winner = max(members, key=lambda n: (centrality(n), counts[n]))
    # A hand-checked spelling always wins over whatever the statistics prefer:
    # these were read off the frames by eye, which OCR cannot be talked into.
    # Test every member, not just the winner -- the winner may itself be the
    # misreading that sits furthest from the confirmed spelling.
    best = None
    for canonical in ALIASES:
        kc = key(canonical)
        r = max(difflib.SequenceMatcher(None, kc, key(m)).ratio() for m in members)
        if r >= 0.80 and (best is None or r > best[0]):
            best = (r, canonical)
    if best:
        winner = best[1]
    for n in members:
        canon[n] = winner
    if len(members) > 1:
        others = sorted(members - {winner}, key=lambda n: -counts[n])
        print('  %-28s <- %s' % (winner, ', '.join('%s(%d)' % (o, counts[o]) for o in others)),
              file=sys.stderr)

out = []
for l in lines:
    m = SPEAKER.match(l)
    out.append(canon[m.group(1)] + m.group(2) if m else l)
print('\n'.join(out))
