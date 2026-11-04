"""Coleta opiniões do Mercado Livre (MLB) pela API oficial, para as 6 marcas da v3.

Fluxo:
  1. Descoberta: /products/search (catálogo) para cada termo, com o mesmo filtro de marca de coleta_varejo.py.
     (/sites/MLB/search responde 403 para apps desde 2025; por isso o catálogo.)
  2. Anúncios: /products/{id}/items para cada produto de catálogo (404 "No winners" = produto sem anúncio ativo).
  3. Opiniões: /reviews/item/{item_id}?catalog_product_id={id}, paginado. Exige token de USUÁRIO:
     o token do app (client_credentials) recebe 403 "access denied" (testado em 04/11/2026).

Credenciais só por variável de ambiente: ML_ACCESS_TOKEN (token de usuário, 6 h) ou ML_CLIENT_ID/ML_CLIENT_SECRET.
Privacidade: reviewer_id não é gravado; só um hash curto para deduplicação.
Uso: python coleta_mercadolivre.py <pasta_bruto> [--so-descoberta]
"""
import sys, os, json, time, hashlib, datetime, pathlib, urllib.request, urllib.parse, urllib.error

OUT = pathlib.Path(sys.argv[1]) / 'mercadolivre'; OUT.mkdir(parents=True, exist_ok=True)
SO_DESC = '--so-descoberta' in sys.argv
API = 'https://api.mercadolibre.com'
TS = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
TERMOS = ['supercoffee', 'super coffee', 'caffeine army', 'desincoffee', 'supercafe desincha', 'brainstorm coffee',
          'essential nutrition brainstorm', 'v-coffee', 'v coffee vitafor', 'ultracoffee', 'ultra coffee', 'mega coffee', 'allure mega coffee']
LOG = open(OUT / 'log.txt', 'a')


def log(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); LOG.write(f'{TS} {s}\n')


def marca(nome, brand):
    t = (brand + ' ' + nome).lower()
    if 'caffeine army' in t or 'supercoffee' in t.replace(' ', ''): return 'Caffeine Army'
    if 'desinc' in t or ('supercaf' in t and ('super nutrition' in t or 'desinch' in t)): return 'Desincoffee'
    if 'brainstorm' in t and 'coffee' in t: return 'Brainstorm Coffee'
    if 'v-coffee' in t or 'v coffee' in t or ('vitafor' in t and 'coffee' in t): return 'V-Coffee'
    if 'ultracoffee' in t.replace(' ', '') or 'ultra coffee' in t: return 'Ultracoffee'
    if 'mega coffee' in t and 'allure' in t: return 'Mega Coffee'
    return None


def token():
    if os.environ.get('ML_ACCESS_TOKEN'): return os.environ['ML_ACCESS_TOKEN'], 'usuario'
    body = urllib.parse.urlencode({'grant_type': 'client_credentials', 'client_id': os.environ['ML_CLIENT_ID'],
                                   'client_secret': os.environ['ML_CLIENT_SECRET']}).encode()
    d = json.loads(urllib.request.urlopen(urllib.request.Request(API + '/oauth/token', data=body), timeout=40).read())
    return d['access_token'], 'app'


class SemRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None  # o 301 da API ecoa o token na URL; não seguir


OPENER = urllib.request.build_opener(SemRedirect)
TOK, TIPO_TOK = token()


def get(path, tent=0):
    time.sleep(1.1)  # ≤ 1 req/s
    req = urllib.request.Request(API + path, headers={'Authorization': 'Bearer ' + TOK, 'User-Agent': 'research-review-study/1.0'})
    try:
        return 200, json.loads(OPENER.open(req, timeout=40).read())
    except urllib.error.HTTPError as e:
        try: msg = json.loads(e.read()).get('message', '')
        except Exception: msg = ''
        if e.code == 429 and tent < 4:
            time.sleep(10 * 2 ** tent); return get(path, tent + 1)
        return e.code, {'erro': e.code, 'message': msg}


log('token:', TIPO_TOK)
# 1. descoberta no catálogo
prods = {}
for t in TERMOS:
    for off in range(0, 150, 50):  # offset ≥ 150 é recusado (400)
        c, d = get(f'/products/search?status=active&site_id=MLB&q={urllib.parse.quote(t)}&limit=50&offset={off}')
        if c != 200: log('busca', t, off, c, d.get('message')); break
        res = d.get('results', [])
        for p in res:
            br = next((a.get('value_name') or '' for a in p.get('attributes', []) if a.get('id') == 'BRAND'), '')
            m = marca(p.get('name', ''), br)
            if m and p['id'] not in prods:
                prods[p['id']] = {'catalog_product_id': p['id'], 'parent_id': p.get('parent_id'), 'nome': p.get('name'), 'brand': br, 'marca': m,
                                  'termo': t, 'url': f'https://www.mercadolivre.com.br/p/{p["id"]}'}
        if len(res) < 50: break
log('produtos de catálogo das marcas:', len(prods), {m: sum(p['marca'] == m for p in prods.values()) for m in sorted({p['marca'] for p in prods.values()})})

# 2. anúncios por produto
for pid, p in prods.items():
    c, d = get(f'/products/{pid}/items')
    p['items_status'] = c
    p['items'] = [{'item_id': i['item_id'], 'seller_id': i.get('seller_id')} for i in d.get('results', [])] if c == 200 else []
log('produtos com anúncio ativo:', sum(bool(p['items']) for p in prods.values()))

# 3. opiniões
reviews, vistos = [], set()
if not SO_DESC:
    for pid, p in prods.items():
        p['reviews_status'] = None; p['n'] = 0
        for it in p['items'][:3]:  # opiniões de catálogo são agregadas por produto; 3 anúncios bastam para confirmar
            off = 0
            while True:
                c, d = get(f'/reviews/item/{it["item_id"]}?catalog_product_id={pid}&limit=50&offset={off}')
                p['reviews_status'] = c
                if c != 200:
                    log('reviews', pid, it['item_id'], c, d.get('message'))
                    break
                p['agregado'] = {'rating_average': d.get('rating_average'), 'paging': d.get('paging'), 'rating_levels': d.get('rating_levels')}
                rs = d.get('reviews', [])
                for r in rs:
                    if r['id'] in vistos: continue
                    vistos.add(r['id'])
                    rid = r.pop('reviewer_id', None)
                    for k in ('buying_date', 'relevance', 'forbidden_words'): r.pop(k, None)
                    r.update({'_autor_hash': hashlib.sha1(str(rid).encode()).hexdigest()[:12] if rid else '', '_marca': p['marca'],
                              '_produto': p['nome'], '_catalog_product_id': pid, '_item_id': it['item_id'], '_url': p['url'], '_coletado_em': TS})
                    reviews.append(r); p['n'] += 1
                off += 50
                if len(rs) < 50 or off >= (d.get('paging') or {}).get('total', 0): break
            if p['reviews_status'] in (401, 403): break
        if p['reviews_status'] in (401, 403):
            log('PARADO: endpoint de opiniões recusou o token', TIPO_TOK); break

json.dump(list(prods.values()), open(OUT / f'produtos_{TS}.json', 'w'), ensure_ascii=False, indent=1)
if not SO_DESC: json.dump(reviews, open(OUT / f'reviews_{TS}.json', 'w'), ensure_ascii=False, indent=1)
log('FIM reviews:', len(reviews))
