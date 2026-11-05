"""v6: hierarquia de cogumelos e de formato no Resumo, editando o XML do arquivo da Janice
(preserva tabela dinâmica, modelo de dados, conexões e suplemento). Uso: build_v6.py <dir_descompactado>"""
import re, sys, os
from xml.sax.saxutils import escape
from lxml import etree
from openpyxl.formula.tokenizer import Tokenizer

D = sys.argv[1]
NS = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
N = '{%s}' % NS
P = "'Tendências por player'"

def rd(p): return open(os.path.join(D, p), encoding='utf8').read()
def wr(p, s): open(os.path.join(D, p), 'w', encoding='utf8').write(s)

# ------------------------------------------------------------------ shared strings
sst = etree.fromstring(rd('xl/sharedStrings.xml').encode())
SS = [''.join(si.itertext()) for si in sst.findall(N + 'si')]

# ------------------------------------------------------------------ estilos
st = rd('xl/styles.xml')
fonts_m = re.search(r'<fonts count="(\d+)"([^>]*)>(.*?)</fonts>', st, re.S)
nf = int(fonts_m.group(1))
base_font = '<sz val="11"/><color theme="1"/><name val="Calibri"/><family val="2"/><charset val="1"/>'
new_fonts = f'<font><b/>{base_font}</font><font><i/>{base_font}</font>'
F_BOLD, F_ITAL = nf, nf + 1
st = st.replace(fonts_m.group(0), f'<fonts count="{nf+2}"{fonts_m.group(2)}>{fonts_m.group(3)}{new_fonts}</fonts>')
xfs_m = re.search(r'<cellXfs count="(\d+)">(.*?)</cellXfs>', st, re.S)
nx = int(xfs_m.group(1))
new_xfs = (f'<xf numFmtId="0" fontId="{F_BOLD}" fillId="0" borderId="12" xfId="0" applyFont="1" applyBorder="1"/>'
           f'<xf numFmtId="0" fontId="0" fillId="0" borderId="12" xfId="0" applyBorder="1" applyAlignment="1"><alignment indent="2"/></xf>'
           f'<xf numFmtId="0" fontId="{F_ITAL}" fillId="0" borderId="12" xfId="0" applyFont="1" applyBorder="1" applyAlignment="1"><alignment indent="2"/></xf>')
X_PARENT, X_CHILD, X_CHILD_IT = nx, nx + 1, nx + 2
st = st.replace(xfs_m.group(0), f'<cellXfs count="{nx+3}">{xfs_m.group(2)}{new_xfs}</cellXfs>')
wr('xl/styles.xml', st)

def istr(ref, text, s=None):
    sa = f' s="{s}"' if s is not None else ''
    return f'<c r="{ref}"{sa} t="inlineStr"><is><t xml:space="preserve">{escape(text)}</t></is></c>'

# ------------------------------------------------------------------ aba de players (sheet4)
LAB_SO, LAB_BL, LAB_SEM = "Só lion's mane", "Lion's mane + outros cogumelos", "Outros cogumelos ou não especificado (sem lion's mane)"
s4 = rd('xl/worksheets/sheet4.xml')
root4 = etree.fromstring(s4.encode())
sd4 = root4.find(N + 'sheetData')

def cell(row, col):
    for c in row.findall(N + 'c'):
        if re.match(col + r'\d+$', c.get('r')): return c
def val(c):
    if c is None: return None
    v = c.find(N + 'v')
    if v is None: return None
    return SS[int(v.text)] if c.get('t') == 's' else v.text

rows4 = sd4.findall(N + 'row')
ys = 59  # estilo amarelo já usado na v5 para células alteradas
bulk_note = ("v6: Bulk Mushroom & Adaptogen Coffee leva lion's mane, cordyceps, reishi, chaga e maitake "
             "(rótulo em bulk.com/uk/products/mushroom-adaptogen-coffee/bpf-mcof).")
expected = {}
for row in rows4:
    r = int(row.get('r'))
    if r == 1:
        for k, (col, lab) in enumerate([('AT', LAB_SO), ('AU', LAB_BL), ('AV', LAB_SEM)]):
            row.append(etree.fromstring(istr(f'{col}1', lab, 51).replace('<c ', f'<c xmlns="{NS}" ', 1)))
        row.set('spans', '1:48')
        continue
    idv = val(cell(row, 'A'))
    if idv == '81':
        for col in ('J', 'K'):
            c = cell(row, col); c.find(N + 'v').text = '1'; c.set('s', str(ys))
        an = cell(row, 'AN'); old = val(an) or ''
        new = etree.fromstring(istr(an.get('r'), (old + ' | ' if old else '') + bulk_note, an.get('s')).replace('<c ', f'<c xmlns="{NS}" ', 1))
        row.replace(an, new)
    I, J, K = (int(val(cell(row, x)) or 0) for x in 'IJK')
    vals = [int(I == 1 and J == 1 and K != 1), int(I == 1 and J == 1 and K == 1), int(I == 1 and J != 1)]
    forms = [f'IF(AND(I{r}=1,J{r}=1,K{r}&lt;&gt;1),1,0)', f'IF(AND(I{r}=1,J{r}=1,K{r}=1),1,0)', f'IF(AND(I{r}=1,J{r}&lt;&gt;1),1,0)']
    for col, f, v in zip(('AT', 'AU', 'AV'), forms, vals):
        row.append(etree.fromstring(f'<c xmlns="{NS}" r="{col}{r}" s="52"><f>{f}</f><v>{v}</v></c>'))
    row.set('spans', '1:48')
    expected[r] = vals
root4.find(N + 'dimension').set('ref', 'A1:AV94')
root4.find(N + 'autoFilter').set('ref', 'A1:AV94')
cols4 = root4.find(N + 'cols')
cols4.append(etree.fromstring(f'<col xmlns="{NS}" min="46" max="48" width="22" customWidth="1"/>'))
wr('xl/worksheets/sheet4.xml', etree.tostring(root4, xml_declaration=True, encoding='UTF-8', standalone=True).decode())

# ------------------------------------------------------------------ Resumo (sheet3): inserir 2 linhas após a 15
INS, K_ = 16, 2
def shift_ref(m):
    col, dol, rown = m.group(1), m.group(2), int(m.group(3))
    return f'{col}{dol}{rown + K_ if rown >= INS else rown}'
REF = re.compile(r'(\$?[A-Z]{1,3})(\$?)(\d+)')
def shift_formula(txt):
    tok = Tokenizer('=' + txt)
    out = []
    for t in tok.items:
        if t.type == 'OPERAND' and t.subtype == 'RANGE' and '!' not in t.value:
            out.append(REF.sub(shift_ref, t.value))
        else:
            out.append(t.value)
    res = ''.join(out)
    return res
def check_roundtrip(txt):
    tok = Tokenizer('=' + txt); return ''.join(t.value for t in tok.items) == txt

s3 = rd('xl/worksheets/sheet3.xml')
root3 = etree.fromstring(s3.encode())
sd3 = root3.find(N + 'sheetData')
bad = 0
for f in root3.iter(N + 'f'):
    if f.text:
        if not check_roundtrip(f.text): bad += 1
        f.text = shift_formula(f.text)
        f.text = f.text.replace(f"{P}!$A$2:$AS$94,0,MATCH", f"{P}!$A$2:$AV$94,0,MATCH").replace(f"{P}!$A$1:$AS$1", f"{P}!$A$1:$AV$1")
    if f.get('ref'):
        f.set('ref', REF.sub(shift_ref, f.get('ref')))
assert bad == 0, f'{bad} fórmulas não fazem round-trip no tokenizer'
for row in sd3.findall(N + 'row'):
    r = int(row.get('r'))
    if r >= INS:
        row.set('r', str(r + K_))
        for c in row.findall(N + 'c'):
            c.set('r', REF.sub(shift_ref, c.get('r')))
root3.find(N + 'dimension').set('ref', 'A1:K94')

# valores esperados (cache) com o filtro atual dela: score >= B4 e contém café = C5
B4 = 3; C5 = 'Sim'
score_col, cafe_col, pais_col = 'AS', 'Z', 'E'
data = []
for row in rows4[1:]:
    r = int(row.get('r'))
    sc = cell(row, score_col); scv = val(sc)
    try: scv = float(scv)
    except Exception: scv = None
    data.append((val(cell(row, pais_col)), scv, int(val(cell(row, cafe_col)) or 0), expected[r], [int(val(cell(row, x)) or 0) for x in 'IJK']))
paises = {'B': 'Reino Unido', 'D': 'Alemanha', 'F': 'EUA', 'H': 'Canadá'}
def passa(d):
    ok_s = d[1] is not None and d[1] >= B4
    ok_c = (C5 == 'Todos') or (d[2] == (1 if C5 == 'Sim' else 0))
    return ok_s and ok_c
def cnt(p, k):
    return sum(1 for d in data if d[0] == p and passa(d) and d[3][k] == 1)
def tot(p): return sum(1 for d in data if d[0] == p and passa(d))
def cog(p): return sum(1 for d in data if d[0] == p and passa(d) and d[4][0] == 1)

def build_row(r, label, k=None, style_label=X_CHILD):
    cells = [istr(f'A{r}', label, style_label)]
    nums = {}
    for col, p in paises.items():
        nxt = chr(ord(col) + 1)
        if k is not None:
            f = (f"COUNTIFS({P}!$E$2:$E$94,{col}$11,INDEX({P}!$A$2:$AV$94,0,MATCH($A{r},{P}!$A$1:$AV$1,0)),1,"
                 f"{P}!$AS$2:$AS$94,\"&gt;=\"&amp;$B$4,{P}!$Z$2:$Z$94,$C$5)")
            v = cnt(p, k); pf = f'IFERROR({col}{r}/{col}$9,0)'; pv = v / tot(p) if tot(p) else 0
        else:
            f = f'{col}14+{col}15'; v = cnt(p, 0) + cnt(p, 1)
            pf = f'IFERROR({col}{r}/{col}13,0)'; pv = v / cog(p) if cog(p) else 0
        nums[col] = v
        cells.append(f'<c r="{col}{r}" s="45"><f>{f}</f><v>{v}</v></c>')
        cells.append(f'<c r="{nxt}{r}" s="46"><f>{pf}</f><v>{pv}</v></c>')
    J = sum(nums.values())
    if k is not None:
        totJ = sum(tot(p) for p in paises.values()); kf = f'IFERROR(J{r}/J$9,0)'; kv = J / totJ if totJ else 0
    else:
        cg = sum(cog(p) for p in paises.values()); kf = f'IFERROR(J{r}/J13,0)'; kv = J / cg if cg else 0
    cells.append(f'<c r="J{r}" s="45"><f>B{r}+D{r}+F{r}+H{r}</f><v>{J}</v></c>')
    cells.append(f'<c r="K{r}" s="46"><f>{kf}</f><v>{kv}</v></c>')
    return etree.fromstring(f'<row xmlns="{NS}" r="{r}" spans="1:11">' + ''.join(cells) + '</row>'), nums, J

rows3 = {int(x.get('r')): x for x in sd3.findall(N + 'row')}
summary = {}
for r, lab, k, sty in [(14, LAB_SO, 0, X_CHILD), (15, LAB_BL, 1, X_CHILD), (16, LAB_SEM, 2, X_CHILD),
                       (17, "Total com lion's mane (% sobre as marcas com cogumelo)", None, X_CHILD_IT)]:
    new, nums, J = build_row(r, lab, k, sty); summary[lab] = (nums, J)
    if r in rows3: sd3.replace(rows3[r], new)
    else:
        prev = rows3.get(r - 1) or [x for x in sd3 if int(x.get('r')) == r - 1][0]
        prev.addnext(new)
    rows3 = {int(x.get('r')): x for x in sd3.findall(N + 'row')}

def set_label_style(r, s, text=None):
    row = rows3[r]; a = row.find(N + 'c')
    assert a.get('r') == f'A{r}'
    if text is None:
        a.set('s', str(s))
    else:
        row.replace(a, etree.fromstring(istr(f'A{r}', text, s).replace('<c ', f'<c xmlns="{NS}" ', 1)))
def label(r):
    a = rows3[r].find(N + 'c'); return val(a) if a.get('t') == 's' else ''.join(a.itertext())
assert label(13) == 'Cogumelos'
set_label_style(13, X_PARENT)
assert label(30) == 'Pó instantâneo' and label(31) == 'Sachê / stick', (label(30), label(31))
set_label_style(30, X_PARENT); set_label_style(31, X_CHILD)
assert label(79).startswith('Ativos confirmados'), label(79)
set_label_style(79, X_PARENT, 'Ativos confirmados (= Ativo + Ativo com ressalva)')
assert label(74) == 'Ativo' and label(75).startswith('Ativo com ressalva')
set_label_style(74, X_CHILD); set_label_style(75, X_CHILD)

# nota explicativa no fim
last = max(rows3)
note = ("• Hierarquia (v6): linhas em negrito são categorias-mãe e as recuadas são subcategorias. "
        "Cogumelos = qualquer cogumelo; as três linhas recuadas logo abaixo são excludentes e somam Cogumelos. "
        "A linha em itálico mostra quantas marcas de cogumelo usam lion's mane. 'Outros cogumelos' (chaga, reishi, cordyceps) "
        "nunca aparece sem lion's mane na base. Sachê / stick é subconjunto de Pó instantâneo. "
        "Ativos confirmados = Ativo + Ativo com ressalva.")
nr = etree.fromstring(f'<row xmlns="{NS}" r="{last+1}" spans="1:1">' + istr(f'A{last+1}', note) + '</row>')
rows3[last].addnext(nr)
root3.find(N + 'dimension').set('ref', f'A1:K{last+1}')
wr('xl/worksheets/sheet3.xml', etree.tostring(root3, xml_declaration=True, encoding='UTF-8', standalone=True).decode())

# ------------------------------------------------------------------ log na aba Revisão v5 (sheet5)
s5 = rd('xl/worksheets/sheet5.xml')
root5 = etree.fromstring(s5.encode()); sd5 = root5.find(N + 'sheetData')
lastr = max(int(x.get('r')) for x in sd5.findall(N + 'row'))
for j, campo in enumerate(["Lion's mane", 'Outros cogumelos (chaga, cordyceps, reishi)']):
    r = lastr + 1 + j
    xml = (f'<row xmlns="{NS}" r="{r}" spans="1:8"><c r="A{r}"><v>81</v></c>' + istr(f'B{r}', 'Collagen Coffee') + istr(f'C{r}', 'Reino Unido')
           + istr(f'D{r}', campo) + f'<c r="E{r}"><v>0</v></c><c r="F{r}"><v>1</v></c>'
           + istr(f'G{r}', "v6: Mushroom & Adaptogen Coffee da Bulk leva lion's mane, cordyceps, reishi, chaga e maitake.")
           + istr(f'H{r}', 'https://www.bulk.com/uk/products/mushroom-adaptogen-coffee/bpf-mcof') + '</row>')
    sd5.append(etree.fromstring(xml))
for tag in ('dimension', 'autoFilter'):
    root5.find(N + tag).set('ref', f'A1:H{lastr+2}')
wr('xl/worksheets/sheet5.xml', etree.tostring(root5, xml_declaration=True, encoding='UTF-8', standalone=True).decode())

# ------------------------------------------------------------------ recalcular ao abrir; remover calcChain
wb = rd('xl/workbook.xml')
wb = re.sub(r'<calcPr ([^>]*?)/>', lambda m: '<calcPr ' + re.sub(r'\s*fullCalcOnLoad="[^"]*"', '', m.group(1)) + ' fullCalcOnLoad="1"/>', wb)
wr('xl/workbook.xml', wb)
if os.path.exists(os.path.join(D, 'xl/calcChain.xml')):
    os.remove(os.path.join(D, 'xl/calcChain.xml'))
    rel = rd('xl/_rels/workbook.xml.rels'); rel = re.sub(r'<Relationship [^>]*calcChain[^>]*/>', '', rel); wr('xl/_rels/workbook.xml.rels', rel)
    ct = rd('[Content_Types].xml'); ct = re.sub(r'<Override [^>]*calcChain[^>]*/>', '', ct); wr('[Content_Types].xml', ct)

for lab, (nums, J) in summary.items():
    print(f'{lab[:55]:55}', nums, 'total', J)
print('cogumelos (filtro atual):', {p: cog(p) for p in paises.values()}, 'players:', {p: tot(p) for p in paises.values()})
