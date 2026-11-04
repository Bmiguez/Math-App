"""Consolida os brutos de saida/bruto/<fonte>/ numa base única (sem nome de autor).
Saída: saida/trabalho/base_consolidada.json + relatório de deduplicação.
Uso: python scripts/consolida.py
"""
import json, glob, re, hashlib, pathlib, collections, unicodedata

RAIZ = pathlib.Path(__file__).resolve().parent.parent
B = RAIZ / 'saida' / 'bruto'
OUT = RAIZ / 'saida' / 'trabalho'; OUT.mkdir(parents=True, exist_ok=True)
CA, DE = 'Caffeine Army (SuperCoffee)', 'Desincoffee (Super Nutrition/Desinchá)'


def ultimo(pat):
    fs = sorted(glob.glob(str(B / pat)))
    return fs[-1] if fs else None


def norm(t):
    t = unicodedata.normalize('NFKD', (t or '').lower())
    return re.sub(r'\W+', ' ', ''.join(c for c in t if not unicodedata.combining(c))).strip()


linhas = []


def add(autor=None, data_hora=None, **k):
    k.setdefault('Obs_coleta', '')
    # hash do autor só para deduplicar; o nome não é gravado
    k['_chave_autor'] = hashlib.sha1((autor or '').strip().lower().encode()).hexdigest()[:12] if autor else ''
    k['_data_hora'] = data_hora or k.get('Data', '')
    k['Texto_bruto'] = (k.get('Texto_bruto') or '').strip()
    linhas.append(k)


# 1) Site Desinchá (Loox, HTML renderizado nas páginas de produto)
f = ultimo('desincha_loox/reviews_*.json')
for r in json.load(open(f)):
    prod = r['produto_review'] or ''
    eh_cafe = bool(re.search(r'supercaf', prod, re.I))
    add(ID_origem='loox:' + r['review_id'], Marca=DE, Fonte='Site Desinchá (Loox)', Mercado='BR',
        Tipo_fonte='Site da marca', Produto=prod, Nota=int(r['nota']) if r['nota'] else None,
        Data=(r['data'] or '')[:10], Compra_verificada='Sim' if r['verificada'] else 'Não',
        Incentivo='Desconhecido' if r['tem_foto'] else 'Não informado',
        Texto_bruto=r['texto'], Link='https://www.desincha.com.br' + (r['produto_review_link'] or ''),
        Produto_elegivel=eh_cafe,
        Obs_coleta=('review com foto: Loox costuma dar cupom por foto; ' if r['tem_foto'] else '') +
                   ('' if eh_cafe else 'produto não é supercafé'),
        Coletado_em=r['coletado_em'], autor=r['autor'], data_hora=r['data'])

# 2) Site Caffeine Army (Judge.me)
f = ultimo('caffeinearmy_site/reviews_*.json')
for r in (json.load(open(f)) if f else []):
    prod = r['produto'] or ''
    eh_sc = bool(re.search(r'super ?coffee', prod, re.I))
    inc = {'review_earned_for_future_purchase': 'Sim (desconto em compra futura)'}.get(r.get('transparencia'), 'Não informado')
    txt = ' '.join(x for x in [r.get('titulo'), r.get('texto')] if x)
    add(ID_origem='jdgm:' + r['review_id'], Marca=CA, Fonte='Site Caffeine Army (Judge.me)', Mercado='BR',
        Tipo_fonte='Site da marca', Produto=prod, Nota=int(r['nota']) if r['nota'] else None,
        Data=(r['data'] or '')[:10], Compra_verificada='Sim' if r['verificada'] == 'true' else 'Não',
        Incentivo=inc, Texto_bruto=txt, Link='https://www.caffeinearmy.com.br' + (r['produto_url'] or ''),
        Produto_elegivel=eh_sc, Formulario=r.get('formulario') or {},
        Obs_coleta='' if eh_sc else 'produto não é SuperCoffee (outra linha da marca)', Coletado_em=r['coletado_em'],
        autor=r.get('autor'), data_hora=r.get('data'))

# 3) Drogaria São Paulo (Konfidency)
f = ultimo('drogariasp_konfidency/reviews_*.json')
for r in json.load(open(f)):
    m = CA if r['_marca'] == 'Caffeine Army' else DE
    add(ID_origem='konf:' + r['_id'], Marca=m, Fonte='Drogaria São Paulo', Mercado='BR', Tipo_fonte='Marketplace independente',
        Produto=r['_produto'], Nota=r.get('rating'), Data=(r.get('created') or '')[:10],
        Compra_verificada='Sim' if r.get('verified') else 'Não', Incentivo='Não informado',
        Texto_bruto=r.get('text') or '', Link=r['_url'], Produto_elegivel=True, Coletado_em=r['_coletado_em'],
        autor=r.get('name'), data_hora=r.get('created'))

# 4) Thingtesting
f = ultimo('thingtesting/reviews_*.json')
ts = re.search(r'(\d{8}T\d{6}Z)', f).group(1)
for r in json.load(open(f)):
    c = r['content']
    txt = ' '.join(x for x in [c.get('bodyPositive'), c.get('bodyNegative')] if x)
    inc = 'Sim (produto grátis)' if r['isIncentivized'] else ('Sim (amigo da marca)' if r['userIsContributorForRootBrand'] else 'Não informado')
    add(ID_origem='tt:' + r['review_id'], Marca=CA, Fonte='Thingtesting', Mercado='EUA', Tipo_fonte='Plataforma de reviews',
        Produto='SuperCoffee / Smart Energy Coffee', Nota=c.get('stars'), Data=r['createdAt'][:10], Compra_verificada='n/d',
        Incentivo=inc, Texto_bruto=txt, Link='https://thingtesting.com/brands/caffeine-army/reviews',
        Produto_elegivel=True, Coletado_em=ts)

# 5) Home Tester Club
f = ultimo('hometesterclub/reviews_*.json')
d = json.load(open(f))
for r in d['reviews']:
    add(ID_origem='htc:' + str(r['id']), Marca=CA, Fonte='Home Tester Club', Mercado='BR', Tipo_fonte='Plataforma de teste',
        Produto=r['product']['name'], Nota=r['starRating'], Data=r['dateCreated'][:10], Compra_verificada='n/d',
        Incentivo='Sim (testador)' if r['isHomeTested'] else 'Não informado',
        Texto_bruto=' '.join(x for x in [r.get('reviewTitle'), r.get('reviewText')] if x),
        Link='https://www.hometesterclub.com/br/pt/reviews/' + r['product']['urlName'], Produto_elegivel=True,
        Obs_coleta='' if r['isHomeTested'] else 'plataforma de teste, mas review não marcada como testador',
        Coletado_em=d['coletado_em'])

# Deduplicação: (a) ID_origem; (b) texto normalizado + data + nota (entre fontes)
dup = collections.Counter()
vistos_id, vistos_txt, vistos_aut = {}, {}, {}
for l in linhas:
    l['Duplicata_de'] = ''
    if l['ID_origem'] in vistos_id:
        l['Duplicata_de'] = vistos_id[l['ID_origem']]; dup['ID_origem'] += 1; continue
    vistos_id[l['ID_origem']] = l['ID_origem']
    t = norm(l['Texto_bruto'])
    if t:
        # mesma pessoa, mesmo instante, mesmo texto e nota = cópia (o Loox replica a review em vários produtos)
        k = (l['Marca'], t, l['_data_hora'], l['Nota'], l['_chave_autor'])
        if k in vistos_txt:
            l['Duplicata_de'] = vistos_txt[k]; dup['texto+data+nota'] += 1; continue
        vistos_txt[k] = l['ID_origem']
    # mesma pessoa repetindo o mesmo texto em outro produto/instante (Loox e Judge.me replicam)
    if len(t) >= 20 and l['_chave_autor']:
        k2 = (l['Marca'], t, l['_chave_autor'])
        if k2 in vistos_aut:
            l['Duplicata_de'] = vistos_aut[k2]; dup['mesmo autor+texto'] += 1; continue
        vistos_aut[k2] = l['ID_origem']

# IDs pseudônimos estáveis: ordem por marca, fonte, data, id de origem
cont = collections.Counter()
for l in sorted(linhas, key=lambda x: (x['Marca'] != CA, x['Fonte'], x['Data'], x['ID_origem'])):
    p = 'CA' if l['Marca'] == CA else 'DE'
    cont[p] += 1
    l['ID'] = f'{p}-{cont[p]:05d}'
linhas.sort(key=lambda x: x['ID'])
json.dump(linhas, open(OUT / 'base_consolidada.json', 'w'), ensure_ascii=False, indent=1)
json.dump(dict(dup), open(OUT / 'deduplicacao.json', 'w'))
print(len(linhas), 'linhas;', dict(dup), 'duplicatas;', collections.Counter((l['Marca'][:6], l['Fonte']) for l in linhas))
