# -*- coding: utf-8 -*-
"""Check every link in a built site.

    python3 scripts/checklinks.py <site-dir> [--external]

Internal links -- other pages, frames, and #anchors within them -- must
resolve inside <site-dir>. With --external, every outside URL is also
requested once, headers only, following redirects. Any 2xx is fine -- IMDb
answers scripts with a 202 challenge page. A 404 or an unreachable host is an
error; a 403 or 429 is only reported, because some sites refuse scripted
requests to pages that are perfectly fine.

Links that start with /thescene/ -- the site's path on GitHub Pages, which
the 404 page uses because it can be served at any depth -- are resolved from
<site-dir>.

Exits 1 if anything is broken.
"""
import os, re, sys, time
from html.parser import HTMLParser
from urllib.parse import urljoin, urldefrag, urlparse, unquote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE = '/thescene/'


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids = [], set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            self.ids.add(a['id'])
        if tag == 'a' and a.get('name'):
            self.ids.add(a['name'])
        for key in ('href', 'src'):
            if a.get(key) and not (tag == 'meta'):
                self.links.append(a[key])
        if tag == 'meta' and (a.get('property') or '').startswith('og:') and \
                (a.get('content') or '').startswith('http') and a.get('property') in ('og:image', 'og:url'):
            self.links.append(a['content'])


def parse(path):
    p = Page()
    with open(path, encoding='utf-8') as f:
        p.feed(f.read())
    return p


def head(url, tries=3):
    """HTTP status for a URL, asking for headers only."""
    for attempt in range(tries):
        try:
            req = Request(url, method='HEAD', headers={'User-Agent': 'thescene-linkcheck/1.0'})
            with urlopen(req, timeout=30) as r:
                return r.status
        except HTTPError as e:
            if e.code in (500, 502, 503, 504) and attempt + 1 < tries:
                time.sleep(5)
                continue
            return e.code
        except (URLError, OSError) as e:
            if attempt + 1 < tries:
                time.sleep(5)
                continue
            return str(getattr(e, 'reason', e))


def main():
    args = sys.argv[1:]
    external = '--external' in args
    args = [a for a in args if a != '--external']
    if len(args) != 1:
        sys.exit(__doc__)
    root = os.path.abspath(args[0])

    pages = {}
    for d, _, files in os.walk(root):
        for f in files:
            if f.endswith('.html'):
                path = os.path.join(d, f)
                pages[path] = parse(path)

    errors, warnings, outside = [], [], {}
    for path, page in sorted(pages.items()):
        rel = os.path.relpath(path, root).replace(os.sep, '/')
        for link in page.links:
            if link.startswith(('data:', 'mailto:', 'javascript:')):
                continue
            if urlparse(link).scheme in ('http', 'https'):
                outside.setdefault(urldefrag(link)[0], set()).add(rel)
                continue
            target, frag = urldefrag(link)
            if target.startswith(BASE):
                target_path = os.path.join(root, unquote(target[len(BASE):]))
            elif target.startswith('/'):
                errors.append('%s: %s -- outside the site' % (rel, link))
                continue
            else:
                target_path = os.path.normpath(os.path.join(os.path.dirname(path), unquote(target))) if target else path
            if os.path.isdir(target_path):
                target_path = os.path.join(target_path, 'index.html')
            if not os.path.exists(target_path):
                errors.append('%s: %s -- no such file' % (rel, link))
            elif frag and target_path.endswith('.html'):
                ids = pages[target_path].ids if target_path in pages else parse(target_path).ids
                if frag not in ids:
                    errors.append('%s: %s -- no element with id "%s"' % (rel, link, frag))

    if external:
        for url in sorted(outside):
            status = head(url)
            where = ', '.join(sorted(outside[url]))
            if isinstance(status, int) and 200 <= status < 300:
                continue
            line = '%s: %s -- %s' % (where, url, status)
            (warnings if status in (401, 403, 405, 429, 999) else errors).append(line)

    for w in warnings:
        print('warning:', w)
    for e in errors:
        print('error:', e)
    print('%d page(s), %d link(s)%s: %d error(s), %d warning(s)' % (
        len(pages), sum(len(p.links) for p in pages.values()),
        ', %d outside URL(s)' % len(outside) if external else '', len(errors), len(warnings)))
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
