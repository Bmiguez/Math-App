"""Gera lotes para codificação: python scripts/lotes.py <prefixo CA|DE> <tamanho>"""
import json, sys, pathlib
R = pathlib.Path(__file__).resolve().parent.parent / 'saida' / 'trabalho'
L = json.load(open(R / 'base_consolidada.json'))
pre, n = sys.argv[1], int(sys.argv[2])
cod = {}
for f in (R / 'codificacao').glob('*.json'):
    for x in json.load(open(f)): cod[x['id']] = x
alvo = [l for l in L if l['ID'].startswith(pre) and not l['Duplicata_de'] and l['Produto_elegivel']
        and l['Texto_bruto'] and l['ID'] not in cod]
(R / 'lotes').mkdir(exist_ok=True)
for i in range(0, len(alvo), n):
    with open(R / 'lotes' / f'{pre}_{i // n + 1:03d}.txt', 'w') as fh:
        for l in alvo[i:i + n]:
            fh.write(f"{l['ID']} [{l['Nota']}★ {l['Produto'][:40]}] {l['Texto_bruto'].replace(chr(10), ' ')}\n")
print(len(alvo), 'a codificar;', (len(alvo) + n - 1) // n, 'lotes')
