"""Gera saida/reviews_cafe_funcional_v3.xlsx a partir de saida/trabalho/base_final.json.
Resultados e comparações são fórmulas (COUNTIFS) sobre a aba Base_reviews.
Uso: python scripts/monta_planilha.py <arquivo_saida.xlsx>
"""
import json, glob, sys, pathlib, collections, re
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter as L

RAIZ = pathlib.Path(__file__).resolve().parent.parent
T = RAIZ / 'saida' / 'trabalho'
B = RAIZ / 'saida' / 'bruto'
OUT = sys.argv[1] if len(sys.argv) > 1 else str(RAIZ / 'saida' / 'reviews_cafe_funcional_v3.xlsx')
CA, DE = 'Caffeine Army (SuperCoffee)', 'Desincoffee (Super Nutrition/Desinchá)'
BS, UC = 'Brainstorm Coffee (Essential Nutrition)', 'Ultracoffee (3corações / Plant Power)'
VC, MC = 'V-Coffee Energy Boost (Vitafor)', 'Mega Coffee (Allure)'
F = json.load(open(T / 'base_final.json'))
C = json.load(open(T / 'codigos.json'))
MOT, BAR, NEU = C['MOT'], C['BAR'], C['NEU']
CODES = MOT + BAR + NEU
V1 = json.load(open(T / 'v1_percentuais.json'))
VAL = json.load(open(T / 'validacao' / 'resultado_validacao.json'))

H = Font(bold=True, color='FFFFFF'); HF = PatternFill('solid', fgColor='3B3B3B')
B1 = Font(bold=True); TIT = Font(bold=True, size=13)
WRAP = Alignment(wrap_text=True, vertical='top')


def cab(ws, row, vals):
    for j, v in enumerate(vals, 1):
        c = ws.cell(row=row, column=j, value=v); c.font = H; c.fill = HF; c.alignment = Alignment(wrap_text=True, vertical='center')


TEMA = {
    'ENE': ('Energia / disposição / eficácia percebida', 'Inclui "cumpre o que promete", "dá gás". "Sem energia" não conta.'),
    'SAB': ('Sabor (elogio)', 'Elogio ao sabor, aroma ou a um sabor específico.'),
    'HAB': ('Hábito, fidelidade ou recompra (inclui intenção de recomprar)', '"Não vivo sem", "tomo todo dia", "já comprei de novo", "vou comprar mais".'),
    'FOC': ('Foco / concentração / produtividade', 'Trabalho, estudo, "dia rende".'),
    'TRE': ('Uso em treino ou esporte', 'Pré-treino, corrida, bike, academia, prova.'),
    'SEF': ('Sem efeito colateral (sem tremedeira, ansiedade, queda, azia, taquicardia, insônia)', 'Inclui "energia sem pico", "não acelera o coração", "não tira o sono".'),
    'TEX': ('Textura / cremosidade', 'Elogio a cremosidade, consistência, espuma.'),
    'PRA': ('Praticidade / preparo fácil / mistura bem', 'Sachê para levar, preparo rápido, versatilidade de preparo, receitas, dissolve fácil.'),
    'SAU': ('Saudável (ingredientes, sem açúcar, colágeno, jejum)', 'Funcional, sem açúcar, não quebra jejum, aliado da dieta, proteína.'),
    'SUB': ('Substitui o café comum / atrai quem não tolera café', 'Trocou o café, não gosta de café, café comum faz mal.'),
    'COR': ('Efeito corporal (termogênico, saciedade, diurético)', 'Inclui "mata a vontade de doce", saciedade, "faz suar".'),
    'CB': ('Custo-benefício / promoção', 'Promoção, "vale a pena", "vale cada centavo", mais barato que cafeteria.'),
    'ENT': ('Entrega ou atendimento elogiado', 'Chegou rápido, bem embalado.'),
    'IND': ('Conheceu por indicação de amigos', 'Só quando a própria pessoa conheceu por indicação (indicar a outros não conta).'),
    'GER': ('Elogio genérico, sem motivo específico de produto', 'Só quando não há nenhum motivo específico ("amei", "muito bom").'),
    'nPRE': ('Preço alto (conta mesmo em "caro, mas vale"; inclui a gíria "salgado")', ''),
    'nSAB': ('Sabor ruim, artificial, adoçante, doce demais ou fraco', 'Inclui "não gostei" em página de sabor e "sem gosto".'),
    'nEFE': ('Efeito fraco ou curto', ''),
    'nENT': ('Não recebeu ou atraso', ''),
    'nPED': ('Pedido errado (sabor trocado, brinde faltando, embalagem divergente)', 'Inclui reembolso/reposição sem retorno após devolução.'),
    'nREN': ('Rende pouco', ''),
    'nTEX': ('Dissolve mal', 'Na v2 também capta queixa de textura ruim (crosta, ralo).'),
    'nOUT': ('Outro pedido (ex.: versão descafeinada)', 'Sem lactose, com proteína, descafeinado, amostras, sabor fora da assinatura.'),
    'nDIS': ('NOVO v2 – Sabor indisponível, esgotado ou descontinuado', 'Pedidos de volta de sabor (Beijinho, Chocolate, Pistache, Paçoca, Evolution), "sempre esgotado", "não tirem de linha".'),
    'nATE': ('NOVO v2 – Atendimento/suporte ruim', 'Sem resposta no WhatsApp/e-mail, demora do suporte. (ENT cobre o elogio; faltava o código de barreira.)'),
    'nING': ('NOVO v2 – Critica ingrediente da fórmula', 'Ex.: excesso de bicarbonato. Frequência muito baixa (1 caso).'),
    'CON': ('Menciona concorrente; anotar qual em Obs', 'Inclui "outras marcas" não nomeadas.'),
    'ASS': ('NOVO v2 – Menciona a assinatura Prime (neutro)', 'Assinante, sabor exclusivo do Prime, "virei Prime". Quando é queixa da exclusividade, vem junto com nDIS ou nOUT.'),
}
TIPO = {c: 'Motivo' for c in MOT} | {c: 'Barreira' for c in BAR} | {c: 'Neutro' for c in NEU}

wb = Workbook()

# ---------------- Base_reviews ----------------
ws = wb.active; ws.title = 'Base_reviews'
cols = ['ID', 'ID_origem', 'Marca', 'Fonte', 'Mercado', 'Tipo de fonte', 'Produto', 'Nota (1-5)', 'Data', 'Compra verificada',
        'Incentivo', 'Incentivada (1/0)', 'Site da marca (1/0)', 'Pico nov–dez/2025 site CA (1/0)', 'Origem do dado', 'Resumo',
        'Incluir', 'Obs', 'Link'] + CODES + ['Algum motivo', 'Alguma barreira']
cab(ws, 1, cols)
ci = {c: i + 1 for i, c in enumerate(cols)}
m0, m1 = L(ci[MOT[0]]), L(ci[MOT[-1]]); b0, b1 = L(ci[BAR[0]]), L(ci[BAR[-1]])
for i, r in enumerate(F, 2):
    pico = 1 if (r['Fonte'].startswith('Site Caffeine') and r['Data'][:7] in ('2025-11', '2025-12')) else 0
    r['Pico'] = pico
    vals = [r['ID'], r['ID_origem'], r['Marca'], r['Fonte'], r['Mercado'], r['Tipo_fonte'], r['Produto'], r['Nota'], r['Data'],
            r['Compra_verificada'], r['Incentivo'], r['Incentivada'], r['Site_marca'], pico, r['Origem_dado'], r['Resumo'],
            r['Incluir'], r['Obs'], r['Link']] + [1 if c in r['codigos'] else 0 for c in CODES]
    for j, v in enumerate(vals, 1):
        ws.cell(row=i, column=j, value=v)
    ws.cell(row=i, column=ci['Algum motivo'], value=f'=IF(SUM({m0}{i}:{m1}{i})>0,1,0)')
    ws.cell(row=i, column=ci['Alguma barreira'], value=f'=IF(SUM({b0}{i}:{b1}{i})>0,1,0)')
NB = len(F) + 1
ws.freeze_panes = 'B2'; ws.auto_filter.ref = f'A1:{L(len(cols))}{NB}'
for c, w in {'A': 10, 'B': 18, 'C': 22, 'D': 22, 'G': 30, 'K': 18, 'O': 22, 'P': 40, 'R': 40, 'S': 30}.items():
    ws.column_dimensions[c].width = w
for c in CODES + ['Algum motivo', 'Alguma barreira']:
    ws.column_dimensions[L(ci[c])].width = 6

# ---------------- Textos ----------------
wt = wb.create_sheet('Textos')
cab(wt, 1, ['ID', 'Texto original (nomes e endereço de autor removidos)'])
k = 2
for r in F:
    if r['Texto']:
        wt.cell(row=k, column=1, value=r['ID']); wt.cell(row=k, column=2, value=r['Texto']); k += 1
wt.column_dimensions['A'].width = 10; wt.column_dimensions['B'].width = 140; wt.freeze_panes = 'A2'

# ---------------- Resultados ----------------
wr = wb.create_sheet('Resultados', 0)
rng = lambda c: f"Base_reviews!${L(ci[c])}$2:${L(ci[c])}${NB}"
GR = [
    ('CA – total', [('Marca', CA)]),
    ('CA – Brasil', [('Marca', CA), ('Mercado', 'BR')]),
    ('CA – EUA', [('Marca', CA), ('Mercado', 'EUA')]),
    ('CA – site da marca', [('Marca', CA), ('Site da marca (1/0)', 1)]),
    ('CA – site, sem o pico nov–dez/2025', [('Marca', CA), ('Site da marca (1/0)', 1), ('Pico nov–dez/2025 site CA (1/0)', 0)]),
    ('CA – fora do site da marca', [('Marca', CA), ('Site da marca (1/0)', 0)]),
    ('CA – fora do site, sem incentivadas', [('Marca', CA), ('Site da marca (1/0)', 0), ('Incentivada (1/0)', 0)]),
    ('DE – total', [('Marca', DE)]),
    ('DE – site da marca', [('Marca', DE), ('Site da marca (1/0)', 1)]),
    ('DE – site, sem reviews com foto', [('Marca', DE), ('Site da marca (1/0)', 1), ('Incentivo', 'Não informado')]),
    ('DE – fora do site da marca', [('Marca', DE), ('Site da marca (1/0)', 0)]),
    ('BS – total', [('Marca', BS)]),
    ('BS – site da marca', [('Marca', BS), ('Site da marca (1/0)', 1)]),
    ('BS – fora do site da marca', [('Marca', BS), ('Site da marca (1/0)', 0)]),
    ('UC – total', [('Marca', UC)]),
    ('UC – site da marca', [('Marca', UC), ('Site da marca (1/0)', 1)]),
    ('UC – fora do site da marca', [('Marca', UC), ('Site da marca (1/0)', 0)]),
    ('VC – total', [('Marca', VC)]),
    ('MC – total', [('Marca', MC)]),
]


def crit(lst):
    parts = [f'{rng("Incluir")},1']
    for col, v in lst:
        parts.append(f'{rng(col)},' + (f'"{v}"' if isinstance(v, str) else str(v)))
    return ','.join(parts)


wr['A1'] = 'Quanto cada tema aparece nas avaliações – v2'; wr['A1'].font = TIT
wr['A2'] = ('% = avaliações que citam o tema ÷ avaliações válidas do grupo (Incluir = 1). Multirresposta: não soma 100%. '
            'Tudo calculado por fórmula sobre Base_reviews. CA = Caffeine Army (SuperCoffee); DE = Desincoffee; BS = Brainstorm Coffee; UC = Ultracoffee; VC = V-Coffee; MC = Mega Coffee.')
hdr = ['Código', 'Tema', 'Tipo']
for g, _ in GR:
    hdr += [f'{g} (n)', f'{g} (%)']
cab(wr, 4, hdr)
wr.cell(row=5, column=1, value='BASE'); wr.cell(row=5, column=2, value='Avaliações válidas (n)')
for k, (g, cr) in enumerate(GR):
    wr.cell(row=5, column=4 + 2 * k, value=f'=COUNTIFS({crit(cr)})')
linhas = CODES + ['Algum motivo', 'Alguma barreira']
ROWRES = {}
for i, c in enumerate(linhas, 6):
    ROWRES[c] = i
    wr.cell(row=i, column=1, value=c if c in CODES else '—')
    wr.cell(row=i, column=2, value=TEMA[c][0] if c in TEMA else c)
    wr.cell(row=i, column=3, value=TIPO.get(c, 'Resumo'))
    for k, (g, cr) in enumerate(GR):
        nc, pc = 4 + 2 * k, 5 + 2 * k
        wr.cell(row=i, column=nc, value=f'=COUNTIFS({crit(cr)},{rng(c)},1)')
        wr.cell(row=i, column=pc, value=f'=IFERROR({L(nc)}{i}/{L(nc)}$5,0)').number_format = '0.0%'
me = len(linhas) + 6
wr.cell(row=me, column=2, value='Margem de erro (95%, p = 50%), em pontos percentuais').font = B1
for k in range(len(GR)):
    nc = 4 + 2 * k
    wr.cell(row=me, column=5 + 2 * k, value=f'=IF({L(nc)}$5>0,1.96*SQRT(0.25/{L(nc)}$5),"")').number_format = '0.0%'
wr.cell(row=me + 2, column=1, value='Como ler').font = B1
notas = [
    'O total da Caffeine Army é 95% site da marca, e 91% dessas reviews foram publicadas em nov–dez/2025 (pico concentrado, típico de campanha de avaliação). Compare a coluna "fora do site da marca" com cautela: n pequeno.',
    'O Desincoffee só tem reviews com texto acessíveis no site da própria marca (Loox). Fora do site, n = 4 (herdadas da v1, Mercado Livre): não dá para responder com dados se "o Desincoffee só parece melhor por vir do próprio site".',
    'No Loox, reviews com foto podem ter ganhado cupom; a coluna "sem reviews com foto" serve de controle.',
    'Grupos com n < 30 têm margem de erro acima de ±18 p.p.; trate como indicação, não como medida.',
    'BS e UC: n de 25 e 27. VC e MC: sem nenhuma review válida nas fontes acessíveis (colunas zeradas de propósito, para registrar a lacuna).',
]
for j, t in enumerate(notas):
    wr.cell(row=me + 3 + j, column=1, value=f'{j + 1}. {t}')
wr.column_dimensions['B'].width = 46; wr.freeze_panes = 'D5'
for k in range(len(GR)):
    wr.column_dimensions[L(4 + 2 * k)].width = 10; wr.column_dimensions[L(5 + 2 * k)].width = 10

# ---------------- Comparacao_v1 ----------------
wc = wb.create_sheet('Comparacao_v1', 1)
wc['A1'] = 'O que mudou em relação à v1 (diferenças acima de 10 p.p. destacadas)'; wc['A1'].font = TIT
wc['A2'] = 'v1 = valores da planilha v1 (n = 66 CA; 192 DE). v2 = fórmulas ligadas à aba Resultados (total de cada marca).'
cab(wc, 4, ['Código', 'Tema', 'CA v1 %', 'CA v2 %', 'CA dif. (p.p.)', 'CA > 10 p.p.?', 'DE v1 %', 'DE v2 %', 'DE dif. (p.p.)', 'DE > 10 p.p.?', 'Explicação'])
EXPL_CA = ('Mudança de fonte, não de opinião: a v1 da CA era Thingtesting (EUA) + Magalu; a v2 é 95% site da marca, '
           'com reviews de "ranking de sabores" publicadas em massa em nov–dez/2025. Fora do site (n = 86 na v3) os % ficam próximos da v1.')
EXPL = {'ENE': EXPL_CA, 'SAB': EXPL_CA, 'HAB': EXPL_CA, 'TRE': EXPL_CA, 'SEF': EXPL_CA, 'SAU': EXPL_CA, 'SUB': EXPL_CA,
        'PRA': EXPL_CA + ' PRA também sobe porque as páginas dos sachês To Go puxam o tema "levar na bolsa/viagem".',
        'TEX': EXPL_CA, 'nPRE': EXPL_CA + ' Preço quase não aparece no site da marca.'}
colv2 = {'CA': 5, 'DE': 4 + 2 * 7 + 1}  # coluna % do grupo CA total e DE total
for i, c in enumerate(CODES, 5):
    wc.cell(row=i, column=1, value=c); wc.cell(row=i, column=2, value=TEMA[c][0])
    for off, key, m in ((0, 'Caffei', 'CA'), (4, 'Desinc', 'DE')):
        v1 = V1[key].get(c)
        wc.cell(row=i, column=3 + off, value=(v1 / 100) if v1 is not None else 'n/d (código novo)')
        wc.cell(row=i, column=4 + off, value=f"=Resultados!{L(colv2[m])}{ROWRES[c]}")
        if v1 is not None:
            wc.cell(row=i, column=5 + off, value=f'=({L(4 + off)}{i}-{L(3 + off)}{i})*100')
            wc.cell(row=i, column=6 + off, value=f'=IF(ABS({L(5 + off)}{i})>10,"SIM","não")')
        for cc in (3 + off, 4 + off):
            wc.cell(row=i, column=cc).number_format = '0.0%'
        wc.cell(row=i, column=5 + off).number_format = '0.0'
    wc.cell(row=i, column=11, value=EXPL.get(c, ''))
wc.column_dimensions['B'].width = 50; wc.column_dimensions['K'].width = 90

# ---------------- Livro_de_codigos ----------------
wl = wb.create_sheet('Livro_de_codigos')
cab(wl, 1, ['Código', 'Tema', 'Tipo', 'Regra de codificação usada na v2'])
for i, c in enumerate(CODES, 2):
    wl.cell(row=i, column=1, value=c); wl.cell(row=i, column=2, value=TEMA[c][0]); wl.cell(row=i, column=3, value=TIPO[c])
    wl.cell(row=i, column=4, value=TEMA[c][1])
r0 = len(CODES) + 3
regras = ['Regras gerais',
          '1. Multirresposta. Barreira conta mesmo com elogio geral ("caro, mas vale" = nPRE + CB).',
          '2. Não codificar por palavra-chave: "sem energia" não vira ENE; "indiquei para amigos" não vira IND.',
          '3. Incluir = 0: texto vazio ou só pontuação; duplicata; outro produto; marca ambígua; quem ainda não provou.',
          '4. Kits do Desinchá com Caramelo de Creatina/Melatonina/chá (Kit Core, Prime, Full): só entra se o texto citar café/supercafé; senão Incluir = 0 (produto ambíguo).',
          '5. Supercoffee virou nome genérico: no site do Desinchá, se a review indica outra marca (ex.: "tomo supercoffee há 2 anos e moro nos EUA"), Incluir = 0.',
          '6. Linhas de outros produtos da Caffeine Army (Koala, Morning Shot, Whey, Creatina) ficam na base com Incluir = 0. SuperCoffee Protein+ entra (é linha SuperCoffee), anotado em Obs.',
          '7. Códigos novos (nDIS, nATE, nING, ASS) foram criados por frequência ou por lacuna do livro; nenhum código antigo mudou de significado.']
for j, t in enumerate(regras):
    wl.cell(row=r0 + j, column=1, value=t).font = B1 if j == 0 else Font()
wl.column_dimensions['B'].width = 60; wl.column_dimensions['D'].width = 100

# ---------------- Cobertura ----------------
wv = wb.create_sheet('Cobertura')
lp = json.load(open(sorted(glob.glob(str(B / 'desincha_loox' / 'paginas_*.json')))[-1]))
avulsos = [p for p in lp if p.get('total_anunciado') and not re.search(r'compre|kit|combo|creatina|chai', p['handle'])]
anun_loox = sum(p['total_anunciado'] for p in avulsos)
v = lambda fonte, marca=None: sum(1 for r in F if r['Fonte'] == fonte and r['Incluir'] and (marca is None or r['Marca'] == marca))
n = lambda fonte, cond=lambda r: True: sum(1 for r in F if r['Fonte'] == fonte and cond(r))
jp = json.load(open(sorted(glob.glob(str(B / 'caffeinearmy_site' / 'paginas_*.json')))[-1]))
anun_jdgm = sum(p.get('total_anunciado', 0) for p in jp)
sc = lambda r: 'supercoffee' in (r['Produto'] or '').lower().replace(' ', '')
cab(wv, 1, ['Fonte', 'Marca', 'Volume anunciado no site', 'Coletado (linhas brutas)', 'Coletado único (pós-deduplicação)', 'Válido (Incluir = 1)',
            '% de cobertura (único ÷ anunciado)', 'Data da coleta', 'Método', 'Bloqueios, amostragem e observações'])
D = '04/11/2026'
loox_unicas = n('Site Desinchá (Loox)', lambda r: not r['Obs'].startswith('duplicata'))
loox_cafe = n('Site Desinchá (Loox)', lambda r: not r['Obs'].startswith('duplicata') and 'não é supercafé' not in r['Obs'])
vp = json.load(open(sorted(glob.glob(str(B / 'varejo' / 'produtos_*.json')))[-1]))
LOJA = {'www.drogariasaopaulo.com.br': 'Drogaria São Paulo', 'www.drogariaspacheco.com.br': 'Drogarias Pacheco',
        'www.americanas.com.br': 'Americanas', 'www.paguemenos.com.br': 'Pague Menos', 'www.drogal.com.br': 'Drogal'}
LINHAS_VAREJO = []
for dom, nome in LOJA.items():
    ps = [x for x in vp if x['loja'] == dom]
    marcas_loja = sorted({x['marca'] for x in ps})
    anun = sum(((x.get('agregado') or {}).get('reviewCount') or 0) if x['widget'] == 'konfidency' else max([t or 0 for t in (x.get('total_por_id') or {}).values()] or [0]) for x in ps)
    col = n(nome); val = v(nome)
    LINHAS_VAREJO.append([f'{nome} ({ps[0]["widget"].capitalize() if ps else "—"})', ' + '.join(marcas_loja) or '—', anun, col, col, val, (col / anun) if anun else '—', D,
                          f'Busca no catálogo VTEX ({len(ps)} produtos das 6 marcas) + widget de reviews público',
                          'Drogaria SP coletada também na v2 (mesmas reviews, não duplicadas). ' + ('Sem reviews com texto para V-Coffee e Mega Coffee.' if ps else '')])
COB = [
    ['Site Desinchá (Loox) – inclui Super Nutrition', 'DE', anun_loox, n('Site Desinchá (Loox)'), loox_cafe, v('Site Desinchá (Loox)'), loox_cafe / anun_loox, D,
     'HTML das 59 páginas de produto de supercafé (40 reviews mais recentes por página)',
     f'robots.txt de loox.io proíbe /widget: endpoint paginado NÃO usado. Anunciado = soma das {len(avulsos)} páginas de sabor avulso (bundles repetem as mesmas reviews). '
     f'{n("Site Desinchá (Loox)") - loox_unicas} cópias removidas. Amostra NÃO aleatória: só as mais recentes (concentradas em jul–out/2026). Kits com creatina/chá: muitas excluídas por produto ambíguo. supernutrition.com.br redireciona para desincha.com.br.'],
    ['Site Caffeine Army (Judge.me)', 'CA', anun_jdgm, n('Site Caffeine Army (Judge.me)'), n('Site Caffeine Army (Judge.me)', lambda r: not r['Obs'].startswith('duplicata')),
     v('Site Caffeine Army (Judge.me)'), n('Site Caffeine Army (Judge.me)', lambda r: not r['Obs'].startswith('duplicata')) / anun_jdgm, D,
     '127 páginas de produto + paginação pública api.judge.me/reviews/reviews_for_widget (não bloqueada no robots.txt)',
     f'Cobertura praticamente total do site. Das {n("Site Caffeine Army (Judge.me)", sc)} reviews de SuperCoffee, {v("Site Caffeine Army (Judge.me)")} válidas; as demais são Koala, Morning Shot, Whey e Creatina (Incluir = 0). 91% das válidas foram publicadas em nov–dez/2025.'],
    *LINHAS_VAREJO,
    ['Thingtesting (EUA)', 'CA', 32, n('Thingtesting'), n('Thingtesting'), v('Thingtesting'), 1.0, D, 'HTML (2 páginas)', 'Recoletado com texto integral (a v1 tinha só paráfrase).'],
    ['Home Tester Club', 'CA + UC', '126 (CA) / 69 (UC)', n('Home Tester Club'), n('Home Tester Club'), v('Home Tester Club'), n('Home Tester Club') / 195, D,
     'HTML das páginas (10 reviews renderizadas por produto)', 'API de paginação exige autenticação (401): não contornado. Página do Desincoffee desativada no site (sem produto). Nenhuma das 20 marcada como testador.'],
    ['Site Essential Nutrition', 'BS', 22, n('Site Essential Nutrition'), n('Site Essential Nutrition'), v('Site Essential Nutrition'), 1.0, D,
     'JSON-LD (schema.org/Review) das 2 páginas de Brainstorm Coffee', 'Cobertura total do site.'],
    ['Mercafé (loja do Grupo 3corações)', 'UC', 14, n('Mercafé (loja 3corações)'), n('Mercafé (loja 3corações)'), v('Mercafé (loja 3corações)'), 1.0, D,
     'HTML das 12 páginas de Ultracoffee (widget Yourviews renderizado)', 'Cobertura total do site.'],
    ['Site Vitafor', 'VC', 0, 0, 0, 0, '—', D, 'API pública do app VTEX Reviews & Ratings', 'O app está instalado, mas nenhum produto da loja tem review publicada.'],
    ['Site Allure Pharma', 'MC', 'não confirmado', 0, 0, 0, 0, D, '—', 'HTTP 403 (bloqueio anti-robô). Não coletado.'],
    ['Mercado Livre', 'todas', '8.600+ (CA, 03/11); 267+ (DE); demais não contadas', 0, 0, v('Mercado Livre'), 0, D, '—',
     'robots.txt do Mercado Livre bloqueia ClaudeBot/Claude-User em todo o site, e a API exige token (403). Não coletado. 4 linhas de DE herdadas da v1.'],
    ['Magazine Luiza', 'todas', 'não confirmado', 0, 0, v('Magazine Luiza'), 0, D, '—', 'HTTP 403 (bloqueio anti-robô) até no robots.txt. 26 linhas herdadas da v1 (só paráfrase).'],
    ['Amazon Brasil', 'todas', '~907 (CA, via Buscapé)', 0, 0, 0, 0, D, '—', 'robots.txt bloqueia agentes Claude. Não coletado.'],
    ['Buscapé / Zoom (réplica da Amazon)', 'CA', '~907', 0, 0, v('Amazon (via Buscapé)') + v('Amazon (via Zoom)'), 0, D, '—', 'robots.txt bloqueia agentes Claude. 3 linhas herdadas da v1.'],
    ['Drogasil / Droga Raia / Panvel / Beleza na Web', 'todas', 'não confirmado', 0, 0, 0, 0, D, '—', 'HTTP 403 (bloqueio anti-robô). Não coletado.'],
    ['Reclame Aqui', 'CA + DE', '2.150 (CA) / 248 (perfil SuperCoffee) / 1.585 (Desinchá)', 0, 0, 0, 0, D, '—',
     'HTTP 403 no site e na API de busca. Contagens da aba Reclame_Aqui são da v1 (03/11), não atualizadas.'],
]
for i, row in enumerate(COB, 2):
    for j, val in enumerate(row, 1):
        c = wv.cell(row=i, column=j, value=val); c.alignment = WRAP
    wv.cell(row=i, column=7).number_format = '0%'
k = len(COB) + 3
dd = json.load(open(T / 'deduplicacao.json'))
wv.cell(row=k, column=1, value='Deduplicação').font = B1
wv.cell(row=k + 1, column=1, value=f"Por ID de origem: {dd.get('ID_origem', 0)}. Por texto + data/hora + nota + autor (cópias do Loox entre produtos): {dd.get('texto+data+nota', 0)}. "
                                   f"Mesmo autor + mesmo texto em outro produto: {dd.get('mesmo autor+texto', 0)}. Mais {sum(1 for r in F if r['Obs'].startswith('duplicata de')) - sum(dd.values())} quase-duplicatas (texto quase idêntico) marcadas na codificação manual.")
wv.cell(row=k + 3, column=1, value='Amostra mínima de 400 por marca').font = B1
wv.cell(row=k + 5, column=1, value=f"BS: {sum(1 for r in F if r['Incluir'] and r['Marca'] == BS)}, UC: {sum(1 for r in F if r['Incluir'] and r['Marca'] == UC)}, VC: 0, MC: 0 válidas. Mínimo NÃO atingido nas 4 marcas novas: as fontes acessíveis não têm esse volume; o grosso das reviews delas está em Mercado Livre e Amazon (bloqueados).")
wv.cell(row=k + 4, column=1, value=f"CA: {sum(1 for r in F if r['Incluir'] and r['Marca'] == CA)} válidas (atingido). DE: {sum(1 for r in F if r['Incluir'] and r['Marca'] == DE)} válidas (atingido, mas não é amostra aleatória estratificada por nota: o Loox só expõe as 40 mais recentes por página sem violar o robots.txt).")
for col, w in {'A': 32, 'B': 9, 'C': 18, 'D': 12, 'E': 14, 'F': 10, 'G': 12, 'H': 11, 'I': 40, 'J': 90}.items():
    wv.column_dimensions[col].width = w

# ---------------- Reclame_Aqui (v1, não atualizado) ----------------
wa = wb.create_sheet('Reclame_Aqui')
wa['A1'] = 'Reclame Aqui – contagens oficiais (base completa da empresa, não amostra)'; wa['A1'].font = TIT
wa['A2'] = 'NÃO ATUALIZADO (v2 e v3): em 04/11/2026 o site e a API de busca do Reclame Aqui responderam HTTP 403. Valores de 03/11/2026 (v1).'
cab(wa, 4, ['Caffeine Army – tipo de problema', 'Reclamações (n)', '% do total de reclamações'])
ra = [('Total de reclamações ativas', 2150), ('Produto não recebido', 618), ('Atraso na entrega', 507), ('Propaganda enganosa', 113),
      ('Não consigo cancelar', 104), ('Qualidade do produto', 93), ('Outro problema', 70)]
for i, (a, b) in enumerate(ra, 5):
    wa.cell(row=i, column=1, value=a); wa.cell(row=i, column=2, value=b)
    if i > 5: wa.cell(row=i, column=3, value=f'=B{i}/$B$5').number_format = '0.0%'
wa['A12'] = 'Entrega (não recebido + atraso)'; wa['B12'] = '=B6+B7'; wa['C12'] = '=B12/$B$5'; wa['C12'].number_format = '0.0%'
wa['A13'] = 'Reclamações sem um desses 6 tipos listados'; wa['B13'] = '=B5-SUM(B6:B11)'; wa['C13'] = '=B13/$B$5'; wa['C13'].number_format = '0.0%'
wa['A15'] = 'Nota média últimos 6 meses (fev–jul/2026): 8,0/10. Tempo médio de resposta: 14 dias e 2 horas.'
wa['A17'] = 'Desinchá (dona do Desincoffee) – resumo'; wa['A17'].font = B1
wa['A18'] = 'Total de reclamações ativas (todas as linhas: chás, supercafés etc.)'; wa['B18'] = 1585
wa['A19'] = 'Nota média últimos 6 meses (fev–jul/2026)'; wa['B19'] = 8.4
wa['A20'] = 'Tempo médio de resposta (dias, aprox.)'; wa['B20'] = 9.4
wa['A22'] = 'Perfil "SuperCoffee" (não oficial): 248 reclamações (03/11/2026), mistura sites falsos com a marca real. Não detalhado.'
wa['A24'] = ('Nas reviews (não no Reclame Aqui), entrega quase não aparece no site da marca: nENT = 0,3% na CA e 1,2% no DE. '
             'O canal de queixa de entrega é o Reclame Aqui, não a página de produto.')
wa.column_dimensions['A'].width = 70

# ---------------- Formulario_CA ----------------
wf = wb.create_sheet('Formulario_CA')
jr = json.load(open(sorted(glob.glob(str(B / 'caffeinearmy_site' / 'reviews_*.json')))[-1]))
ids_validos = {r['ID_origem'] for r in F if r['Incluir'] and r['Fonte'].startswith('Site Caffeine')}
form = [x['formulario'] for x in jr if 'jdgm:' + x['review_id'] in ids_validos and x['formulario']]
wf['A1'] = 'Formulário estruturado do Judge.me (site Caffeine Army) – respostas de quem avaliou SuperCoffee'; wf['A1'].font = TIT
wf['A2'] = f'Base: {len(form)} reviews válidas de SuperCoffee com formulário preenchido. Objetivo é multisseleção (não soma 100%). Valores calculados no script; não é fórmula.'
row = 4
for q in ['Qual é o seu objetivo no consumo deste produto?', 'Qual sua idade?', 'Você recomendaria ele para uma amiga ou amigo?']:
    cab(wf, row, [q, 'n', '%']); row += 1
    cnt = collections.Counter()
    for fm in form:
        if q in fm:
            opts = [o.strip() for o in fm[q].split(', ')] if q.startswith('Qual é') else [fm[q]]
            for o in opts: cnt[o] += 1
    for o, nn in cnt.most_common():
        wf.cell(row=row, column=1, value=o); wf.cell(row=row, column=2, value=nn)
        wf.cell(row=row, column=3, value=nn / len(form)).number_format = '0.0%'; row += 1
    row += 1
wf.column_dimensions['A'].width = 70

# ---------------- Validacao ----------------
wq = wb.create_sheet('Validacao')
wq['A1'] = 'Validação da codificação (amostra recodificada às cegas)'; wq['A1'].font = TIT
wq['A2'] = (f"Amostra aleatória (semente 20261104): {VAL['por_marca']['CA']['n']} CA (10%) + {VAL['por_marca']['DE']['n']} DE (mínimo 100). "
            f"Inclusão concordante em {VAL['inclusao_concorda']} de {VAL['n_amostra']}. Concordância por código calculada sobre as {VAL['n_ambos_incluidos']} incluídas nos dois passes.")
wq['A3'] = ('Limitação: recodificação feita pelo mesmo codificador (teste-reteste), sem acesso à primeira codificação, mas não é um segundo codificador independente. '
            'Nenhum código ficou abaixo de 85%; não houve recodificação.')
cab(wq, 5, ['Código', 'Concordância', 'Kappa de Cohen', 'n (1º passe)', 'n (recodificação)'])
for i, (c, d) in enumerate(VAL['por_codigo'].items(), 6):
    wq.cell(row=i, column=1, value=c); wq.cell(row=i, column=2, value=d['concordancia']).number_format = '0.0%'
    wq.cell(row=i, column=3, value=d['kappa']); wq.cell(row=i, column=4, value=d['n_orig']); wq.cell(row=i, column=5, value=d['n_recod'])

# ---------------- LEIA-ME ----------------
wm = wb.create_sheet('LEIA-ME', 0)
nCA = sum(1 for r in F if r['Incluir'] and r['Marca'] == CA); nDE = sum(1 for r in F if r['Incluir'] and r['Marca'] == DE)
nBS = sum(1 for r in F if r['Incluir'] and r['Marca'] == BS); nUC = sum(1 for r in F if r['Incluir'] and r['Marca'] == UC)
txt = [
    ('Base de reviews codificada: cafés funcionais (6 marcas) – v3', TIT),
    ('Gerado em 04/11/2026. Coleta automatizada de páginas públicas, respeitando robots.txt e limite de 1 requisição a cada 1,2–1,5 s.', None),
    ('', None),
    ('O que tem aqui', B1),
    ('Resultados: % de avaliações por tema, por marca e por segmento (mercado, site da marca, incentivo, pico de campanha). Fórmulas sobre Base_reviews.', None),
    ('Comparacao_v1: diferença de cada tema contra a v1, com destaque acima de 10 p.p. e explicação.', None),
    (f'Base_reviews: {len(F)} linhas (todas as coletadas, inclusive duplicatas e outros produtos, com Incluir = 0 e motivo em Obs). Válidas: CA {nCA}, DE {nDE}, BS {nBS}, UC {nUC}, VC 0, MC 0.', None),
    ('Marcas: CA = SuperCoffee 3.0 (Caffeine Army); DE = Desincoffee (Desinchá); BS = Brainstorm Coffee (Essential Nutrition); UC = Ultracoffee (Grupo 3corações / Plant Power); VC = V-Coffee Energy Boost (Vitafor); MC = Mega Coffee (Allure).', None),
    ('Textos: texto original das reviews de produtos elegíveis, ligado por ID (nomes e um endereço escritos pelos autores foram removidos).', None),
    ('Livro_de_codigos: os 24 códigos da v1 sem mudança de sentido + 4 novos (nDIS, nATE, nING, ASS) e as regras de decisão.', None),
    ('Cobertura: volume anunciado x coletado x válido por fonte, método e bloqueios.', None),
    ('Reclame_Aqui: contagens da v1 (o site bloqueou em 04/11).', None),
    ('Formulario_CA: respostas estruturadas (objetivo, idade, recomendaria) de quem avaliou no site da Caffeine Army.', None),
    ('Validacao: concordância e kappa da recodificação cega de 238 reviews (CA e DE, rodada v2).', None),
    ('O que mudou da v2 para a v3: entraram Brainstorm, Ultracoffee, V-Coffee e Mega Coffee, mais 4 varejistas (Pacheco, Americanas, Pague Menos, Drogal) e o Home Tester do Ultracoffee. Nenhuma linha ou código da v2 foi alterado; IDs preservados.', None),
    ('', None),
    ('Privacidade', B1),
    ('Nenhum nome ou foto de autor na planilha; ID pseudônimo (CA-00001 / DE-00001). Os brutos com nome ficam só em saida/bruto/ (local, fora do Git).', None),
    ('A coluna Resumo é gerada a partir dos códigos atribuídos (lista de temas), não é paráfrase escrita à mão. Nas linhas herdadas da v1, é a paráfrase da v1.', None),
    ('', None),
    ('Limitações (leia antes de citar os números)', B1),
    ('1. V-Coffee e Mega Coffee: ZERO reviews nas fontes acessíveis (site Vitafor sem reviews; site Allure bloqueado; farmácias sem avaliações). Brainstorm (n = 25) e Ultracoffee (n = 27) têm n pequeno: margem de erro de ±20 p.p.; use só a ordem dos temas.', None),
    ('2. Marketplaces (Mercado Livre, Amazon, Magalu) e Reclame Aqui bloquearam agentes automáticos e não entraram, salvo 33 linhas herdadas da v1. CA e DE são medidas quase só pelo próprio site (94% e 98%).', None),
    ('3. Site da Caffeine Army: 91% das reviews válidas foram publicadas em nov–dez/2025, em formato de "ranking de sabores". Isso indica campanha de avaliação solicitada; o resultado puxa SAB para cima e ENE, preço e barreiras para baixo. Use a coluna "sem o pico" e a coluna "fora do site" como controle.', None),
    ('4. Desincoffee: só as 40 reviews mais recentes de cada página (jul–out/2026, majoritariamente). Não é amostra aleatória, e não há controle "fora do site" com n útil (n = 4).', None),
    ('5. Notas: 94% das válidas da CA e 83% das do DE são 5 estrelas. Barreiras ficam sub-representadas nas duas; no site da CA fora do pico de nov–dez/2025, 28% citam alguma barreira (contra 4% no total).', None),
    ('6. Codificação feita por um codificador, com recodificação cega de 10% de CA e DE (concordância ≥ 95,7% em todos os códigos; PRA é o mais instável, kappa 0,89). As 68 reviews novas da v3 não passaram por recodificação cega.', None),
    ('7. Margem de erro (95%): ±2,6 p.p. no total CA, ±4,8 p.p. no total DE, ±10,6 p.p. na CA fora do site, ±17 p.p. na CA EUA, ±20 p.p. em BS e UC.', None),
]
for i, (t, f) in enumerate(txt, 1):
    c = wm.cell(row=i, column=1, value=t)
    if f: c.font = f
    c.alignment = Alignment(wrap_text=True, vertical='top')
wm.column_dimensions['A'].width = 150

wb.save(OUT)
print('salvo', OUT)
