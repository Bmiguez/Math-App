"""Coleta reviews de varejistas VTEX acessíveis (robots.txt permite; sem login/token) para as 6 marcas da v3.
Widgets: Konfidency (API pública reviews-api.konfidency.com.br) e Yourviews (GraphQL público da loja VTEX, query persistida productReviews).
Uso: python coleta_varejo.py <pasta_bruto>
"""
import sys, json, time, base64, datetime, pathlib, urllib.request, urllib.parse, re

OUT = pathlib.Path(sys.argv[1]) / 'varejo'; OUT.mkdir(parents=True, exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) research-review-study/1.0'}
TS = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
LOJAS = {  # domínio: (widget, cliente konfidency)
    'www.drogariasaopaulo.com.br': ('konfidency', 'drogariasaopaulo'),
    'www.drogariaspacheco.com.br': ('konfidency', 'drogariaspacheco'),
    'www.americanas.com.br': ('konfidency', 'americanas'),
    'www.paguemenos.com.br': ('yourviews', None),
    'www.drogal.com.br': ('yourviews', None),
}
TERMOS = ['supercoffee', 'super coffee', 'caffeine army', 'desincoffee', 'supercafe', 'brainstorm coffee', 'essential nutrition brainstorm',
          'v-coffee', 'v coffee vitafor', 'ultracoffee', 'ultra coffee', 'mega coffee', 'allure mega coffee']
YV_HASH = '2436be17d0eee9022cd34fa89872a21b024ac0f25ffd1e4423fba8f6cf267c4c'


def marca(p):
    t = (p.get('brand', '') + ' ' + p.get('productName', '')).lower()
    if 'caffeine army' in t or 'supercoffee' in t.replace(' ', ''): return 'Caffeine Army'
    if 'desinc' in t or ('supercaf' in t and ('super nutrition' in t or 'desinch' in t)): return 'Desincoffee'
    if 'brainstorm' in t and 'coffee' in t: return 'Brainstorm Coffee'
    if 'v-coffee' in t or 'v coffee' in t or ('vitafor' in t and 'coffee' in t): return 'V-Coffee'
    if 'ultracoffee' in t.replace(' ', '') or 'ultra coffee' in t: return 'Ultracoffee'
    if 'mega coffee' in t and 'allure' in t: return 'Mega Coffee'
    return None


def get(u, js=True):
    time.sleep(1.2)
    r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read().decode('utf-8', 'replace')
    return json.loads(r) if js else r


def yourviews(dom, pid):
    var = {'productId': str(pid), 'page': 1, 'count': 50, 'orderBy': 0}
    ext = {'persistedQuery': {'version': 1, 'sha256Hash': YV_HASH, 'sender': 'yourviews.yourviewsreviews@1.x', 'provider': 'yourviews.yourviewsreviews@1.x'},
           'variables': base64.b64encode(json.dumps(var).encode()).decode()}
    u = (f'https://{dom}/_v/segment/graphql/v1?workspace=master&maxAge=short&appsEtag=remove&domain=store&locale=pt-BR'
         f'&operationName=productReviews&variables=%7B%7D&extensions=' + urllib.parse.quote(json.dumps(ext)))
    return (get(u).get('data') or {}).get('productReviews') or {}


reviews, produtos = [], []
for dom, (widget, cli) in LOJAS.items():
    vistos = {}
    for t in TERMOS:
        for frm in (0, 50):
            try: ps = get(f'https://{dom}/api/catalog_system/pub/products/search?ft={urllib.parse.quote(t)}&_from={frm}&_to={frm + 49}')
            except Exception as e: print(dom, t, 'erro', e); break
            for p in ps:
                m = marca(p)
                if m: vistos[p['productId']] = (p, m)
            if len(ps) < 50: break
    print(dom, len(vistos), 'produtos das marcas', flush=True)
    for pid, (p, m) in vistos.items():
        reg = {'loja': dom, 'widget': widget, 'marca': m, 'productId': pid, 'produto': p['productName'], 'brand': p.get('brand'), 'url': p.get('link'), 'n': 0}
        try:
            if widget == 'konfidency':
                d = get(f'https://reviews-api.konfidency.com.br/{cli}/{pid}/summary/created,-1?pageSize=100&page=1')
                r0 = (d.get('reviews') or [{}])[0]
                reg['agregado'] = {k: r0.get(k) for k in ('reviewCount', 'aggregateRating', 'textReviews')}
                for v in r0.get('reviews', []) or []:
                    v.update({'_loja': dom, '_marca': m, '_produto': p['productName'], '_url': p.get('link'), '_coletado_em': TS}); reviews.append(v); reg['n'] += 1
            else:
                ids = [pid] + [it['itemId'] for it in p.get('items', [])]
                vistos_rev = set()
                for i in ids:
                    d = yourviews(dom, i)
                    for v in ((d.get('Element') or {}).get('Reviews') or []) if isinstance(d.get('Element'), dict) else (d.get('Element') or []):
                        k = v.get('ReviewId') or json.dumps(v, sort_keys=True)[:200]
                        if k in vistos_rev: continue
                        vistos_rev.add(k)
                        u_ = v.get('User') or {}
                        for campo in ('Email', 'IPAddress', 'UserId', 'YourviewsUserId', 'ZipCode'):
                            u_.pop(campo, None)  # minimização: não guardar e-mail/IP/ID do autor
                        v.update({'_loja': dom, '_marca': m, '_produto': p['productName'], '_url': p.get('link'), '_id_consultado': i, '_coletado_em': TS})
                        reviews.append(v); reg['n'] += 1
                    reg.setdefault('total_por_id', {})[i] = d.get('Total')
        except Exception as e:
            reg['erro'] = str(e)
        produtos.append(reg)
    print(dom, 'reviews acumuladas', len(reviews), flush=True)
json.dump(reviews, open(OUT / f'reviews_{TS}.json', 'w'), ensure_ascii=False, indent=1)
json.dump(produtos, open(OUT / f'produtos_{TS}.json', 'w'), ensure_ascii=False, indent=1)
print('FIM', len(reviews))
