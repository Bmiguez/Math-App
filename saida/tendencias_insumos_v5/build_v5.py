"""Gera Mapa_Concorrentes_SuperCoffee_v5.xlsx a partir da v4 (revisão de tendências + status dos players)."""
import sys, json, copy
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.comments import Comment

SRC, OUT, WEB = sys.argv[1], sys.argv[2], sys.argv[3]
wb = openpyxl.load_workbook(SRC)
t = wb['Tendências por player']
H = [c.value for c in t[1]]
col = {h: i + 1 for i, h in enumerate(H)}
row_of = {t.cell(r, 1).value: r for r in range(2, t.max_row + 1)}
web = {o['ID']: o for o in json.load(open(WEB))}

CHG = PatternFill('solid', fgColor='FFF2CC')
D = '04/11/2026'

# ---------------------------------------------------------------- correções
# (ID): (alterações {coluna: novo valor}, motivo, URL de evidência)
C = {
 # ---- Reino Unido
 50: ({'Matcha': 1, 'Colágeno': 1, 'Creatina': 1}, "Portfólio atual tem Matcha cerimonial com cogumelos, Coffee/Matcha with Collagen e Coffee/Matcha with Creatine.", 'https://dirteaworld.com'),
 83: ({'Matcha': 1, 'Cogumelos': 1, "Lion's mane": 1, 'Outros cogumelos (chaga, cordyceps, reishi)': 1}, "Matcha + Collagen leva lion's mane; Cacao + Chaga no portfólio.", 'https://ancientandbrave.earth'),
 84: ({'Matcha': 1, 'Adaptógenos': 1}, "Magic Matcha: matcha + lion's mane + ashwagandha KSM-66.", 'https://rhealsuperfoods.com'),
 138: ({'RTD (pronto para beber)': 1}, 'Marca vende Sneak Energy em lata (500 ml), além do pó.', 'https://sneakenergy.com'),
 78: ({'Cogumelos': 1, "Lion's mane": 1, 'Adaptógenos': 1}, "Coffee/Matcha with Creatine e Mocha with Collagen declaram 'functional mushrooms'; Lion's Mane vendido como add-on da marca; Vanilla Black Coffee com adaptógenos. Reverte o zeramento de cogumelos da v4.", 'https://www.feelreformed.com'),
 52: ({'Matcha': 1}, "Lançou 'matcha dust' (matcha com lion's mane).", 'https://spacegoods.com'),
 54: ({'Creatina': 1, 'Outros cogumelos (chaga, cordyceps, reishi)': 1}, 'IGNITE (bebida de energia com cordyceps e creatina) no portfólio. Magic Coffee aparece esgotado no site oficial.', 'https://www.vivolife.co.uk'),
 55: ({'Matcha': 1}, 'Matcha Superfood Latte no portfólio.', 'https://naturya.com'),
 95: ({'Cogumelos': 1, "Lion's mane": 1}, "Lançou TENZING Fiery Mango + Lion's Mane (500 mg).", 'https://tenzingnaturalenergy.com'),
 56: ({'País de origem': 'Polônia', "Lion's mane": 1, 'Outros cogumelos (chaga, cordyceps, reishi)': 0, 'Adaptógenos': 1, 'Moído / grão / K-Cup': 1}, "Fabricante é Solve Labs Sp. z o.o. (Lublin, Polônia). O café encontrado é arábica moído 330 g com lion's mane + rhodiola (varejo polonês). Café com chaga não encontrado. Presença no UK não confirmada.", 'https://www.okazje.info.pl/szukaj/solve-labs-mushroom-coffee-kawa-z-rhodiola-i-lion-s-mane-330g/ceny.html'),
 92: ({'Cogumelos': 1, "Lion's mane": 1, 'Outros cogumelos (chaga, cordyceps, reishi)': 1, 'Adaptógenos': 1, 'Matcha': 1, 'Sachê / stick': 1}, "Portfólio tem Mushroom Coffee (lion's mane, reishi, chaga, cordyceps, ashwagandha) e Protein Matcha (colágeno + cogumelos), em pote e sachês. Proteína segue 0 (é colágeno).", 'https://www.wodpowders.co.uk'),
 81: ({'Cogumelos': 1, 'Adaptógenos': 1}, 'Bulk vende Mushroom & Adaptogen Coffee.', 'https://www.bulk.com/uk/products/mushroom-adaptogen-coffee/bpf-mcof'),
 82: ({'Matcha': 1, 'Cogumelos': 1, "Lion's mane": 1, 'TCM / keto': 1}, "Rótulo atual: colágeno 10–20 g + MCT + lion's mane + vitaminas; lançou Vanilla Collagen Matcha.", 'https://giantscoffee.co.uk'),
 59: ({"Lion's mane": 1, 'Adaptógenos': 1}, "Produto: Functional Mushroom Chocolate Drink com lion's mane e ashwagandha.", 'https://www.nocrash.co.uk'),
 86: ({'Matcha': 1}, 'Ceremonial Grade Matcha no portfólio.', 'https://www.ancientextracts.co.uk'),
 88: ({'Pó instantâneo': 1, 'Outros cogumelos (chaga, cordyceps, reishi)': 1}, 'Linha inclui café moído, instantâneo e blend de 5 cogumelos.', 'https://www.merryhill-mushrooms.co.uk/mushroom-coffee-and-hot-chocolate-range'),
 89: ({'Matcha': 1}, 'Linha de Matcha Green Tea Drink e Matcha Latte.', 'https://greenorigins.com'),
 90: ({'Matcha': 1}, "Organic Lion's Mane Matcha Latte no portfólio.", 'https://mushroomsforlife.com'),
 91: ({'Matcha': 1, 'TCM / keto': 1}, "Lion's Mane Coffee leva óleo de coco MCT; vende matcha cerimonial e matcha latte.", 'https://cheerfulbuddha.com'),
 # ---- Alemanha
 101: ({'Matcha': 1}, 'Protein Matcha no portfólio.', 'https://www.esn.com'),
 60: ({'Matcha': 1}, 'Matcha Latte e sabores com matcha.', 'https://www.holy.com'),
 102: ({'Matcha': 1}, "Portfólio tem Protein Matcha; o café proteico aparece como 'Protein Frappé' no site (rockanutrition.de).", 'https://www.rockanutrition.de'),
 140: ({'Matcha': 1}, 'Protein Iced Matcha 500 g no portfólio.', 'https://neosupps.com'),
 112: ({'Matcha': 1}, 'Linha Strawberry Matcha / Weisse Schoko Matcha.', 'https://www.koawach.de'),
 61: ({'Pó instantâneo': 1, 'Moído / grão / K-Cup': 0, 'RTD (pronto para beber)': 0, 'Colágeno': 1, 'Creatina': 1, 'Vitaminas / minerais': 1}, 'Produto atual é café instantâneo à base de grãos (sem café), com versões com creatina, colágeno + hialurônico, ferro + vitaminas B. Não há RTD no site.', 'https://www.ciaocoffee.eu'),
 109: ({'Matcha': 1}, 'Matcha 2.0 no portfólio.', 'https://tastydose.com'),
 143: ({'Matcha': 1}, 'Matchaelixier no portfólio.', 'https://naturtreu.de'),
 # ---- EUA
 19: ({'Matcha': 1}, 'Mushroom Matcha no portfólio.', 'https://www.ryzesuperfoods.com'),
 28: ({'Matcha': 1}, 'Matcha Collagen no portfólio. No site só aparecem creamers (Collagen Coffee não listado).', 'https://www.vitalproteins.com'),
 22: ({'Matcha': 1, 'TCM / keto': 1, 'Creamer': 1}, 'Strawberry Matcha / Morning Matcha e creamer de coco com MCT.', 'https://mudwtr.com'),
 23: ({'Proteína': 1, 'Matcha': 1}, 'Protein Coffee (10 g de proteína do leite) e Protein Matcha (lançado 06/2026).', 'https://lairdsuperfood.com'),
 20: ({'Matcha': 1}, 'Mushroom Matcha+ no portfólio.', 'https://healf.com/products/everyday-dose-matcha'),
 21: ({'Matcha': 1}, 'Protein Matcha e Protein & Creatine Matcha.', 'https://us.foursigmatic.com'),
 130: ({'Creamer': 1}, 'Proffee (Protein Coffee) Stix lançado 04/2026: 20 g de whey e 150 mg de cafeína; Protein Creamer Stix lançado 10/2026.', 'https://www.skinnymixes.com/collections/proffee-stix'),
 30: ({'Creatina': 1}, 'Creatine Sticks/Sachets no portfólio.', 'https://www.neutonic.com'),
 25: ({'Pó instantâneo': 1, 'Moído / grão / K-Cup': 0, 'Creamer': 0, 'Cafeína por dose (mg)': 80}, 'Site atual: RTD Protein+, Protein+ Powdered Coffee (80 mg) e linha XXTRA (200 mg). Moído/K-Cup e creamer não constam. Cafeína ajustada para a linha principal (80 mg); a aba Concorrentes mantém 200.', 'https://www.drinksupercoffee.com'),
 123: ({'Matcha': 1}, 'Matcha Collagen Latte no portfólio.', 'https://strongcoffeecompany.com'),
 128: ({'Proteína': 1, 'Colágeno': 1}, 'Slim Protein Coffee Shake e Collagen Elixir Sticks no portfólio.', 'https://www.vitacup.com'),
 # ---- Canadá
 115: ({'Matcha': 1}, "Enhanced Collagen Protein Matcha no portfólio; o creamer mapeado aparece hoje como 'Enhanced Collagen Protein Creamer'.", 'https://organika.com'),
 33: ({'Matcha': 1, 'Probióticos / fibras': 1}, 'Matcha Latte with Probiotics e Premium Matcha no portfólio.', 'https://organictraditions.com'),
 135: ({'Matcha': 1, 'Colágeno': 1}, "Protein Strawberry Matcha Latte; proteína de caldo de osso descrita como 'collagen-rich'.", 'https://becksbroth.com'),
 37: ({'Matcha': 1, 'TCM / keto': 1, 'Creamer': 1, 'Moído / grão / K-Cup': 1}, 'Portfólio inclui café moído, creamers de coco com MCT e Vanilla Matcha Latte.', 'https://pureshrooms.co'),
 122: ({'Cafeína por dose (mg)': 120, 'Adaptógenos': 1, 'Vitaminas / minerais': 1}, 'Botany Energy (lançado 12/2025): 120 mg de cafeína, ginseng, schisandra, vitaminas B.', 'https://retail-insider.com/retail-insider/2026/01/collective-arts-carves-out-a-new-space-in-clean-functional-energy-with-botany/'),
 119: ({"Lion's mane": 1, 'Outros cogumelos (chaga, cordyceps, reishi)': 1}, "Linhas Dreamer/Lioness com lion's mane; Centered com chaga e reishi.", 'https://urbancalmcoffee.ca'),
 117: ({"Lion's mane": 1, 'Outros cogumelos (chaga, cordyceps, reishi)': 1, '2+ sabores': 1, 'Sabor: Chai/especiarias/sobremesa': 1, 'Sabores citados': 'Chai/especiarias/sobremesa'}, "Três versões: lion's mane + bordo, chaga + coco, turkey tail + cardamomo.", 'https://shynecoffee.ca'),
 118: ({"Lion's mane": 1, 'Outros cogumelos (chaga, cordyceps, reishi)': 1, 'Pó instantâneo': 1, 'Moído / grão / K-Cup': 0, 'Cafeína por dose (mg)': 64}, "Produtos atuais são instantâneos; 4 Protection leva lion's mane, reishi, chaga e turkey tail; Vitality declara 64 mg de cafeína.", 'https://www.dodjivi.com'),
}

# ---------------------------------------------------------------- status
S = {}  # ID: (status, evidência)
ATIVO = 'Ativo'
for i, o in web.items():
    home = o.get('home') or [None, None]
    S[i] = (ATIVO, f'Site oficial no ar e linha encontrada no catálogo ({D}): {home[1]}')
SP = {
 79: (ATIVO, 'Menu do site Myprotein UK tem a categoria Iced Coffee; produto também listado em comparador alemão (droptime.de).'),
 137: ('Incerto', 'Produto de 2020. Ainda listado no site Myprotein Canadá, mas não confirmado no site UK.'),
 94: (ATIVO, 'Lançada no UK via Amazon/TikTok Shop e Holland & Barrett (The Grocer, 2026).'),
 81: (ATIVO, 'Página do produto no site Bulk UK no ar.'),
 54: ('Ativo – produto esgotado', 'Magic Coffee aparece esgotado no site oficial; varejistas listam como backorder. Marca ativa.'),
 56: ('Incerto', 'Site oficial inacessível; café da marca só encontrado em varejo polonês; presença no UK não confirmada.'),
 57: (ATIVO, 'Pote 213 g à venda em varejistas UK (Healf, Holland & Barrett); sachês esgotados na Medino; site próprio sem conteúdo.'),
 53: ('Ativo – linha alterada', "Café moído com lion's mane não está mais no site; marca vende café 'clean' + elixires de lion's mane/reishi."),
 93: (ATIVO, 'Cold brew RTD listado na Holland & Barrett (600 lojas a partir de 01/2026); sticks da loja própria estão esgotados.'),
 103: (ATIVO, 'Site mudou para sunday.de (domínio sundaynatural.com está à venda); Protein Coffee à venda e no comparador droptime.de.'),
 136: (ATIVO, 'Listado em Fitadium e varejo polonês (doz.pl); alguns lotes com validade curta.'),
 102: ('Ativo – linha alterada', "Protein Coffee Iced Latte ainda no comparador droptime.de; no site o café proteico aparece como 'Protein Frappé'."),
 104: (ATIVO, 'Energy Kaffee 900 g listado no comparador droptime.de (11/2026); site ruehl24.de no ar.'),
 99: (ATIVO, 'Lançado 09/2025 (Stack3d); listado no comparador droptime.de.'),
 142: (ATIVO, 'nu3.de redireciona para Shop Apotheke; produto disponível lá.'),
 108: (ATIVO, 'Página de cafés funcionais da BeKeto no ar.'),
 107: ('Inativo / pausado', "Site em modo senha ('Opening soon'); nenhum produto à venda."),
 62: (ATIVO, 'Site próprio inacessível; produto à venda na DocMorris (disponível).'),
 105: ('Não verificado (grupo)', 'Linha agrupa ~20 marcas; checagem individual não feita. Várias aparecem no comparador droptime.de.'),
 106: (ATIVO, 'Disponível na Shop Apotheke.'),
 110: ('Inativo / pausado', "Site em modo senha: 'We are rebuilding NOT COFFEE... will be back soon'."),
 144: (ATIVO, 'Página do produto no dm.de responde (conteúdo carregado por JavaScript).'),
 61: ('Ativo – linha alterada', 'Marca ativa; produto mudou de formato (instantâneo à base de grãos), sem RTD.'),
 20: (ATIVO, 'Site com proteção anti-bot; marca em 1.500 lojas Target desde 08/2025 e com Matcha+ em varejistas.'),
 24: (ATIVO, 'Site com proteção anti-bot; lançou sabor baunilha do High Protein Iced Coffee em 03/2026 e café com creatina em 2026.'),
 26: (ATIVO, "Marca hoje grafada 'Javvy'; site com protein coffee, refreshers, creamer e concentrado."),
 130: ('Ativo – linha alterada', "Produto mapeado relançado como 'Proffee Stix' (04/2026)."),
 32: ('Ativo – marca renomeada', 'Guayakí opera como Yerba Madre (site yerbamadre.com).'),
 25: ('Ativo – linha alterada', 'Portfólio atual: RTD e pó Protein+; sem creamer e moído no site.'),
 126: (ATIVO, 'Site inacessível pelo proxy; à venda na Target, com expansão de latas em 05/2026 (BevNET).'),
 127: (ATIVO, 'Site inacessível pelo proxy; à venda no Walmart e varejo internacional (2026).'),
 131: ('Incerto', 'Site da Le-Vel não lista produtos sem login; Thrive Café consta em listas de produtos, sem confirmação recente.'),
 29: (ATIVO, 'Site oficial no ar, com energéticos.'),
 129: (ATIVO, 'Iced Coffee With Protein no catálogo oficial.'),
 132: (ATIVO, 'Protein Coffee no catálogo oficial.'),
 124: (ATIVO, 'Coffee Protein no catálogo oficial.'),
 115: ('Ativo – linha alterada', "Creamer mapeado aparece como 'Enhanced Collagen Protein Creamer'."),
 133: (ATIVO, 'Protein Coffee (Original Blend) no catálogo oficial.'),
 35: (ATIVO, 'Site inacessível pelo proxy; linhas Vital/Vigor/Spark à venda em Ma Caféine e Well.ca.'),
 122: (ATIVO, 'Lançado 12/2025; 7-Eleven Canadá. drinkbotany.com é loja-modelo vazia; a marca vende pela Collective Arts.'),
 34: (ATIVO, 'Site migrou para coffeeapes.com; produto à venda (Amazon, Walmart.ca). Banner do site desatualizado.'),
 36: ('Inativo / pausado', 'Site fora do ar. A empresa virou Mercanto Holdings (02/2025), com foco em cannabis/vape; sem evidência da linha de cogumelos em 2025–26.'),
 113: (ATIVO, 'Cold brew proteico à venda na Costco.ca, Goodness Me e Natura Market (2026).'),
 116: (ATIVO, 'Site com erro de certificado; Ghee MCT Creamer e MCT Collagen Creamer à venda em varejo canadense.'),
 134: ('Incerto', 'Site fora do ar; só aparece em marketplaces (eBay com "sold out"). Provável descontinuação.'),
 121: (ATIVO, 'Lançada 05/2026 (GlobeNewswire); loja oficial com estoque.'),
 117: (ATIVO, 'Site oficial no ar, com três versões de café.'),
 96: (ATIVO, 'Site oficial no ar. Atenção: é cápsula, não bebida.'),
}
S.update(SP)
NOTE_EXTRA = {
 116: "Sproos tem dois creamers: Ghee MCT (sem colágeno) e MCT Collagen (colágeno marinho). Colágeno = 1 vale pelo portfólio; a frase da base 'sem colágeno' refere-se só ao de ghee.",
 32: 'Marca renomeada para Yerba Madre.',
 26: "Marca hoje grafada 'Javvy'. Pilar proteico confirmado: site centrado em Protein Coffee.",
 96: 'Cápsula nootrópica, não bebida. Mantida por estar na base; avaliar exclusão.',
 103: 'Site oficial atual: sunday.de.',
 34: 'Site atual: coffeeapes.com.',
}

# ---------------------------------------------------------------- aplicar
log = []
for i, (chg, why, url) in C.items():
    r = row_of[i]
    for k, v in chg.items():
        c = t.cell(r, col[k])
        if c.value != v:
            log.append((i, t.cell(r, 2).value, t.cell(r, 5).value, k, c.value, v, why, url))
            c.value = v
            c.fill = CHG
    nota = t.cell(r, col['Nota da classificação'])
    nota.value = ((nota.value + ' | ') if nota.value else '') + 'v5: ' + why
    nota.fill = CHG
    fonte = t.cell(r, col['Fonte da classificação'])
    fonte.value = 'Base + revisão v5 (site/varejo, 11/2026)'
    u = t.cell(r, col['URL verificação'])
    u.value = url if not u.value else u.value + ' ; ' + url
for i, txt in NOTE_EXTRA.items():
    r = row_of[i]; nota = t.cell(r, col['Nota da classificação'])
    nota.value = ((nota.value + ' | ') if nota.value else '') + 'v5: ' + txt
    nota.fill = CHG
    if i == 116:
        log.append((i, t.cell(r, 2).value, t.cell(r, 5).value, 'Nota', '', 'esclarecida', txt, 'https://well.ca/products/sproos-mct-collagen-creamer_172373.html'))

# 2+ sabores consistente com sabores citados (Shyne)
# novas colunas de status
hdr_src = t.cell(1, 1)
newcols = ['Status (verificação 04/11/2026)', 'Evidência do status', 'Ativo confirmado (1/0)']
base_c = t.max_column
for j, h in enumerate(newcols):
    c = t.cell(1, base_c + 1 + j, h)
    c.font = copy.copy(hdr_src.font); c.fill = copy.copy(hdr_src.fill)
    c.alignment = copy.copy(hdr_src.alignment); c.border = copy.copy(hdr_src.border)
ST, EV, AT = base_c + 1, base_c + 2, base_c + 3
body_font = copy.copy(t.cell(2, 2).font)
for i, r in row_of.items():
    st, ev = S[i]
    t.cell(r, ST, st).font = body_font
    t.cell(r, EV, ev).font = body_font
    t.cell(r, AT, f'=IF(LEFT({openpyxl.utils.get_column_letter(ST)}{r},5)="Ativo",1,0)').font = body_font
    if st != ATIVO:
        t.cell(r, ST).fill = PatternFill('solid', fgColor='F4CCCC' if st.startswith(('Inativo', 'Incerto')) else 'FCE5CD')
from openpyxl.utils import get_column_letter as L
t.column_dimensions[L(ST)].width = 26
t.column_dimensions[L(EV)].width = 70
t.column_dimensions[L(AT)].width = 14
t.auto_filter.ref = f'A1:{L(AT)}{t.max_row}'

# ---------------------------------------------------------------- Resumo
R = wb['Resumo tendências']
R['A2'] = R['A2'].value + ' Revisão v5 (04/11/2026): flags conferidas no site oficial/varejo de cada marca; status de atividade nas colunas AP–AR da aba de players.'
title_font = copy.copy(R['A62'].font); title_fill = copy.copy(R['A62'].fill)
sub_font = copy.copy(R['B63'].font); sub_fill = copy.copy(R['B63'].fill)
lab_font = copy.copy(R['A64'].font); num_font = copy.copy(R['B64'].font)
# mover notas para baixo: reescrever bloco de leitura em linhas 81+
old_notes = [R.cell(rr, 1).value for rr in range(67, 74)]
old_style = (copy.copy(R['A67'].font), copy.copy(R['A68'].font))
for rr in range(67, 74):
    R.cell(rr, 1).value = None
paises = [('B', 'Reino Unido'), ('D', 'Alemanha'), ('F', 'EUA'), ('H', 'Canadá')]
r0 = 67
R.cell(r0, 1, 'Status dos players (verificação 04/11/2026)').font = title_font
R.cell(r0, 1).fill = title_fill
for cl, p in paises + [('J', 'Total')]:
    R[f'{cl}{r0}'] = p; R[f'{cl}{r0}'].font = title_font; R[f'{cl}{r0}'].fill = title_fill
    nxt = chr(ord(cl) + 1)
    R[f'{nxt}{r0}'].fill = title_fill
    R[f'{cl}{r0+1}'] = 'Nº'; R[f'{nxt}{r0+1}'] = '%'
    for x in (cl, nxt):
        R[f'{x}{r0+1}'].font = sub_font; R[f'{x}{r0+1}'].fill = sub_fill
R.cell(r0 + 1, 1).fill = sub_fill
cats = [('Ativo', '"Ativo"'), ('Ativo com ressalva (linha alterada, esgotado, renomeado)', '"Ativo –*"'),
        ('Incerto', '"Incerto"'), ('Inativo / pausado', '"Inativo / pausado"'), ('Não verificado (grupo)', '"Não verificado (grupo)"')]
P = "'Tendências por player'"
SL = L(ST)
for k, (lab, crit) in enumerate(cats):
    rr = r0 + 2 + k
    R.cell(rr, 1, lab).font = lab_font
    for cl, p in paises:
        R[f'{cl}{rr}'] = f'=COUNTIFS({P}!$E$2:$E$96,"{p}",{P}!${SL}$2:${SL}$96,{crit})'
        nxt = chr(ord(cl) + 1)
        R[f'{nxt}{rr}'] = f'=IFERROR({cl}{rr}/{cl}$6,0)'
    R[f'J{rr}'] = f'=B{rr}+D{rr}+F{rr}+H{rr}'
    R[f'K{rr}'] = f'=IFERROR(J{rr}/J$6,0)'
rr = r0 + 2 + len(cats)
R.cell(rr, 1, 'Ativos confirmados (total)').font = Font(name=lab_font.name, size=lab_font.size, bold=True)
for cl, p in paises:
    R[f'{cl}{rr}'] = f'=SUMIFS({P}!${L(AT)}$2:${L(AT)}$96,{P}!$E$2:$E$96,"{p}")'
    nxt = chr(ord(cl) + 1); R[f'{nxt}{rr}'] = f'=IFERROR({cl}{rr}/{cl}$6,0)'
R[f'J{rr}'] = f'=B{rr}+D{rr}+F{rr}+H{rr}'; R[f'K{rr}'] = f'=IFERROR(J{rr}/J$6,0)'
for r_ in range(r0 + 2, rr + 1):
    for x in 'BDFHJ':
        R[f'{x}{r_}'].font = num_font; R[f'{x}{r_}'].number_format = 'General'
        n = chr(ord(x) + 1); R[f'{n}{r_}'].font = num_font; R[f'{n}{r_}'].number_format = '0%'

nr = rr + 2
old_notes[2] = old_notes[2].replace('17 players tiveram ajuste manual ou verificação na web', '17 players tiveram ajuste manual ou verificação na web na v4, e 46 na v5')
notes = [old_notes[0]] + old_notes[1:] + [
 "• Revisão v5: as flags valem para o portfólio de bebidas da marca (café, latte, matcha, cacau, energético), conferido no site oficial em 04/11/2026. Pós de whey, cápsulas e acessórios não contam.",
 "• Matcha: em quase todas as marcas é extensão de linha (marca de cogumelo, colágeno ou proteína que lançou uma versão matcha), não o produto principal. Nenhum player tem matcha como pilar.",
 "• Status: 'Ativo' = site oficial ou varejo vende a linha em 11/2026. 'Ativo – …' = marca ativa, mas o produto mapeado mudou, esgotou ou a marca foi renomeada. 'Incerto' = sem confirmação. As contagens acima incluem todos os 95 players; use a coluna 'Ativo confirmado' para filtrar.",
 "• Células alteradas na v5 estão em amarelo na aba de players. A lista completa das alterações (antes/depois e fonte) está na aba 'Revisão v5'.",
]
for k, txt in enumerate(notes):
    c = R.cell(nr + k, 1, txt)
    c.font = old_style[0] if k == 0 else old_style[1]
    c.alignment = copy.copy(R['A68'].alignment) if R['A68'].alignment else Alignment(wrap_text=False)

# ---------------------------------------------------------------- aba Revisão v5
V = wb.create_sheet('Revisão v5', index=wb.sheetnames.index('Tendências por player') + 1)
cols = ['ID', 'Marca / produto', 'Mercado mapeado', 'Campo', 'Antes (v4)', 'Depois (v5)', 'Motivo', 'Fonte']
for j, h in enumerate(cols, 1):
    c = V.cell(1, j, h); c.font = copy.copy(hdr_src.font); c.fill = copy.copy(hdr_src.fill); c.alignment = copy.copy(hdr_src.alignment)
for k, rowv in enumerate(log, 2):
    for j, v in enumerate(rowv, 1):
        V.cell(k, j, v).font = body_font
for j, w in enumerate([6, 34, 14, 30, 12, 12, 90, 60], 1):
    V.column_dimensions[L(j)].width = w
V.freeze_panes = 'A2'
V.auto_filter.ref = f'A1:H{len(log)+1}'

wb.calculation.fullCalcOnLoad = True
wb.save(OUT)
print('alterações de célula:', len(log), '| players alterados:', len(C))
from collections import Counter
print(Counter(s for s, _ in S.values()))
