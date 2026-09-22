import re,sys
path=sys.argv[1]
seen={}
out=[]
cur="0:00"
for line in open(path,encoding='utf-8',errors='replace'):
    line=line.rstrip()
    if line.startswith('### t='):
        cur=line[6:]; continue
    s=line.strip()
    if len(s)<6: continue
    key=re.sub(r'[^a-z0-9]','',s.lower())
    if len(key)<8: continue
    key=key[:45]
    if key in seen: continue
    seen[key]=1
    out.append(f"[{cur}] {s}")
print("\n".join(out))
