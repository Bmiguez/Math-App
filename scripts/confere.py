"""Recontagem independente (pandas, a partir de base_final.json) x valores das fórmulas recalculadas no LibreOffice.
Uso: python scripts/confere.py <xlsx_recalculado>
Sai com código 1 se houver qualquer divergência ou erro de fórmula."""
import sys, json, pathlib
import pandas as pd
from openpyxl import load_workbook

RAIZ = pathlib.Path(__file__).resolve().parent.parent
T = RAIZ / 'saida' / 'trabalho'
CA, DE = 'Caffeine Army (SuperCoffee)', 'Desincoffee (Super Nutrition/Desinchá)'
F = json.load(open(T / 'base_final.json'))
C = json.load(open(T / 'codigos.json'))
CODES = C['MOT'] + C['BAR'] + C['NEU']
df = pd.DataFrame(F)
for c in CODES:
    df[c] = df['codigos'].apply(lambda x, c=c: int(c in x))
df['Algum motivo'] = (df[C['MOT']].sum(axis=1) > 0).astype(int)
df['Alguma barreira'] = (df[C['BAR']].sum(axis=1) > 0).astype(int)
df['Pico'] = ((df['Fonte'].str.startswith('Site Caffeine')) & (df['Data'].str[:7].isin(['2025-11', '2025-12']))).astype(int)
v = df[df['Incluir'] == 1]
GR = [v[v.Marca == CA], v[(v.Marca == CA) & (v.Mercado == 'BR')], v[(v.Marca == CA) & (v.Mercado == 'EUA')],
      v[(v.Marca == CA) & (v.Site_marca == 1)], v[(v.Marca == CA) & (v.Site_marca == 1) & (v.Pico == 0)],
      v[(v.Marca == CA) & (v.Site_marca == 0)], v[(v.Marca == CA) & (v.Site_marca == 0) & (v.Incentivada == 0)],
      v[v.Marca == DE], v[(v.Marca == DE) & (v.Site_marca == 1)], v[(v.Marca == DE) & (v.Site_marca == 1) & (v.Incentivo == 'Não informado')],
      v[(v.Marca == DE) & (v.Site_marca == 0)]]

wb = load_workbook(sys.argv[1], data_only=True)
erros = []
for ws in wb:
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value, str) and c.value.startswith('#') and c.value.rstrip('!?/0').upper() in ('#REF', '#VALUE', '#NAME', '#DIV', '#N/A', '#NUM', '#NULL', '#ERR'):
                erros.append((ws.title, c.coordinate, c.value))
            if isinstance(c.value, str) and (c.value.startswith('Err:') or c.value in ('#REF!', '#VALUE!', '#NAME?', '#DIV/0!', '#N/A', '#NUM!')):
                erros.append((ws.title, c.coordinate, c.value))
ws = wb['Resultados']
linhas = CODES + ['Algum motivo', 'Alguma barreira']
div = []
for k, g in enumerate(GR):
    nc, pc = 4 + 2 * k, 5 + 2 * k
    if ws.cell(row=5, column=nc).value != len(g):
        div.append(('BASE', k, ws.cell(row=5, column=nc).value, len(g)))
    for i, c in enumerate(linhas, 6):
        n = int(g[c].sum()); p = n / len(g) if len(g) else 0
        if ws.cell(row=i, column=nc).value != n or abs((ws.cell(row=i, column=pc).value or 0) - p) > 1e-9:
            div.append((c, k, ws.cell(row=i, column=nc).value, n))
# Base: Algum motivo / Alguma barreira por linha
wb_ = wb['Base_reviews']
hdr = [c.value for c in wb_[1]]
ia, ib = hdr.index('Algum motivo'), hdr.index('Alguma barreira')
for r_xl, (_, r_pd) in zip(wb_.iter_rows(min_row=2, values_only=True), df.iterrows()):
    assert r_xl[0] == r_pd['ID']
    if r_xl[ia] != r_pd['Algum motivo'] or r_xl[ib] != r_pd['Alguma barreira']:
        div.append(('linha', r_pd['ID']))
print('células com erro de fórmula:', len(erros), erros[:5])
print('divergências pandas x planilha:', len(div), div[:10])
print('n por grupo:', [len(g) for g in GR])
sys.exit(1 if erros or div else 0)
