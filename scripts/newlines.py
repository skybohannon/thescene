import re,sys
pat=re.compile(r'(\[\d{2}:\d{2}\]\s*)?<[A-Za-z0-9_\[\]@#$%^&*()+-]{2,14}>')
def load(p):
    out={}
    try: f=open(p,encoding='utf-8',errors='replace')
    except: return out
    for line in f:
        s=line.rstrip(); m=pat.search(s)
        if not m: continue
        s=s[m.start():].strip()
        k=re.sub(r'[^a-z0-9]','',s.lower())[:34]
        if len(k)>=10: out.setdefault(k,s)
    return out
old=load(sys.argv[1]); new=load(sys.argv[2])
for k,v in new.items():
    if k not in old: print(v)
