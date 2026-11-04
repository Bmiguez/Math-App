"""Coleta reviews Judge.me do site da Caffeine Army.
1) lê cada página de produto (contagem e product_id); 2) pagina api.judge.me/reviews/reviews_for_widget
(caminho público, não bloqueado no robots.txt de api.judge.me). 1,5 s entre requisições.
Uso: python coleta_judgeme.py <arquivo_handles> <pasta_saida>"""
import sys, json, re, time, datetime, html, pathlib, urllib.request, urllib.parse
handles, out = sys.argv[1], pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) research-review-study/1.0'}
SHOP = 'caffeinearmy.myshopify.com'
ts = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
def get(u):
    time.sleep(1.5); return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read().decode('utf-8', 'replace')
def g(p, s):
    m = re.search(p, s, re.S); return html.unescape(m.group(1).strip()) if m else None
def parse(h, src):
    rs = []
    for blk in re.split(r"(?=<div class='jdgm-rev jdgm-divider-top')", h)[1:]:
        cf = {html.unescape(a).rstrip(':'): html.unescape(b) for a, b in re.findall(r"cf-ans__title'>(.*?)</b>\s*<span class='jdgm-rev__cf-ans__value'>(.*?)</span>", blk, re.S)}
        body = g(r"<div class='jdgm-rev__body'>(.*?)</div>", blk)
        rs.append({'review_id': g(r"data-review-id='([^']+)'", blk), 'verificada': g(r"data-verified-buyer='([^']+)'", blk),
            'produto': g(r"data-product-title='([^']+)'", blk), 'produto_url': g(r"data-product-url='([^']+)'", blk),
            'nota': g(r"data-score='(\d)'", blk), 'data': g(r"datetime='([^']+)'", blk), 'autor': g(r"jdgm-rev__author'>(.*?)<", blk),
            'titulo': g(r"jdgm-rev__title'>(.*?)</b>", blk), 'texto': re.sub(r'<[^>]+>', ' ', body or '').strip(),
            'formulario': cf, 'transparencia': g(r"data-badge-type=([a-z_]+)", blk), 'origem_pagina': src, 'coletado_em': ts})
    return rs
recs, pags = {}, []
for h in [l.strip() for l in open(handles) if l.strip()]:
    url = f'https://www.caffeinearmy.com.br/products/{h}'
    try: p = get(url)
    except Exception as e: pags.append({'handle': h, 'erro': str(e)}); continue
    pid = g(r"jdgm-widget jdgm-review-widget[^>]*data-id='(\d+)'", p) or g(r"data-id='(\d{10,})'", p)
    n = int(g(r"data-number-of-reviews='(\d+)", p) or 0)
    pags.append({'handle': h, 'url': url, 'product_id': pid, 'total_anunciado': n, 'nota_media': g(r"data-average-rating='([\d.]+)", p)})
    if not n or not pid: continue
    for page in range(1, n // 20 + 2):
        q = urllib.parse.urlencode({'url': SHOP, 'shop_domain': SHOP, 'platform': 'shopify', 'page': page, 'per_page': 20, 'product_id': pid})
        try: js = json.loads(get('https://api.judge.me/reviews/reviews_for_widget?' + q))
        except Exception as e: pags[-1].setdefault('erros', []).append(str(e)); break
        rs = parse(js.get('html', ''), url)
        for r in rs: recs.setdefault(r['review_id'], r)
        if len(rs) < 20: break
    pags[-1]['unicas_acumuladas'] = len(recs)
    print(h, n, len(recs), flush=True)
json.dump(list(recs.values()), open(out / f'reviews_{ts}.json', 'w'), ensure_ascii=False, indent=1)
json.dump(pags, open(out / f'paginas_{ts}.json', 'w'), ensure_ascii=False, indent=1)
print('FIM', len(recs))
