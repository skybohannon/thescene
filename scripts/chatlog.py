import re,sys
pat=re.compile(r'\[\d{2}:\d{2}\]')
seen=set(); out=[]
for line in open(sys.argv[1],encoding='utf-8',errors='replace'):
    s=line.rstrip()
    m=pat.search(s)
    if not m: continue
    s=s[m.start():].strip()
    s=re.sub(r'\s+[vN|¥ay»]{1,3}$','',s).strip()
    key=re.sub(r'[^a-z0-9]','',s.lower())[:40]
    if len(key)<10 or key in seen: continue
    seen.add(key); out.append(s)
print("\n".join(out))
