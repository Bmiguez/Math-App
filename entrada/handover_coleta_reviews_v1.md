# Handover: coleta completa de reviews – Caffeine Army x Desincoffee

Versão 1 · 03/11/2026 · continuação do estudo iniciado no Claude (chat)

---

## 1. Objetivo

Coletar **todas** as avaliações públicas de consumidores da **Caffeine Army (SuperCoffee)** e do concorrente **Desincoffee (Super Nutrition / Desinchá)**. Em seguida, codificar cada avaliação nos temas do livro de códigos (seção 6) e entregar a base e os percentuais por tema em uma nova versão da planilha (`reviews_cafe_funcional_v2.xlsx`).

A pergunta de pesquisa é dupla:
- o que leva as pessoas a comprar e recomprar;
- o que as afasta (barreiras).

Tudo comparado entre as duas marcas.

---

## 2. Contexto (o que já foi feito)

- **A v1 é uma amostra pequena.** Ela tem 263 avaliações (258 válidas): 66 da Caffeine Army e 192 do Desincoffee, o que cobre cerca de 2% do total existente.
- **Coleta incompleta na v1.** Reclame Aqui, Mercado Livre, Amazon e Buscapé bloquearam a leitura automática. Do site da Desinchá saíram só as ~40 reviews mais recentes de cada sabor.
- **Resultados preliminares da v1, a validar com a base completa:**
  - Caffeine Army: sabor 65%, energia 53%, hábito/recompra 24%. Barreira principal nas reviews: preço (15% no Brasil).
  - Desincoffee: sabor 57%, energia 23%. Barreira principal: sabor (adoçante, doce demais), 9%.
  - Reclame Aqui da Caffeine Army (contagem oficial): 2.150 reclamações, das quais 29% são produto não recebido e 24% são atraso na entrega.
- **Arquivo de referência:** `entrada/reviews_cafe_funcional_v1.xlsx`. Coloque-o nessa pasta antes de começar. As abas `Livro_de_codigos` e `Base_reviews` definem o formato a seguir.

---

## 3. Regras de trabalho

- **Pastas.**
  - `entrada/`: arquivos recebidos. Nunca editar; trabalhar em cópias.
  - `saida/`: arquivos produzidos.
  - Versionamento: `nome_v2.ext`, `nome_v3.ext`. Nunca sobrescrever uma versão já entregue.
- **Dados brutos.** Salvar o que for coletado, sem alteração, em `saida/bruto/<fonte>/` (JSON ou CSV), com data e hora da coleta. A codificação trabalha sempre a partir desses arquivos, para que a análise possa ser refeita.
- **Ética e limites de coleta.**
  - Respeitar robots.txt e os termos de uso de cada site.
  - Limitar a taxa de requisições (no máximo 1 por segundo, com pausas).
  - Não contornar CAPTCHA, não usar login de terceiros, não burlar bloqueios.
  - Se uma fonte bloquear, registrar no log de cobertura (seção 8) e seguir para a próxima.
  - Prefira API pública oficial quando houver.
- **Privacidade.** Não guardar nome nem foto de autor na base de análise; usar um ID pseudônimo. O texto bruto fica só nos arquivos locais de `bruto/`, para uso desta pesquisa.

---

## 4. Fontes, volumes conhecidos e método sugerido

Os volumes abaixo são os observados em 03/11/2026. Confirme o número atual ao iniciar a coleta e registre a diferença.

### Caffeine Army

| Fonte | Volume conhecido | Ponto de partida | Método sugerido |
|---|---|---|---|
| Mercado Livre (loja oficial e outros vendedores) | 8.600+ avaliações nos kits; os produtos avulsos também têm avaliações | https://www.mercadolivre.com.br/loja/caffeine-army | Verificar se a API pública de avaliações (`api.mercadolibre.com/reviews/item/{ITEM_ID}`) responde. Senão, navegador com paginação. Listar todos os IDs MLB de anúncios SuperCoffee. Atenção: anúncios de catálogo compartilham avaliações; deduplicar por ID de review. |
| Magazine Luiza | 7 páginas de produtos da marca; as avaliações ficam em `/review/{codigo}/.../SA/CINA/` | https://www.magazineluiza.com.br/marcas/caffeine-army/ | Percorrer todas as 7 páginas, extrair os códigos de produto e abrir cada página `/review/` com "Ver mais avaliações". Anúncios de sellers diferentes podem compartilhar o mesmo conjunto de avaliações (ex.: `gfbb268587` e `ce4aj8g32k`); deduplicar. |
| Amazon Brasil | ~907 (agregado pelo Buscapé) | buscar "SuperCoffee Caffeine Army" na amazon.com.br | A Amazon costuma bloquear coleta automática. Tentar pelo navegador do usuário; se bloquear, registrar e usar só os trechos do Buscapé/Zoom. |
| Buscapé / Zoom | replicam reviews da Amazon | https://www.buscape.com.br/suplementos/supercoffee-3-0-380g-caffeine-army | Só se a Amazon falhar; marcar a fonte original como "Amazon via Buscapé" e deduplicar contra a Amazon. |
| Home Tester Club | 76 | https://www.hometesterclub.com/br/pt/reviews/super-coffee--original-classic-size | Navegador. Marcar todas como incentivo = "Sim (testador)". |
| Thingtesting (EUA) | 32 (já completo na v1) | https://thingtesting.com/brands/caffeine-army/reviews | Reaproveitar da v1. |
| Site oficial | verificar se há widget de reviews nas páginas de produto | https://www.caffeinearmy.com.br/pages/vitrine-sc | Em 03/11 o site estava em modo teaser de Black Friday; tentar de novo. |
| Drogasil / Droga Raia / Drogaria SP / Panvel | não contado | páginas de produto SuperCoffee | Verificar se há avaliações com texto; coletar se houver. |
| Reclame Aqui – empresa "Caffeine Army" | 2.150 reclamações | https://www.reclameaqui.com.br/empresa/caffeine-army/lista-reclamacoes/ | Bloqueia leitura automática. Pelo navegador: atualizar as contagens oficiais por tipo de problema e, se possível, coletar título, data, status e problema de cada reclamação dos últimos 12 meses. |
| Reclame Aqui – perfil "SuperCoffee" (não oficial) | 248 | https://www.reclameaqui.com.br/empresa/supercoffee/lista-reclamacoes/ | Mistura reclamações contra sites falsos com algumas sobre a marca real. Coletar separado e marcar a origem. |

### Desincoffee

| Fonte | Volume conhecido | Ponto de partida | Método sugerido |
|---|---|---|---|
| Site Desinchá (widget Loox) | ~585 Chocolate Suíço, ~594 Caramelo, ~577 Extreme Espresso, mais os outros sabores (Vanilla Latte, Baunilha e Avelã, Chocolate Belga, Cinnamon Roll, Palha Italiana, Chocolate Branco, Chocolate Branco com Morango, Evolution Coffee, sticks) | https://www.desincha.com.br/collections/compre-1-leve-2-supercafe | Inspecionar as requisições de rede do widget Loox para achar o endpoint paginado. **Atenção:** o Loox repete a mesma review em vários produtos e mistura reviews de chás; deduplicar por ID de review e excluir o que não for supercafé. |
| Site Super Nutrition | não contado | https://www.supernutrition.com.br/ | Mesmo widget; deduplicar contra o site Desinchá. |
| Mercado Livre | 267 (Chocolate Suíço) e outros anúncios | https://www.mercadolivre.com.br/supercafe-desincoffee-termognico-220g-chocolate-suico-super-nutrition/p/MLB23634072 | Mesmo método do Mercado Livre acima. |
| Amazon / Magalu / farmácias | não contado | buscar "Desincoffee" e "Supercafé Super Nutrition" | Mesmo método das fontes equivalentes da Caffeine Army. |
| Reclame Aqui – "Desinchá" | 1.585 reclamações (todas as linhas da empresa) | https://www.reclameaqui.com.br/empresa/desincha/lista-reclamacoes | Coletar contagens por tipo de problema. Se possível, filtrar só reclamações de supercafé (palavra-chave no título). |

**Se "todos" for inviável em alguma fonte** (bloqueio ou volume grande demais): coletar uma amostra aleatória estratificada por nota (1 a 5 estrelas), com pelo menos 400 avaliações com texto por marca. Registrar no log que a cobertura foi amostral e com qual peso cada estrato entrou.

---

## 5. Esquema da base (aba `Base_reviews`)

Uma linha por avaliação, com as colunas abaixo. Os códigos do livro de códigos vão como colunas 0/1, mais as colunas calculadas "Algum motivo" e "Alguma barreira".

| Coluna | Conteúdo |
|---|---|
| ID | `CA-00001` ou `DE-00001` |
| ID_origem | ID da review no site de origem (para deduplicar) |
| Marca | `Caffeine Army (SuperCoffee)` ou `Desincoffee (Super Nutrition/Desinchá)` |
| Fonte | Mercado Livre, Magazine Luiza, Amazon, Site Desinchá (Loox), etc. |
| Mercado | BR ou EUA |
| Tipo de fonte | Marketplace independente, Site da marca, Plataforma de reviews, Plataforma de teste |
| Produto | nome, sabor e tamanho |
| Nota (1-5) | quando disponível |
| Data | data exata quando houver; senão aproximada |
| Compra verificada | Sim / Não / n/d |
| Incentivo | Sim (produto grátis, influenciador, amigo da marca, testador) / Não informado / Desconhecido |
| Texto_bruto | texto original (pode ir numa aba separada para não poluir) |
| Resumo | paráfrase curta |
| Incluir | 1 = válida; 0 = sem texto, duplicata, outro produto ou marca ambígua |
| Obs | motivo da exclusão ou da dúvida de codificação |
| Link | URL da página de origem |

---

## 6. Livro de códigos (manter idêntico ao da v1)

Os códigos são multirresposta: cada avaliação pode ter vários. Os percentuais não somam 100%.

**Motivos**

| Código | Tema |
|---|---|
| ENE | Energia / disposição / eficácia percebida |
| SAB | Sabor (elogio) |
| HAB | Hábito, fidelidade ou recompra (inclui intenção de recomprar) |
| FOC | Foco / concentração / produtividade |
| TRE | Uso em treino ou esporte |
| SEF | Sem efeito colateral (sem tremedeira, ansiedade, queda, azia, taquicardia, insônia) |
| TEX | Textura / cremosidade |
| PRA | Praticidade / preparo fácil / mistura bem |
| SAU | Saudável (ingredientes, sem açúcar, colágeno, jejum) |
| SUB | Substitui o café comum / atrai quem não tolera café |
| COR | Efeito corporal (termogênico, saciedade, diurético) |
| CB | Custo-benefício / promoção |
| ENT | Entrega ou atendimento elogiado |
| IND | Conheceu por indicação de amigos |
| GER | Elogio genérico, sem motivo específico de produto |

**Barreiras**

| Código | Tema |
|---|---|
| nPRE | Preço alto (conta mesmo em "caro, mas vale"; inclui a gíria "salgado") |
| nSAB | Sabor ruim, artificial, adoçante, doce demais ou fraco |
| nEFE | Efeito fraco ou curto |
| nENT | Não recebeu ou atraso |
| nPED | Pedido errado (sabor trocado, brinde faltando, embalagem divergente) |
| nREN | Rende pouco |
| nTEX | Dissolve mal |
| nOUT | Outro pedido (ex.: versão descafeinada) |

**Neutro**

| Código | Tema |
|---|---|
| CON | Menciona concorrente; anotar qual em Obs |

**Temas novos.** Se surgir um tema frequente que não está no livro (ex.: assinatura ou cancelamento nas reviews, embalagem danificada, alergia), criar um código novo, documentar a definição na aba `Livro_de_codigos` e avisar no relatório final. Não reaproveitar código existente para um tema diferente.

---

## 7. Método de codificação com volume alto

1. **Codificar com LLM em lotes.** Usar lotes de 25 a 50 avaliações, com o livro de códigos e 10 exemplos da v1 no prompt. Saída em JSON: `{id, codigos[], obs}`.
2. **Validar uma amostra manualmente.** Sortear 10% das avaliações (mínimo de 100 por marca) e revisá-las uma a uma. Calcular a concordância por código; se algum ficar abaixo de 85%, refinar a definição e recodificar esse código.
3. **Não codificar por palavra-chave pura.** "Sem energia" não pode virar ENE.
4. **Tratar texto vazio, emoji solto ou só "ok"** como `Incluir = 0`, com o motivo em Obs.

---

## 8. Verificações obrigatórias antes de entregar

- [ ] **Log de cobertura** (aba `Cobertura`): para cada fonte, o volume anunciado no site, o volume coletado, o volume válido, a % de cobertura, a data e o método. Registrar também bloqueios e amostragens.
- [ ] **Deduplicação** por `ID_origem` e por texto idêntico + data + nota entre fontes. Informar quantas duplicatas foram removidas.
- [ ] **Recontagem independente**: recalcular os percentuais em código (pandas) e comparar com as fórmulas da planilha. Zero divergências.
- [ ] **Fórmulas sem erro**: rodar o recálculo (LibreOffice) e conferir zero erros.
- [ ] **Resultados segmentados**, como na v1: por marca, por mercado (BR/EUA), e com e sem fontes incentivadas ou do site da marca. Isso responde se o Desincoffee só parece melhor por vir do próprio site.
- [ ] **Margem de erro** por grupo (95%, p = 50%).
- [ ] **Comparação com a v1**: listar os temas cujo percentual mudou mais de 10 pontos e explicar o motivo.

---

## 9. Entregáveis

1. `saida/reviews_cafe_funcional_v2.xlsx`, com as abas LEIA-ME, Livro_de_codigos, Base_reviews, Resultados, Reclame_Aqui e Cobertura.
2. `saida/bruto/`: dados brutos por fonte.
3. Um resumo curto, de até uma página, com o que mudou em relação à v1, as conclusões e as limitações.

---

## 10. Riscos conhecidos

- **Mercado Livre agrega avaliações** de catálogo e de kits, então a mesma review pode aparecer em vários anúncios.
- **O widget Loox mistura produtos**: chás e supercafés aparecem juntos e a mesma review se repete em várias páginas.
- **"Supercoffee" virou nome genérico.** Reviews no site do concorrente podem falar da Caffeine Army; nesses casos, `Incluir = 0` e explicar em Obs.
- **Reviews no site da marca** podem ser moderadas ou incentivadas com desconto (o Loox costuma oferecer cupom por avaliação com foto). Segmentar nos resultados.
- **Black Friday em andamento** (começou em 03/11): preços e volume de reviews mudam rápido, então registrar a data de cada coleta.
