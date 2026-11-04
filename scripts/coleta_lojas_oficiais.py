"""Coleta reviews das lojas oficiais das marcas da v3 (HTML público, robots.txt verificado):
- Essential Nutrition (Brainstorm Coffee): JSON-LD schema.org/Review embutido na página de produto.
- Mercafé / 3corações (Ultracoffee): reviews Yourviews renderizadas no HTML (Next.js).
- Vitafor (V-Coffee): API pública do app VTEX Reviews & Ratings (retornou 0 reviews em 04/11/2026).
Uso: python coleta_lojas_oficiais.py <pasta_bruto>
"""
import sys, json, re, time, html, datetime, pathlib, urllib.request

OUT = pathlib.Path(sys.argv[1])
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) research-review-study/1.0', 'Accept-Encoding': 'identity'}
TS = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def get(u):
    time.sleep(1.5)
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read().decode('utf-8', 'replace')


def salva(pasta, nome, txt):
    p = OUT / pasta / 'html'; p.mkdir(parents=True, exist_ok=True)
    (p / f'{nome}_{TS}.html').write_text(txt)


# ---------- Essential Nutrition ----------
ess, pag = [], []
for slug in ['brainstorm-coffee-cafe', 'brainstorm-coffee-caramel-latte']:
    u = f'https://www.essentialnutrition.com.br/{slug}'
    h = get(u); salva('essential_site', slug, h)
    for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
        try: d = json.loads(m)
        except Exception: continue
        for x in (d if isinstance(d, list) else [d]):
            if isinstance(x, dict) and 'review' in x:
                pag.append({'url': u, 'produto': x.get('name'), 'agregado': x.get('aggregateRating'), 'n_reviews_pagina': len(x['review'])})
                for r in x['review']:
                    ess.append({'pagina': slug, 'produto': x.get('name'), 'autor': r.get('author', {}).get('name'), 'data': r.get('datePublished'),
                                'titulo': r.get('name'), 'texto': r.get('reviewBody'), 'nota': r.get('reviewRating', {}).get('ratingValue'),
                                'url': u, 'coletado_em': TS})
(OUT / 'essential_site').mkdir(parents=True, exist_ok=True)
json.dump(ess, open(OUT / 'essential_site' / f'reviews_{TS}.json', 'w'), ensure_ascii=False, indent=1)
json.dump(pag, open(OUT / 'essential_site' / f'paginas_{TS}.json', 'w'), ensure_ascii=False, indent=1)
print('Essential', len(ess), pag)

# ---------- Mercafé (Ultracoffee) ----------
prods = json.loads(get('https://mercafe.vtexcommercestable.com.br/api/catalog_system/pub/products/search?ft=ultracoffee&_from=0&_to=49'))
mc, pagm = [], []
FILLED = 'M239.2,97.4A16.4'  # caminho da estrela cheia; a vazia usa outro path
for p in prods:
    u = f"https://www.mercafe.com.br/{p['linkText']}/p"
    try: h = get(u)
    except Exception as e: pagm.append({'url': u, 'erro': str(e)}); continue
    salva('mercafe_ultracoffee', p['linkText'], h)
    agg = None
    for m in re.findall(r'<script[^>]*ld\+json[^>]*>(.*?)</script>', h, re.S):
        try: d = json.loads(m)
        except Exception: continue
        for x in (d if isinstance(d, list) else [d]):
            if isinstance(x, dict) and 'aggregateRating' in x: agg = x['aggregateRating']
    ms = list(re.finditer(r'class="CardReviewWrapper[^"]*"', h))
    vistos = set(); n = 0
    for a, b in zip(ms, ms[1:] + [None]):
        s = h[a.start(): b.start() if b else a.start() + 15000]
        txt = lambda c: (lambda m: html.unescape(m.group(1)).strip() if m else None)(re.search(r'class="' + c + r'-codeby[^"]*"[^>]*>([^<]+)<', s))
        corpo = s[s.find('CardReviewBody'):]
        stars = re.findall(r'<svg[^>]*viewBox="0 0 256 256">.*?<path d="([^"]{0,20})', corpo[:6000], re.S)[:5]
        partes = [html.unescape(t).strip() for t in re.findall(r'>([^<>]+)<', re.sub(r'<svg.*?</svg>', '', corpo, flags=re.S)) if t.strip()]
        titulo, texto = (partes[0] if partes else None), (partes[1] if len(partes) > 1 else None)
        k = (txt('CardReviewPersonName'), txt('CardReviewDate'), texto)
        if k in vistos: continue  # o HTML repete cada review (versão desktop e mobile)
        vistos.add(k); n += 1
        mc.append({'produto': p['productName'], 'productId': p['productId'], 'autor': k[0], 'data': k[1], 'titulo': titulo, 'texto': texto,
                   'nota': sum(1 for d in stars if d.startswith(FILLED)) or None, 'verificada': 'Compra verificada' in s,
                   'recomenda': next((x for x in partes if 'recomendaria' in x or x in ('Sim', 'Não')), None), 'url': u, 'coletado_em': TS})
    pagm.append({'url': u, 'produto': p['productName'], 'agregado': agg, 'n_reviews_pagina': n})
(OUT / 'mercafe_ultracoffee').mkdir(parents=True, exist_ok=True)
json.dump(mc, open(OUT / 'mercafe_ultracoffee' / f'reviews_{TS}.json', 'w'), ensure_ascii=False, indent=1)
json.dump(pagm, open(OUT / 'mercafe_ultracoffee' / f'paginas_{TS}.json', 'w'), ensure_ascii=False, indent=1)
print('Mercafé', len(mc), [(x.get('produto'), x.get('agregado'), x.get('n_reviews_pagina')) for x in pagm])

# ---------- Vitafor (V-Coffee) ----------
vf = []
for pid in ['523']:
    vf.append({'productId': pid, 'rating': json.loads(get(f'https://www.vitafor.com.br/reviews-and-ratings/api/rating/{pid}')),
               'reviews': json.loads(get(f'https://www.vitafor.com.br/reviews-and-ratings/api/reviews?product_id={pid}&from=0&to=50&status=true')), 'coletado_em': TS})
(OUT / 'vitafor_site').mkdir(parents=True, exist_ok=True)
json.dump(vf, open(OUT / 'vitafor_site' / f'reviews_{TS}.json', 'w'), ensure_ascii=False, indent=1)
print('Vitafor', vf)
