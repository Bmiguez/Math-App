"""Monta a base final (uma linha por avaliação) a partir de:
- saida/trabalho/base_consolidada.json (coleta v2, deduplicada)
- saida/trabalho/codificacao/*.json (codificação em lotes)
- entrada/reviews_cafe_funcional_v1.xlsx (linhas herdadas de fontes que bloquearam na v2)
Saída: saida/trabalho/base_final.json
"""
import json, glob, pathlib, re
import openpyxl

RAIZ = pathlib.Path(__file__).resolve().parent.parent
T = RAIZ / 'saida' / 'trabalho'
CA, DE = 'Caffeine Army (SuperCoffee)', 'Desincoffee (Super Nutrition/Desinchá)'

MOT = ['ENE', 'SAB', 'HAB', 'FOC', 'TRE', 'SEF', 'TEX', 'PRA', 'SAU', 'SUB', 'COR', 'CB', 'ENT', 'IND', 'GER']
BAR = ['nPRE', 'nSAB', 'nEFE', 'nENT', 'nPED', 'nREN', 'nTEX', 'nOUT', 'nDIS', 'nATE', 'nING']
NEU = ['CON', 'ASS']
CODES = MOT + BAR + NEU
ROTULO = {'ENE': 'energia', 'SAB': 'sabor', 'HAB': 'hábito/recompra', 'FOC': 'foco', 'TRE': 'treino', 'SEF': 'sem efeito colateral',
          'TEX': 'textura', 'PRA': 'praticidade', 'SAU': 'saudável', 'SUB': 'substitui café', 'COR': 'efeito corporal/saciedade',
          'CB': 'custo-benefício', 'ENT': 'entrega/atendimento ok', 'IND': 'indicação', 'GER': 'elogio genérico',
          'nPRE': 'preço alto', 'nSAB': 'sabor ruim', 'nEFE': 'efeito fraco', 'nENT': 'não recebeu/atraso', 'nPED': 'pedido errado',
          'nREN': 'rende pouco', 'nTEX': 'dissolve mal/textura', 'nOUT': 'pede outra versão', 'nDIS': 'sabor indisponível/descontinuado',
          'nATE': 'atendimento ruim', 'nING': 'critica ingrediente', 'CON': 'cita concorrente', 'ASS': 'cita assinatura Prime'}

# Dados pessoais encontrados nos textos durante a codificação (nomes assinados, endereço). Removidos da planilha.
REDACAO = [
    (r'Rua Rubem Berta.*?apt \d+', '[endereço removido]'),
    (r'Djalma victor', '[nome removido]'), (r'Denyse Bastos', '[nome removido]'), (r'Camila Moll', '[nome removido]'),
    (r'Giane Triches', '[nome removido]'), (r'Att\. Marcio Mendes', '[nome removido]'), (r'^Thamyres', '[nome removido]'),
    (r'Obrigada, Deisy', 'Obrigada, [nome removido]'), (r'^Carla ', '[nome removido] '),
]


def redige(t):
    for p, s in REDACAO:
        t = re.sub(p, s, t, flags=re.S)
    return t


base = json.load(open(T / 'base_consolidada.json'))
cod = {}
for f in glob.glob(str(T / 'codificacao' / '*.json')):
    for x in json.load(open(f)):
        cod[x['id']] = x
id_por_origem = {l['ID_origem']: l['ID'] for l in base}

final = []
for l in base:
    r = {k: l[k] for k in ('ID', 'ID_origem', 'Marca', 'Fonte', 'Mercado', 'Tipo_fonte', 'Produto', 'Nota', 'Data',
                           'Compra_verificada', 'Incentivo', 'Link', 'Coletado_em')}
    r['Origem_dado'] = 'Coleta v2 (texto integral)'
    r['Texto'] = redige(l['Texto_bruto']) if l['Produto_elegivel'] else ''
    r['codigos'] = []
    obs = []
    if l['Duplicata_de']:
        r['Incluir'] = 0; obs.append('duplicata de ' + id_por_origem[l['Duplicata_de']])
    elif not l['Produto_elegivel']:
        r['Incluir'] = 0; obs.append(l['Obs_coleta'] or 'outro produto')
    elif not l['Texto_bruto']:
        r['Incluir'] = 0; obs.append('sem texto (só nota)')
    else:
        c = cod[l['ID']]
        r['Incluir'] = c['inc']; r['codigos'] = c['c'] if c['inc'] else []
        if c['obs']: obs.append(c['obs'])
        if l['Obs_coleta'] and l['Produto_elegivel']: obs.append(l['Obs_coleta'].rstrip('; '))
    r['Obs'] = '; '.join(o for o in obs if o)
    if r['Incluir']:
        temas = ', '.join(ROTULO[c] for c in r['codigos'])
        r['Resumo'] = f'Temas: {temas}' if temas else ''
    else:
        r['Resumo'] = ''
    final.append(r)

# Linhas herdadas da v1 (fontes que a v2 não conseguiu coletar: Magalu, Amazon via agregadores, Mercado Livre)
wb = openpyxl.load_workbook(RAIZ / 'entrada' / 'reviews_cafe_funcional_v1.xlsx')
ws = wb['Base_reviews']
rows = list(ws.iter_rows(values_only=True)); h = list(rows[0])
v1codes = h[13:37]
_f_ids = sorted(T.glob('ids_v*.json'), key=lambda f: int(f.stem.split('_v')[1]))
ids_ant = json.load(open(_f_ids[-1])) if _f_ids else {}
# com dado novo do Mercado Livre, as linhas herdadas da v1 dessa fonte saem (o dado coletado substitui a paráfrase)
ml_novo = any(r['Fonte'] == 'Mercado Livre' for r in final)
prox = {p: max([int(r['ID'][3:]) for r in final if r['ID'].startswith(p)] + [int(v[3:]) for v in ids_ant.values() if v.startswith(p)])
        for p in ('CA', 'DE')}
for row in rows[1:]:
    d = dict(zip(h, row))
    if d['Fonte'] not in ('Magazine Luiza', 'Amazon (via Buscapé)', 'Amazon (via Zoom)', 'Mercado Livre'):
        continue
    if ml_novo and d['Fonte'] == 'Mercado Livre':
        continue
    p = 'CA' if d['Marca'].startswith('Caffeine') else 'DE'
    if 'v1:' + d['ID'] in ids_ant:
        novo_id = ids_ant['v1:' + d['ID']]
    else:
        prox[p] += 1; novo_id = f'{p}-{prox[p]:05d}'
    codes = [c for c in v1codes if str(d[c]) == '1']
    final.append({'ID': novo_id, 'ID_origem': 'v1:' + d['ID'], 'Marca': d['Marca'], 'Fonte': d['Fonte'],
                  'Mercado': d['Mercado'], 'Tipo_fonte': 'Marketplace independente', 'Produto': d['Produto'],
                  'Nota': d['Nota (1-5)'] or None, 'Data': str(d['Data aprox.'] or ''), 'Compra_verificada': 'n/d',
                  'Incentivo': d['Incentivo'], 'Link': d['Link'], 'Coletado_em': '20261103 (v1)',
                  'Origem_dado': 'Herdado da v1 (só paráfrase; fonte bloqueada na v2)', 'Texto': '',
                  'codigos': codes if str(d['Incluir']) == '1' else [], 'Incluir': int(d['Incluir']),
                  'Obs': ('v1: ' + d['Obs']) if d['Obs'] else 'herdado da v1', 'Resumo': d['Resumo (paráfrase)']})

for r in final:
    r['Incentivada'] = 1 if str(r['Incentivo']).startswith('Sim') else 0
    r['Site_marca'] = 1 if r['Tipo_fonte'] == 'Site da marca' else 0
    assert all(c in CODES for c in r['codigos']), (r['ID'], r['codigos'])

final.sort(key=lambda r: r['ID'])
json.dump(final, open(T / 'base_final.json', 'w'), ensure_ascii=False, indent=1)
json.dump({'MOT': MOT, 'BAR': BAR, 'NEU': NEU, 'ROTULO': ROTULO}, open(T / 'codigos.json', 'w'), ensure_ascii=False)
print(len(final), 'linhas;', sum(r['Incluir'] for r in final), 'válidas')
