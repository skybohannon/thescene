# -*- coding: utf-8 -*-
"""Check the character index against the synopses.

    python3 scripts/check.py

Two things drift when a synopsis is edited and the index isn't:

- The Episodes column. It is defined as the episode entries that name the
  character, so it can be recomputed from the synopses and compared.
- The handles. Every speaker in a quoted chat log should be someone the index
  knows about; a new one means a row (and an entry in characters.py) is due.

Prints each disagreement and exits 1 if there are any.
"""
import io, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from characters import HANDLES, BOUND, anchor_for

SYNOPSES = {1: 'The-Scene-S01-Episode-Synopses.md', 2: 'The-Scene-S02-Episode-Synopses.md'}
INDEX_MD = 'The-Scene-Characters.md'

# Things quoted in the same bold form as a chat speaker that aren't one: mail
# headers, and the unnamed voices transcribed from the spoken scenes.
IGNORED_SPEAKERS = {'Date', 'From', 'Subject', 'To', 'Man', 'Woman'}


def episodes(path):
    """Episode number -> the text of its entry, up to the next heading."""
    text = io.open(path, encoding='utf-8').read()
    parts = re.split(r'^## Episode (\d+) .*$', text, flags=re.M)
    out = {}
    for i in range(1, len(parts), 2):
        out[int(parts[i])] = re.split(r'^#{2,3} ', parts[i + 1], flags=re.M)[0]
    return out


def named_in(eps, spellings):
    rx = re.compile(BOUND % '|'.join(map(re.escape, spellings)))
    return sorted(n for n, body in eps.items() if rx.search(body))


def parse_spec(spec):
    """'all 20', 'every episode but 4 and 6', '1–5, 7, 12–20' -> a list.
    None for anything that isn't a list of episodes ('the whole season')."""
    spec = spec.strip()
    if spec == 'all 20':
        return list(range(1, 21))
    m = re.match(r'every episode but (.+)$', spec)
    if m:
        skip = [int(x) for x in re.findall(r'\d+', m.group(1))]
        return [n for n in range(1, 21) if n not in skip]
    if not re.fullmatch(r'[\d\s,–-]+', spec):
        return None
    out = []
    for part in spec.split(','):
        a, _, b = part.strip().replace('–', '-').partition('-')
        out +=list(range(int(a), int(b) + 1)) if b else [int(a)]
    return out


def format_spec(eps):
    """The same list written the way the index writes it."""
    if eps == list(range(1, 21)):
        return 'all 20'
    missing = [n for n in range(1, 21) if n not in eps]
    if 0 < len(missing) <= 2:
        return 'every episode but ' + ' and '.join(map(str, missing))
    runs, start = [], None
    for i, n in enumerate(eps):
        if start is None:
            start = n
        if i + 1 == len(eps) or eps[i + 1] != n + 1:
            runs.append(str(start) if start == n else '%d–%d' % (start, n))
            start = None
    return ', '.join(runs)


def index_rows():
    """(season, anchor) -> the Episodes cell of that character's first row."""
    rows, header = {}, None
    for line in io.open(INDEX_MD, encoding='utf-8'):
        if not line.startswith('|'):
            header = None
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if header is None:
            header = cells
            continue
        if set(''.join(cells)) <= set('- '):
            continue
        if 'Episodes' not in header:
            continue
        found = anchor_for(re.sub(r'[*`]', '', cells[0]))
        if found and found not in rows:
            rows[found] = cells[header.index('Episodes')]
    return rows


def speakers(path):
    """Every nick that speaks in a quoted chat log."""
    text = io.open(path, encoding='utf-8').read()
    out = set()
    for line in text.splitlines():
        if not line.startswith('>'):
            continue
        m = re.match(r'>\s*\*\*(?:&lt;|<)([^&<>*]+?)(?:&gt;|>)\*\*', line) or \
            re.match(r'>\s*\*\*([^*:]+?):\*\*', line)
        if m:
            out.add(m.group(1).strip())
    return out


def main():
    problems = []
    rows = index_rows()

    for season, path in SYNOPSES.items():
        eps = episodes(path)
        for anchor, spellings in HANDLES[season]:
            cell = rows.get((season, anchor))
            if cell is None:
                problems.append('%s: s%d-%s has no row with an Episodes column' % (INDEX_MD, season, anchor))
                continue
            listed = parse_spec(cell)
            if listed is None:
                continue
            actual = named_in(eps, spellings)
            if listed != actual:
                problems.append('%s: s%d-%s lists "%s", but the synopsis names them in "%s"'
                                % (INDEX_MD, season, anchor, cell, format_spec(actual)))

        known = re.compile(BOUND % '|'.join(re.escape(h) for _, hs in HANDLES[season] for h in hs))
        for nick in sorted(speakers(path)):
            if nick not in IGNORED_SPEAKERS and not known.fullmatch(nick):
                problems.append('%s: chat speaker "%s" is not in characters.py' % (path, nick))

    for p in problems:
        print(p)
    print('%d problem%s' % (len(problems), '' if len(problems) == 1 else 's'))
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
