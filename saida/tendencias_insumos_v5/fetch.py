import json,re,sys,requests,concurrent.futures as cf
from urllib.parse import urlparse
S=sys.argv[1]
rows=json.load(open(f'{S}/rows.json'))
H={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36','Accept-Language':'en-GB,en;q=0.9,de;q=0.8'}
def get(u,t=25):
    try:
        r=requests.get(u,headers=H,timeout=t,allow_redirects=True)
        return r.status_code,r.url,r.text
    except Exception as e: return None,u,str(e)[:200]
def txt(h):
    h=re.sub(r'(?is)<(script|style|noscript).*?</\1>',' ',h); h=re.sub(r'(?s)<[^>]+>',' ',h); return re.sub(r'\s+',' ',h)
def one(d):
    out={'ID':d['ID'],'marca':d['Marca / produto']}
    site=d['_site']
    if not site or site=='N/D': return out
    st,fu,h=get(site); out['home']=[st,fu]
    m=re.search(r'(?is)<title[^>]*>(.*?)</title>',h or ''); out['title']=m.group(1).strip()[:150] if m else None
    out['home_txt']=txt(h)[:6000] if st else h
    p=urlparse(fu); base=f'{p.scheme}://{p.netloc}'
    st2,_,h2=get(base+'/products.json?limit=250')
    if st2==200:
        try:
            js=json.loads(h2); out['shop']=[{'t':x['title'],'avail':any(v.get('available') for v in x['variants']),'upd':x.get('updated_at'),'body':txt(x.get('body_html') or '')[:600]} for x in js['products']]
        except Exception: pass
    for k in ('_fonte','URL verificação'):
        u=d.get(k)
        if u and u.startswith('http'):
            s3,f3,h3=get(u); out[k]=[s3,f3,txt(h3)[:5000] if s3 else h3]
    return out
with cf.ThreadPoolExecutor(16) as ex: res=list(ex.map(one,rows))
json.dump(res,open(f'{S}/web.json','w'),ensure_ascii=False)
for o in res:
    print(o['ID'],o['marca'][:30],'|',o.get('home'),'|',(o.get('title') or '')[:70],'| shop:',len(o.get('shop',[])) if 'shop' in o else '-', '| fonte:',(o.get('_fonte') or [None])[0])
