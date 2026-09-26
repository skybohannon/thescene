"""Recover the third category: application furniture that carries data.

The chat pass reads conversations and the prose pass reads documents. Both throw
away window titles, address bars, header fields, status lines and file paths as
"chrome" -- and in this series a good deal of the plot lives exactly there. The
FTP client in episode 4 has the server address, the account and the remote
directory in its toolbar; episode 11's Gmail tab names the subject line; the
local path in both says whose machine it is.

So: keep a line only when it looks like furniture AND carries a value -- a host,
a path, an address, a port, a subject, a date, a count. Chrome without a value
(toolbars, menu bars, button rows) is still dropped.

    python3 chrome.py <raw_ocr.txt> > <chrome.txt>
"""
import re, sys

FIELD = re.compile(
    r'\b(address|user|password|port|host|server|status|response|subject|date|sent|'
    r'from|to|local site|remote site|filename|filesize|command|connected|'
    r'directory|login|logoff|account|topic|users?)\b\s*[:=]', re.I)
VALUE = re.compile(
    r'(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'            # an IP
    r'|[A-Za-z]:\\[\w\s.\\-]{4,}'                          # a windows path
    r'|/home/[\w./-]{3,}|/[\w.-]+/[\w./-]{3,}'             # a unix path
    r'|\b[\w.-]+@[\w.-]+\.[a-z]{2,}\b'                     # an address
    r'|\bport\s*[:=]?\s*\d{1,5}\b'
    r'|\b(?:ftp|http|https|irc)://[\w./:-]{4,}'
    r'|\b[\w-]{3,}\.(?:com|net|org|edu|gov)\b'             # a domain
    r'|#[A-Za-z][\w-]{2,}'                                 # an IRC channel
    r'|\b\d{1,3}:\d{2}(?::\d{2})?\s*(?:am|pm)?\b'          # a clock time
    r'|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2},?\s*\d{4}\b)', re.I)
# window titles: "Something - Application" or a bracketed mIRC title
TITLE = re.compile(r'(mIRC\s*-\s*\[|Mozilla Firefox|Internet Explorer|Yahoo!\s*Mail|Gmail\s*-|'
                   r'-\s*Message Session|Instant Message|Windows Explorer|FileZilla|FlashFXP|WinSCP)', re.I)
JUNKY = re.compile(r'^[^A-Za-z]*$')

seen, out = set(), []
t = None
for line in open(sys.argv[1], encoding='utf-8', errors='replace'):
    s = ' '.join(line.split())
    m = re.match(r'### t=(\d+):(\d+)', s)
    if m:
        t = int(m.group(1)) * 60 + int(m.group(2))
        continue
    if t is None or len(s) < 10 or JUNKY.match(s):
        continue
    if not (VALUE.search(s) or (FIELD.search(s) and re.search(r'[:=]\s*\S', s)) or TITLE.search(s)):
        continue
    letters = sum(c.isalpha() for c in s)
    if letters / len(s) < 0.45:
        continue
    key = re.sub(r'[^a-z0-9]', '', s.lower())[:26]
    if len(key) < 10 or key in seen:
        continue
    seen.add(key)
    out.append('[%d:%02d] %s' % (t // 60, t % 60, s))
print('\n'.join(out))
