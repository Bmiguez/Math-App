# Handover: tendências campeãs do café funcional (UK, Alemanha, EUA, Canadá)

Versão 1 · 04/11/2026 · Para revisão completa no Claude Code.

## 1. Pedido da usuária (Janice)

1. Entender **o que domina** os mercados de UK, Alemanha, EUA e Canadá a partir da aba "Concorrentes" do `Mapa_Concorrentes_SuperCoffee_v3.xlsx`: ingredientes (cogumelo/juba-de-leão, proteína, matcha etc.), formatos (incluindo RTD), sabores, claims e players. Complementar com pesquisa web com fontes, "com calma".
2. Levar isso para o Excel: criar uma aba nova com os players, país de origem, países onde atuam e a classificação de tendências, para ter uma **análise quantitativa do screening**. Ela vai apresentar os números e pediu garantia de que todos os players estão incluídos e de que as tendências estão certas.

Preferências dela: resposta em português, entregáveis em `saida/` com versionamento `_v1`, `_v2` (nunca sobrescrever versão já entregue) e nada editado em `entrada/`.

## 2. Entregáveis (todos em `/mnt/project-files/saida/`)

| Arquivo | O que é | Status |
|---|---|---|
| `Mapa_Concorrentes_SuperCoffee_v4.xlsx` | v3 + 2 abas novas: **Resumo tendências** (fórmulas) e **Tendências por player** (95 linhas). As abas originais não foram alteradas. | Entregue, **principal a revisar** |
| `tendencias_campeas_uk_de_eua_ca_v2.html` | Relatório por país: resposta curta, tabelas, cards por país, matcha/RTD, implicações para a SuperCoffee, método e 21 fontes. Números alinhados à v4. | Entregue, **revisar** |
| `tendencias_campeas_uk_de_eua_ca_v1.html` | Primeira versão, com números da classificação automática antes da revisão. Mantida por versionamento. | Substituída pela v2 |
| `tendencias_insumos/` | Scripts, CSV de entrada, JSON intermediários e cópia da v3 (ver seção 5) | Apoio |

## 3. O que foi feito

### 3.1 Base
- A aba "Concorrentes" da v3 tem 143 linhas. Foram filtradas as 95 com **Mercado mapeado** = Reino Unido (30), Alemanha (23), EUA (24) ou Canadá (18).
- O filtro usa **Mercado mapeado**, e não País de origem. Exemplos: Bloom (origem EUA) entra no UK, e Coffee 2.0 (Eslovênia) e Fitking (Polônia) entram na Alemanha.

### 3.2 Classificação (aba "Tendências por player")
- **Etapa automática** (`classify.py`): busca de palavras (regex) nas colunas Marca, Formato, Proposta/ativos-chave e Observações. As colunas Pó instantâneo, Contém café e 2+ sabores vêm direto das flags da base (Instantâneo, Contém café, Sabores ≥2).
- **Etapa manual** (`build_xlsx.py`, função `S()`): ajustes em 17 players, cada um registrado nas colunas *Fonte da classificação*, *Nota da classificação* e *URL verificação*:
  - Lion's mane confirmado na web: RYZE, MUD\WTR, Laird, Four Sigmatic, Clevr, London Nootropics, Coffee of the Apes, PureShrooms, Clearly (Not Coffee), Mush N Go (Brainstoorm).
  - Reformed: cogumelos zerados. O café é de colágeno ou creatina, e o lion's mane é add-on vendido à parte (site feelreformed).
  - Four Sigmatic: Proteína, Colágeno e Creatina = 1 (linha Protein Coffee).
  - Bulletproof: Proteína = 1 (High Protein Iced Coffee, set/2025).
  - MUD\WTR: Contém café = 1 (já vende Coffee blend com 45 mg; a base dizia 0).
  - Giants, WOD Powders e Strong Coffee: Proteína = 0, porque a proteína é colágeno (regra abaixo).
  - DIRTEA: outros cogumelos = 1 (chaga e tremella). Focus Fuel, Clevr e Reformed: sabores citados preenchidos à mão.
  - Sabor "Iced coffee/latte" removido de RYZE, Naturya, Green Origins e Clevr, onde "latte" era tipo de produto e não sabor.
- **Pilar principal**: atribuído à mão, um por player (dicionário `PIL` em `build_xlsx.py`). São 6 pilares: Café de cogumelo, Café proteico, Café com colágeno, Keto/TCM, Café de energia/performance e Energético/alternativa sem café. O `assert` garante que os 95 IDs têm pilar.

### 3.3 Regras de classificação adotadas
1. **Proteína** = whey, proteína do leite ou vegetal. Café cuja proteína é colágeno conta só em **Colágeno**.
2. **Lion's mane** só é marcado se citado na base ou confirmado na web. "Cogumelos" sem detalhe e sem confirmação ficam só em Cogumelos: Coffee 2.0, Urban Calm, The Good Shroom Co, Shyne e Dodjivi.
3. Flags de linha valem para o portfólio da marca, não só para o SKU da linha. Exemplos: Four Sigmatic Protein Coffee e Rapidfire com a linha Protein.
4. **Audiência** = seguidores no Instagram, com perfil contado uma vez (coluna *Seguidores IG (perfil único)*). O Myprotein aparece em 2 produtos.
5. **RTD**: regex sobre Formato e Marca, revisado (15 players). Desses, 11 são energéticos ou bebidas sem café, e só 4 são café pronto: Super Coffee (Kitu), Projo, brüst e Unconform.

### 3.4 Aba "Resumo tendências"
- Tudo em `COUNTIFS`/`SUMIFS` sobre `'Tendências por player'!$X$2:$X$96`. As porcentagens dividem pelo total do país (linha "Total de players").
- Mediana e média de cafeína usam fórmula matricial `MEDIAN(IF(...))` (ArrayFormula).
- O arquivo foi salvo com `fullCalcOnLoad=True`. Os valores são calculados ao abrir no Excel, porque o openpyxl não grava cache.
- Validação feita: recalculado no LibreOffice headless, **0 erros** de fórmula, totais iguais aos do Python, e **0 diferenças** nas abas originais em relação à v3.

### 3.5 Resultados principais (v4/v2)

| | UK (30) | DE (23) | EUA (24) | CA (18) |
|---|---|---|---|---|
| Cogumelos | 15 (50%) | 7 (30%) | 9 (38%) | 9 (50%) |
| Lion's mane | 13 (43%) | 6 (26%) | 8 (33%) | 5 (28%) |
| Proteína | 1 (3%) | 10 (43%) | 11 (46%) | 4 (22%) |
| Colágeno | 7 (23%) | 4 (17%) | 7 (29%) | 2 (11%) |
| Matcha | 2 | 1 | 1 | 0 |
| RTD | 3 | 2 | 6 | 4 |
| Pilar nº1 em marcas | Cogumelo 47% | Proteico 43% | Proteico 29% (cogumelo 25%) | Cogumelo 44% |
| Pilar nº1 em audiência | Proteico 28% / cogumelo 24% / sem café 24% | Proteico 82% | Cogumelo 48% | Proteico 71% |
| Cafeína mediana | 78 mg | 80 mg | 118 mg | 73 mg |

Conclusão do relatório: cogumelo (lion's mane) lidera no UK e nos EUA, e proteína na Alemanha. No Canadá há muitas marcas pequenas de cogumelo, e a proteína tem o alcance. Matcha é tendência de bebida, mas quase não aparece no café funcional (4/95). RTD não lidera em nenhum país, e o pó instantâneo (67%) é o formato dominante.

## 4. Pontos para a revisão (prioridade)

1. **Classificação linha a linha da aba "Tendências por player"**. É o que a Janice vai apresentar. Conferir principalmente:
   - Pilares discutíveis: Laird (cogumelo ou creamer/TCM?), Javy (proteico ou concentrado de baixa caloria?), Everyday Dose (cogumelo ou colágeno?), Strong Coffee e Reformed (colágeno), VitaCup (energia/performance), Hunter & Gather (keto), NO CRASH e Starmount (sem café, mas com cogumelo).
   - Marcas com flag zerada só porque a base não detalha: possível subcontagem de adaptógenos, vitaminas e zero açúcar. "Zero açúcar" ficou **fora** de propósito, porque a base não registra o atributo de forma consistente.
   - Lion's mane não confirmado em 5 marcas (regra 2). Confirmar com o site de cada uma pode subir a contagem.
2. **Fórmulas do Resumo**: abrir no Excel (não só no LibreOffice) e conferir se as ArrayFormulas de mediana calculam. Valores esperados: UK 77,5; DE 80; EUA 117,5; CA 72,5; Total 80.
3. **Consistência entre o relatório v2 e a planilha v4**: todas as porcentagens do HTML (seções 1, 2, 3 e cards) devem bater com a aba Resumo. O texto da seção 4 usa números de mercado da web que não estão na planilha.
4. **Fontes web**: conferir se cada número citado no HTML está na fonte linkada. A Lebensmittel Zeitung [15] tem paywall, e só o lead foi lido. A Clevr [verificação] veio de um diretório (shroomap), e não do rótulo.
5. **Escopo**: a aba Concorrentes é uma seleção, não um inventário. Relatórios anteriores contaram ~179 marcas nos EUA, ~50 no UK, ~45–50 na Alemanha e ~20 no Canadá. Avaliar se vale ampliar a amostra, por exemplo com a aba "Cauda longa" ou as research_notes, antes de apresentar como "mercado".
6. Ordem das abas na v4: as abas novas ficaram depois de "Concorrentes". Ajustar se preferir.

## 5. Como reproduzir (`saida/tendencias_insumos/`)

```bash
cd /mnt/project-files/saida/tendencias_insumos
# 1) conc.csv = aba Concorrentes exportada da v3 (já incluída; para regerar, exportar a aba de Mapa_Concorrentes_SuperCoffee_v3_copia.xlsx)
python3 classify.py            # gera cls_raw.json (flags automáticas) e imprime a revisão por player
python3 build_xlsx.py Mapa_Concorrentes_SuperCoffee_v3_copia.xlsx out.xlsx   # aplica ajustes manuais + pilares, gera cls_final.json e a planilha
soffice --headless --calc --convert-to xlsx --outdir rc out.xlsx              # recalcular para conferir valores
```

- `tag.py` e `pillar.py` são os scripts exploratórios da primeira análise (v1 do relatório). Não são usados na v4.
- Para salvar a versão final foi aplicado `wb.calculation.fullCalcOnLoad=True` antes de gravar como `Mapa_Concorrentes_SuperCoffee_v4.xlsx`. Esse passo não está no script.
- Os scripts usam caminhos relativos e devem rodar de dentro da pasta.

## 6. Material de apoio já existente

- `saida/relatorio_concorrentes_supercoffee_v1.md`: inventário por país das rodadas anteriores. Daí vêm Folgers Functional, Organic Traditions na Voilà, marcas próprias dm/Aldi/Kaufland e o tamanho dos inventários.
- `saida/resumo_marcas_uk_de_v1.md`: 8 marcas UK/DE, incluindo o caso Foodwatch × MORE.
- `saida/mercado_cafe_funcional_tendencias_v2.md`: mercado e drivers (EUA, BR, CL, PE).
- `saida/pesquisa/research_notes/Concorrentes SuperCoffee cinco países/`: notas brutas por país.
