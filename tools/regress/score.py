import json,sys
from collections import defaultdict
def ed(a,b):
    d=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        p,d[0]=d[0],i
        for j,y in enumerate(b,1): p,d[j]=d[j],min(d[j]+1,d[j-1]+1,p+(x!=y))
    return d[-1]
norm=lambda s:''.join(s.split())
for M in sys.argv[1:]:
    R=json.load(open(f'res_{M}.json')); g=defaultdict(lambda:[0,0,0.0,0])
    for r in R:
        a,b=norm(r['ans']),norm(r['got'])
        for key in (r['mode']+'：'+r['tag'].split('・')[0]+'・'+(r['tag'].split('・')[1] if '・' in r['tag'] else ''), r['mode']+'：全体'):
            x=g[key]; x[0]+=1; x[1]+=a==b; x[2]+=max(0,1-ed(a,b)/max(1,len(a))); x[3]+=r['ms']
    print('====',M)
    for k in sorted(g): n,ok,ca,ms=g[k]; print(f'{k:22s} 完全一致 {ok/n:5.0%}  文字の正しさ {ca/n:5.0%}  平均{ms/n:6.0f}ms  ({n})')
