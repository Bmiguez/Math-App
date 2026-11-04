"""Compara codificação original x recodificação cega (amostra 10%, mín. 100/marca).
Concordância por código = % de reviews da amostra (incluídas nas duas) em que os dois passes concordam (0/0 ou 1/1).
Também calcula kappa de Cohen por código."""
import json, glob, pathlib, collections
R = pathlib.Path(__file__).resolve().parent.parent / 'saida' / 'trabalho'
orig, rec = {}, {}
for f in glob.glob(str(R / 'codificacao' / '*.json')):
    for x in json.load(open(f)): orig[x['id']] = x
for f in glob.glob(str(R / 'validacao' / 'recod_*.json')):
    for x in json.load(open(f)): rec[x['id']] = x
ids = json.load(open(R / 'validacao' / 'amostra_ids.json'))
assert set(ids) == set(rec), (len(ids), len(rec), set(ids) ^ set(rec))
codes = sorted({c for d in (orig, rec) for x in d.values() for c in x['c']})
out = {'n_amostra': len(ids), 'inclusao_concorda': sum(orig[i]['inc'] == rec[i]['inc'] for i in ids), 'por_marca': {}, 'por_codigo': {}}
both = [i for i in ids if orig[i]['inc'] and rec[i]['inc']]
out['n_ambos_incluidos'] = len(both)
for c in codes:
    a = [int(c in orig[i]['c']) for i in both]; b = [int(c in rec[i]['c']) for i in both]
    n = len(both); agree = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n; pe = pa * pb + (1 - pa) * (1 - pb)
    kappa = (agree - pe) / (1 - pe) if pe < 1 else 1.0
    out['por_codigo'][c] = {'concordancia': round(agree, 4), 'kappa': round(kappa, 3), 'n_orig': sum(a), 'n_recod': sum(b)}
for p in sorted({i[:2] for i in ids}):
    s = [i for i in ids if i.startswith(p)]
    out['por_marca'][p] = {'n': len(s), 'inclusao_concorda': sum(orig[i]['inc'] == rec[i]['inc'] for i in s),
                           'codigos_identicos': sum(set(orig[i]['c']) == set(rec[i]['c']) for i in s if orig[i]['inc'] and rec[i]['inc'])}
out['divergencias'] = [{'id': i, 'orig': sorted(orig[i]['c']), 'recod': sorted(rec[i]['c']), 'inc': (orig[i]['inc'], rec[i]['inc'])}
                       for i in ids if set(orig[i]['c']) != set(rec[i]['c']) or orig[i]['inc'] != rec[i]['inc']]
json.dump(out, open(R / 'validacao' / 'resultado_validacao.json', 'w'), ensure_ascii=False, indent=1)
print('amostra', len(ids), 'inclusão concorda', out['inclusao_concorda'], '| ambos incluídos', len(both))
print(out['por_marca'])
for c, v in out['por_codigo'].items(): print(f"{c:5} conc {v['concordancia']:.3f} kappa {v['kappa']:+.2f}  n {v['n_orig']}/{v['n_recod']}")
print('divergências:', len(out['divergencias']))
for d in out['divergencias']: print(d)
