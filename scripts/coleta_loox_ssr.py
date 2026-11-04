"""Coleta reviews Loox renderizadas no HTML (SSR) das páginas de produto Shopify.
Respeita robots.txt (loox.io/widget é Disallow; só lemos as páginas de produto da loja).
Uso: python coleta_loox_ssr.py <dominio> <arquivo_handles> <pasta_saida>
"""
import sys, json, re, time, datetime, html, pathlib, urllib.request
dom, handles_file, out = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3])
(out / 'html').mkdir(parents=True, exist_ok=True)
UA = 'Mozilla/5.0 (X11; Linux x86_64) research-review-study/1.0'
ts = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
art = re.compile(r'<article\s+class="loox-review"(.*?)</article>', re.S)
def g(p, s):
    m = re.search(p, s, re.S); return html.unescape(m.group(1).strip()) if m else None
recs, resumo = [], []
for h in [l.strip() for l in open(handles_file) if l.strip()]:
    url = f'https://{dom}/products/{h}'
    try:
        body = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=30).read().decode('utf-8', 'replace')
    except Exception as e:
        resumo.append({'handle': h, 'url': url, 'erro': str(e)}); time.sleep(1.5); continue
    (out / 'html' / f'{h}_{ts}.html').write_text(body)
    tot = re.search(r'Overall rating: ([\d.]+) / 5 from (\d+) reviews', body)
    n = 0
    for a in art.finditer(body):
        b = a.group(1); n += 1
        recs.append({'review_id': g(r'data-review-id="([^"]+)"', b), 'product_id_pagina': g(r'data-product-id="([^"]+)"', b),
            'pagina_handle': h, 'texto': g(r'<p class="loox-review-body">(.*?)</p>', b), 'autor': g(r'loox-reviewer-name">(.*?)<', b),
            'nota': g(r'loox-review-rating">(\d)/5', b), 'verificada': 'loox-review-verified' in b,
            'data': g(r'datetime="([^"]+)"', b), 'produto_review': g(r'loox-review-product-link"[^>]*>(.*?)</a>', b),
            'produto_review_link': g(r'loox-review-product-link" href="([^"]+)"', b), 'tem_foto': 'loox-review-image' in b,
            'url': url, 'coletado_em': ts})
    resumo.append({'handle': h, 'url': url, 'nota_media': tot and tot.group(1), 'total_anunciado': tot and int(tot.group(2)), 'reviews_na_pagina': n})
    time.sleep(1.5)
json.dump(recs, open(out / f'reviews_{ts}.json', 'w'), ensure_ascii=False, indent=1)
json.dump(resumo, open(out / f'paginas_{ts}.json', 'w'), ensure_ascii=False, indent=1)
print(len(recs), 'reviews;', len({r["review_id"] for r in recs}), 'únicas;', len(resumo), 'páginas')
