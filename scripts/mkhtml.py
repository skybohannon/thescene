# -*- coding: utf-8 -*-
import io, os, re, sys, base64, html
from markdown_it import MarkdownIt

# usage: python3 scripts/mkhtml.py [--web OUTDIR] <file.md>
#
# By default writes the matching .html next to the source, self-contained:
# the frames are embedded, so the one file can be read anywhere. With --web
# the frames are linked from stills/ and lazy-loaded instead, and the page
# goes to OUTDIR -- that is the GitHub Pages build.
args = sys.argv[1:]
WEB = None
if args[:1] == ['--web']:
    WEB, args = args[1], args[2:]
SRC = args[0] if args else 'The-Scene-S01-Episode-Synopses.md'
NAME = re.sub(r'\.md$', '', os.path.basename(SRC)) + '.html'
OUT = os.path.join(WEB, NAME) if WEB else re.sub(r'\.md$', '', SRC) + '.html'
SITE = 'https://skybohannon.github.io/thescene/'
SEASON = 1 if 'S01' in NAME else 2 if 'S02' in NAME else None

md_text = io.open(SRC, encoding='utf-8').read()
md = MarkdownIt('commonmark', {'typographer': False}).enable(['table'])
body = md.render(md_text)

# --- frames: embedded, or linked and lazy-loaded for the web --------------
stills = re.findall(r'src="([^"]+\.jpg)"', body)

def embed(m):
    src = m.group(1)
    path = src
    if not os.path.exists(path):
        return m.group(0)
    if WEB:
        return 'loading="lazy" src="%s"' % src
    b = base64.b64encode(open(path, 'rb').read()).decode('ascii')
    return 'src="data:image/jpeg;base64,%s"' % b

body = re.sub(r'src="([^"]+\.jpg)"', embed, body)

# --- links to a sibling .md point at its HTML edition instead -------------
body = re.sub(r'href="([^":/]+)\.md"', r'href="\1.html"', body)

# --- "Where to look": each start time opens the episode at that second ----
# The timings were taken from the Internet Archive's H.264 encodes, so they
# link to those files. Season 2's episodes are numbered from zero there.
def episode_url(ep):
    if SEASON == 1:
        return 'https://archive.org/download/the_scene_season_1/the_scene_xvid_episode_%d.mp4' % ep
    return 'https://archive.org/download/welcometothescene_version2.0_xvid/episode2.%d_xvid.mp4' % (ep - 1)

def link_timings(section):
    def row(m):
        tr = m.group(0)
        cells = re.findall(r'<td>(.*?)</td>', tr, flags=re.S)
        if not cells or not cells[0].strip().isdigit():
            return tr
        url = episode_url(int(cells[0]))
        def t(tm):
            mins, secs = tm.group(1), tm.group(2)
            return '<a href="%s#t=%d">%s:%s</a>' % (url, int(mins) * 60 + int(secs), mins, secs)
        last = cells[-1]
        linked = re.sub(r'(?<![\d:])(\d{1,2}):(\d\d)(?![\d:])', t, last, count=1)
        return tr.replace('<td>%s</td>' % last, '<td>%s</td>' % linked)
    return re.sub(r'<tr>.*?</tr>', row, section, flags=re.S)

if SEASON:
    body = re.sub(r'(<h3>Where to look</h3>)(.*?)(?=<h[23][ >]|\Z)',
                  lambda m: m.group(1) + link_timings(m.group(2)), body, flags=re.S)

# --- characters link to their row in the character index ------------------
# Anchor, then every handle and name that belongs to it. Longer spellings are
# tried first, so a full Jabber ID wins over the bare nick inside it. Season 2
# mostly calls people by name, so names are here as well as handles.
HANDLES = {
    1: [('drosan', ['BrianSan333', 'BrianSan', 'dro_5544', 'Drosan']),
        ('teflon', ['monticello235', 'copleyr785', 'collangello998', 'spinnaker', 'teflon']),
        ('trooper', ['troopercamy', 'trooper', 'Jodi']),
        ('pyr0', ['pyr0']),
        ('slipknot', ['slipknot']),
        ('coda', ['cOda']),
        ('melissa', ['melissbliss04', 'Melissa']),
        ('dana', ['danaburke123', 'danaburke55']),
        ('todd', ['Tremor2212', 'Todd']),
        ('suzy', ['suzyxiao', 'Suzy']),
        ('luckychi', ['LuckyChi2203']),
        ('gryffin', ['gryffin']),
        ('burroughs', ['burroughs485', 'Burroughs']),
        ('agents', ['brenner2604', 'alanmeans06'])],
    2: [('danika', ['houdini6@jabber.org', 'houdini6', 'DanikaLi99', 'sng330', 'lukai', 'Danika']),
        ('talisman', ['talisman']),
        ('t0mb0', ['t0mb0@jabber.org', 't0mb0', 'Tomasz']),
        ('stan', ['tann3r@jabber.org', 'tann3r', 'Stan']),
        ('murph', ['t!nman@jabber.org', 't!nman', 'spartan', 'Murph']),
        ('ralph', ['jimbrandon09@jabber.org', 'jimbrandon09', 'Ralph Lasky', 'Ralph']),
        ('mike', ['MikeyD5550', 'Mike Davis']),
        ('katerina', ['Katerina']),
        ('vicky', ['Vicky']),
        ('zhen', ['bellbird', 'Zhen']),
        ('greenberg', ['Greenberg']),
        ('cunningham', ['Michael Cunningham', 'Cunningham']),
        ('laurent', ['J. Laurent']),
        ('weichang', ['Wei Chang'])],
}
INDEX = 'The-Scene-Characters.html'
BOUND = r'(?<![\w@.!])(%s)(?![\w@])'

def handle_re(season):
    alts = sorted(((h, a) for a, hs in HANDLES[season] for h in hs), key=lambda x: -len(x[0]))
    return re.compile(BOUND % '|'.join(re.escape(h) for h, _ in alts)), dict(alts)

SKIP = {'a', 'blockquote', 'h1', 'h2', 'h3', 'table', 'nav', 'figcaption'}

def link_handles(body, season):
    """Link the first mention of each character in every h2/h3 section of
    prose. Chat logs, tables, headings and existing links are left alone."""
    rx, lookup = handle_re(season)
    out, stack, seen = [], [], set()
    for part in re.split(r'(<[^>]+>)', body):
        tag = re.match(r'<(/?)([a-z0-9]+)', part)
        if tag:
            closing, name = tag.group(1), tag.group(2)
            if name in ('h2', 'h3') and not closing:
                seen = set()
            if name in SKIP:
                if closing:
                    if name in stack:
                        stack.remove(name)
                else:
                    stack.append(name)
            out.append(part)
            continue
        if stack or not part:
            out.append(part)
            continue
        def sub(m):
            anchor = lookup[m.group(1)]
            if anchor in seen:
                return m.group(0)
            seen.add(anchor)
            return '<a class="h" href="%s#s%d-%s">%s</a>' % (INDEX, season, anchor, m.group(1))
        out.append(rx.sub(sub, part))
    return ''.join(out)

def anchor_rows(body):
    """On the index itself, give each character's first row its anchor."""
    done = set()
    def row(m):
        tr = m.group(0)
        first = re.search(r'<td>(.*?)</td>', tr, flags=re.S)
        if not first:
            return tr
        cell = html.unescape(re.sub(r'<[^>]+>', '', first.group(1)))
        for season in (1, 2):
            for anchor, hs in HANDLES[season]:
                key = 's%d-%s' % (season, anchor)
                if key not in done and re.search(BOUND % '|'.join(map(re.escape, hs)), cell):
                    done.add(key)
                    return tr.replace('<tr>', '<tr id="%s">' % key, 1)
        return tr
    return re.sub(r'<tr>.*?</tr>', row, body, flags=re.S)

if SEASON:
    body = link_handles(body, SEASON)
elif NAME == INDEX:
    body = anchor_rows(body)

# --- image + following italic paragraph -> figure -------------------------
body = re.sub(
    r'<p><img([^>]*?)/?></p>\s*<p><em>(.*?)</em></p>',
    lambda m: '<figure><img%s><figcaption>%s</figcaption></figure>' % (m.group(1), m.group(2)),
    body, flags=re.S)

# --- heading ids + table of contents --------------------------------------
def slug(t):
    t = re.sub(r'<[^>]+>', '', t)
    t = html.unescape(t)
    t = re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')
    return t

toc = []
def addid(m):
    lvl, attrs, text = m.group(1), m.group(2), m.group(3)
    s = slug(text)
    toc.append((int(lvl), s, text))
    return '<h%s id="%s"%s>%s</h%s>' % (lvl, s, attrs, text, lvl)

body = re.sub(r'<h([23])(.*?)>(.*?)</h\1>', addid, body, flags=re.S)

eps, back = [], []
for lvl, s, text in toc:
    plain = re.sub(r'<[^>]+>', '', text)
    if lvl == 2 and plain.startswith('Episode'):
        eps.append((s, plain))
    elif lvl == 2 or lvl == 3:
        back.append((s, plain))

def li(items):
    return '\n'.join('<li><a href="#%s">%s</a></li>' % (s, t) for s, t in items)

nav = ('<nav id="toc" aria-label="Contents">\n<h2 class="toch">Contents</h2>\n'
       '<ol class="eps">\n%s\n</ol>\n<ul class="back">\n%s\n</ul>\n</nav>'
       % (li(eps), li(back)))

# drop the leading <h1> out of the flow so we can rebuild the header
m = re.search(r'<h1>(.*?)</h1>', body, flags=re.S)
title = re.sub(r'<[^>]+>', '', m.group(1)) if m else 'The Scene'
body = body.replace(m.group(0), '', 1) if m else body

# --- description and link previews: the page's own opening paragraph ------
first = re.search(r'<p>(.*?)</p>', body, flags=re.S)
desc = html.unescape(re.sub(r'<[^>]+>', '', first.group(1))) if first else title
desc = ' '.join(desc.split())
if len(desc) > 200:
    stop = desc[:200].rfind('. ')
    desc = desc[:stop + 1] if stop > 80 else desc[:197].rsplit(' ', 1)[0] + u'\u2026'
image = SITE + (stills[0] if stills else 'stills/s01/e01-luckychi-icq.jpg')
meta = '\n'.join([
    '<meta name="description" content="%s">' % html.escape(desc),
    '<meta property="og:type" content="article">',
    '<meta property="og:url" content="%s">' % (SITE + NAME),
    '<meta property="og:title" content="%s">' % html.escape(title),
    '<meta property="og:description" content="%s">' % html.escape(desc),
    '<meta property="og:image" content="%s">' % image,
    '<meta name="twitter:card" content="summary_large_image">',
])
# the web build links home relatively; the standalone file links to the site
home = 'index.html' if WEB else SITE

CSS = """
:root{
  --bg:#fbfaf7; --fg:#22201d; --muted:#6b6560; --rule:#ddd8d0;
  --accent:#8a4b2a; --quote-bg:#f2efe9; --mono-bg:#eeeae3;
  --max:44rem;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#16181a; --fg:#dcd9d4; --muted:#938f89; --rule:#2e3134;
    --accent:#d99a6c; --quote-bg:#1e2124; --mono-bg:#23262a;
  }
}
:root[data-theme="dark"]{
  --bg:#16181a; --fg:#dcd9d4; --muted:#938f89; --rule:#2e3134;
  --accent:#d99a6c; --quote-bg:#1e2124; --mono-bg:#23262a;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0; background:var(--bg); color:var(--fg);
  font:17px/1.62 Charter,"Bitstream Charter","Iowan Old Style",Georgia,"Times New Roman",serif;
  padding:0 16px;
}
.wrap{max-width:var(--max);margin:0 auto;padding:3.5rem 0 6rem}
header.mast{border-bottom:2px solid var(--fg);padding-bottom:1.1rem;margin-bottom:2rem}
header.mast h1{font-size:2.05rem;line-height:1.15;margin:0 0 .4rem;letter-spacing:-.01em}
header.mast p.kicker{margin:0;color:var(--muted);font-size:.9rem;letter-spacing:.06em;text-transform:uppercase}
h2{font-size:1.32rem;line-height:1.25;margin:3.2rem 0 .9rem;padding-top:.3rem;border-top:1px solid var(--rule)}
h2:first-of-type{border-top:0}
h3{font-size:1.06rem;margin:2.4rem 0 .7rem;letter-spacing:.02em;text-transform:uppercase;color:var(--muted)}
p{margin:0 0 1.05rem}
a{color:var(--accent);text-decoration:none;border-bottom:1px solid rgba(138,75,42,.35)}
a:hover{border-bottom-color:currentColor}
strong{font-weight:600}
em{font-style:italic}
code{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.86em;
  background:var(--mono-bg);padding:.1em .34em;border-radius:3px}
blockquote{
  margin:1.3rem 0;padding:.85rem 1rem;background:var(--quote-bg);
  border-left:3px solid var(--rule);border-radius:2px;
  font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  font-size:.83rem;line-height:1.55;
}
blockquote p{margin:0 0 .5rem}
blockquote p:last-child{margin:0}
blockquote code{background:transparent;padding:0;font-size:1em}
table{width:100%;border-collapse:collapse;margin:1.4rem 0;font-size:.88rem;display:block;overflow-x:auto}
th,td{text-align:left;padding:.42rem .7rem .42rem 0;border-bottom:1px solid var(--rule);vertical-align:top}
th{font-weight:600;color:var(--muted);text-transform:uppercase;font-size:.74rem;letter-spacing:.05em}
ul,ol{padding-left:1.25rem;margin:0 0 1.05rem}
li{margin:0 0 .5rem}
hr{border:0;border-top:1px solid var(--rule);margin:2.5rem 0}
figure{margin:2rem 0}
figure img{width:100%;height:auto;display:block;border:1px solid var(--rule);border-radius:3px}
figcaption{margin-top:.6rem;font-size:.86rem;line-height:1.5;color:var(--muted)}
#toc{margin:0 0 3rem;padding:1.2rem 1.3rem;background:var(--quote-bg);border-radius:4px}
#toc .toch{font-size:.74rem;text-transform:uppercase;letter-spacing:.09em;color:var(--muted);
  margin:0 0 .8rem;border:0;padding:0}
#toc ol,#toc ul{margin:0;padding:0;list-style:none;font-size:.88rem}
#toc ol.eps{columns:2;column-gap:1.6rem}
#toc li{margin:0 0 .3rem;break-inside:avoid}
#toc ul.back{margin-top:.9rem;padding-top:.8rem;border-top:1px solid var(--rule);
  columns:2;column-gap:1.6rem}
#toc a{border:0;color:var(--fg)}
#toc a:hover{color:var(--accent)}
a.h{color:inherit;border-bottom:1px dotted var(--muted)}
a.h:hover{color:var(--accent);border-bottom-color:currentColor}
header.mast p.kicker a.home{color:inherit;border:0}
header.mast p.kicker a.home:hover{color:var(--accent)}
tr:target td{background:var(--quote-bg)}
footer.colophon{margin-top:4rem;padding-top:1.2rem;border-top:1px solid var(--rule);
  font-size:.82rem;color:var(--muted)}
@media (max-width:600px){
  body{font-size:16px}
  .wrap{padding:2.2rem 0 4rem}
  header.mast h1{font-size:1.6rem}
  #toc ol.eps,#toc ul.back{columns:1}
  blockquote{font-size:.78rem;padding:.7rem .8rem}
}
@media print{
  body{background:#fff;color:#000}
  #toc{display:none}
  h2{break-after:avoid}
  figure{break-inside:avoid}
}
"""

doc = u"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
%s
<style>%s</style>
</head>
<body>
<div class="wrap">
<header class="mast">
<p class="kicker"><a class="home" href="%s">The Scene</a> &middot; Reconstruction</p>
<h1>%s</h1>
</header>
%s
%s
<footer class="colophon">
<p>Original writing here is licensed <a href="https://creativecommons.org/licenses/by/4.0/">CC&nbsp;BY&nbsp;4.0</a>.
<em>The Scene</em> (2004&ndash;2006) is a work of Jun Group Entertainment, released under
<a href="https://creativecommons.org/licenses/by-nd/2.0/">CC&nbsp;BY-ND&nbsp;2.0</a>; the quoted dialogue and the
frames reproduced above remain theirs.</p>
</footer>
</div>
</body>
</html>
""" % (html.escape(title), meta, CSS, home, html.escape(title), nav, body)

io.open(OUT, 'w', encoding='utf-8', newline='\n').write(doc)
print('wrote', OUT, os.path.getsize(OUT), 'bytes;', len(eps), 'episodes,', len(back), 'back sections')
