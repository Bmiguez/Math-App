# Metodologia: reviews de café funcional (6 marcas)

Documento de referência para a base `reviews_cafe_funcional_v4.xlsx` (04/11/2026), que tem 4.499 linhas coletadas e 1.890 reviews válidas.

## Resumo

- **O que foi feito:** foram coletadas reviews públicas de consumidores de 6 marcas de café funcional. Cada review foi lida inteira e recebeu os temas que cita, escolhidos de uma lista fixa de 28 códigos (o Livro de códigos). O resultado de cada tema é o percentual de reviews que o citam.
- **Limite principal:** quase todas as reviews de SuperCoffee e Desincoffee vêm do site da própria marca, o que puxa os resultados para o elogio. Brainstorm e Ultracoffee têm n pequeno. Compare a ordem dos temas dentro de cada marca, não os percentuais entre marcas.

## 1. Marcas consideradas

| ID | Marca | Empresa | Reviews válidas |
|---|---|---|---|
| CA | SuperCoffee 3.0 | Caffeine Army | 1.417 |
| DE | Desincoffee / Supercafé | Desinchá / Super Nutrition | 421 |
| BS | Brainstorm Coffee | Essential Nutrition | 25 |
| UC | Ultracoffee | Grupo 3corações / Plant Power | 27 |
| VC | V-Coffee Energy Boost | Vitafor | 0 |
| MC | Mega Coffee | Allure | 0 |

**Como a marca de cada produto foi identificada:** pelo nome do produto e pela marca cadastrada na loja.
- "supercoffee" ou "caffeine army": CA.
- "desinc": DE.
- "brainstorm" + "coffee": BS.
- "ultracoffee": UC.
- "v-coffee": VC.
- "mega coffee" + "allure": MC.

**O que ficou na base com Incluir = 0:**
- Outras linhas das mesmas empresas, como Koala, Morning Shot, Whey e Creatina da Caffeine Army.
- Kits do Desinchá com creatina, melatonina ou chá, quando o texto não cita o café.

## 2. Fontes

### 2.1 Fontes coletadas

| Fonte | Tipo | Marcas | Como foi coletada | Válidas |
|---|---|---|---|---|
| Site Caffeine Army | Site da marca | CA | Widget Judge.me (ver 2.2) | 1.331 |
| Site Desinchá | Site da marca | DE | HTML das 59 páginas de supercafé, com o widget Loox já renderizado | 414 |
| Site Essential Nutrition | Site da marca | BS | Dados estruturados da página (JSON-LD schema.org/Review) | 22 |
| Mercafé (loja da 3corações) | Site da marca | UC | HTML das 12 páginas de produto (widget Yourviews) | 14 |
| Thingtesting (EUA) | Plataforma de reviews | CA | HTML de 2 páginas | 32 |
| Home Tester Club | Plataforma de teste (produto grátis) | CA, UC | Páginas públicas, que mostram 10 reviews por produto | 20 |
| Americanas, Drogaria São Paulo, Drogarias Pacheco | Varejo | CA, BS | Busca no catálogo da loja e API pública do widget Konfidency | 16 |
| Pague Menos, Drogal | Varejo | CA, DE, UC | Busca no catálogo da loja e widget Yourviews | 8 |
| Magalu, Amazon (via Buscapé e Zoom), Mercado Livre | Marketplace | CA, DE | Herdadas da v1, só com paráfrase e sem texto original | 33 |

### 2.2 Exemplo de coleta: Judge.me (site da Caffeine Army)

O Judge.me é o aplicativo de avaliações da loja Shopify da Caffeine Army. As avaliações ficam nos servidores do Judge.me, e a página do produto só as exibe.

1. **Leitura da página do produto.** O coletor leu as 127 páginas de produto da loja; 44 delas tinham avaliações. De cada uma, extraiu o número interno do produto e o total de avaliações. Exemplo:
   https://www.caffeinearmy.com.br/products/supercoffee-beijinho-economic-size
   (produto `8131660644574`, 85 avaliações).
2. **Pedido das avaliações.** Elas foram pedidas ao Judge.me em páginas de 20, pelo mesmo caminho que o navegador usa ao clicar em "ver mais". Exemplo:
   https://api.judge.me/reviews/reviews_for_widget?url=caffeinearmy.myshopify.com&shop_domain=caffeinearmy.myshopify.com&platform=shopify&page=1&per_page=20&product_id=8131660644574
3. **Campos extraídos:**
   - nota, data, título e texto;
   - compra verificada;
   - formulário opcional (objetivo de uso, idade, se recomendaria), que alimenta a aba Formulario_CA.

O script é `scripts/coleta_judgeme.py`.

### 2.3 Fontes tentadas e não coletadas

| Fonte | Motivo |
|---|---|
| Mercado Livre | O robots.txt bloqueia agentes automáticos. Pela API oficial, a busca no catálogo funciona (497 produtos das marcas, 182 com anúncio ativo). Já o endpoint de opiniões responde 403 tanto com token de app quanto com token de usuário (OAuth), porque a API não libera opiniões de anúncios de terceiros. |
| Amazon, Buscapé, Zoom | O robots.txt bloqueia agentes automáticos. |
| Magazine Luiza, Drogasil, Droga Raia, Panvel, Beleza na Web | HTTP 403 (bloqueio anti-robô). |
| Site Allure (Mega Coffee) | HTTP 403. |
| Site Vitafor (V-Coffee) | O app de reviews está instalado, mas não há nenhuma review publicada. |
| Reclame Aqui | HTTP 403 no site e na API. A aba Reclame_Aqui usa as contagens da v1, de 03/11/2026. |

### 2.4 Regras de coleta

- Respeitar o robots.txt e os termos de uso de cada site.
- No máximo 1 requisição por segundo.
- Não contornar CAPTCHA, login ou bloqueio. Cada bloqueio foi registrado na aba Cobertura.
- Usar API oficial sempre que houver.

## 3. Preparação da base

### 3.1 Privacidade

- **Dados removidos:** nome, foto, e-mail, IP e ID de usuário dos autores não entram na base de análise.
- **Identificação:** cada review recebe um ID pseudônimo (CA-00001, DE-00001…).
- **Texto:** nomes e endereços escritos pelos próprios autores dentro do texto foram removidos.
- **Dados brutos:** ficam só localmente, fora do Git.

### 3.2 Deduplicação

Cerca de 1.000 cópias foram removidas, nesta ordem:
1. mesmo ID de origem;
2. mesmo texto, data e hora, nota e autor (o Loox replica a mesma review em vários produtos);
3. mesmo autor com o mesmo texto em outro produto;
4. quase-duplicatas (texto quase idêntico), marcadas à mão.

### 3.3 Critério de inclusão

Ficam com **Incluir = 0**, continuam na base e têm o motivo registrado em Obs:
- texto vazio ou só pontuação;
- duplicata;
- outro produto;
- marca ambígua;
- quem ainda não provou o produto.

Casos específicos:
- **Kits do Desinchá** (Kit Core, Prime, Full): só entram se o texto citar café ou supercafé.
- **"Supercoffee" como nome genérico:** no site do Desinchá, se a review indica outra marca, ela sai.

## 4. Classificação (codificação temática)

### 4.1 Procedimento

- Cada review válida foi lida inteira, e a codificação foi feita em lotes.
- É multirresposta: uma review recebe todos os temas que cita.
- A codificação não é por palavra-chave, e sim pelo sentido. Por exemplo, "sem energia" não vira ENE, e "indiquei para amigos" não vira IND.
- Uma barreira conta mesmo junto de um elogio. Por exemplo, "caro, mas vale" recebe nPRE e CB.
- A codificação foi feita pelo Claude (IA), seguindo as regras escritas do Livro de códigos. Não houve codificador humano.

### 4.2 Livro de códigos (28 códigos)

**Motivos (15)**

| Código | Tema |
|---|---|
| ENE | Energia, disposição, eficácia percebida ("cumpre o que promete") |
| SAB | Sabor (elogio), aroma, sabor específico |
| HAB | Hábito, fidelidade, recompra ou intenção de recompra |
| FOC | Foco, concentração, produtividade |
| TRE | Uso em treino ou esporte |
| SEF | Sem efeito colateral (tremedeira, ansiedade, taquicardia, insônia, pico) |
| TEX | Textura, cremosidade |
| PRA | Praticidade, preparo fácil, mistura bem, receitas |
| SAU | Saudável (ingredientes, sem açúcar, jejum, proteína) |
| SUB | Substitui o café comum, atrai quem não tolera café |
| COR | Efeito corporal (termogênico, saciedade, diurético) |
| CB | Custo-benefício, promoção, "vale a pena" |
| ENT | Elogio à entrega ou ao atendimento |
| IND | A própria pessoa conheceu o produto por indicação |
| GER | Elogio genérico, só quando não há outro motivo ("amei") |

**Barreiras (11)**

| Código | Tema |
|---|---|
| nPRE | Preço alto (inclui "caro, mas vale" e a gíria "salgado") |
| nSAB | Sabor ruim, artificial, doce demais ou fraco |
| nEFE | Efeito fraco ou curto |
| nENT | Não recebeu ou atraso na entrega |
| nPED | Pedido errado (sabor trocado, brinde faltando) |
| nREN | Rende pouco |
| nTEX | Dissolve mal ou textura ruim |
| nOUT | Pede outra versão (descafeinado, sem lactose, sachê) |
| nDIS | Sabor indisponível, esgotado ou descontinuado |
| nATE | Atendimento ou suporte ruim |
| nING | Crítica a um ingrediente da fórmula |

**Neutros (2)**

| Código | Tema |
|---|---|
| CON | Menciona concorrente ou "outras marcas" |
| ASS | Menciona a assinatura Prime |

### 4.3 Indicador

**% do tema = reviews válidas que citam o tema ÷ reviews válidas do grupo.**

- Como cada review pode citar vários temas, os percentuais não somam 100%.
- Na planilha, tudo é calculado por fórmula sobre a aba Base_reviews.

### 4.4 Segmentos de controle

Os resultados são separados por:
- site da marca × fora do site;
- Brasil × EUA;
- incentivada (produto grátis) × não incentivada;
- com e sem o pico de nov–dez/2025 no site da Caffeine Army.

O último corte existe porque 91% das reviews válidas desse site foram publicadas nesse período, no formato de "ranking de sabores", o que indica uma campanha de avaliação solicitada pela marca.

## 5. Validação da classificação

- **Método:** recodificação cega, sem acesso aos códigos originais, de 306 reviews:
  - **Rodada v2:** amostra aleatória de 10% de CA (semente 20261104) e no mínimo 100 de DE.
  - **Rodada v4:** todas as 68 reviews novas da v3 (BS 25, UC 27, CA 13, DE 3).
- **Resultado:**
  - Concordância de 96% ou mais em todos os códigos.
  - O código menos estável é PRA (kappa 0,87).
  - Na rodada v4, a inclusão bateu em 67 de 68 reviews, e os códigos ficaram idênticos em 51 de 68.
- **Uso:** a codificação original foi mantida. A recodificação mede a estabilidade e não altera os códigos.
- **Limitação:** as duas leituras foram feitas pelo mesmo codificador. É um teste-reteste, não um teste de concordância entre codificadores independentes.

## 6. Limitações

1. **Viés de fonte.** 94% das reviews válidas de CA e 98% das de DE vêm do site da própria marca.
2. **Viés de nota.** 94% das reviews de CA e 83% das de DE são 5 estrelas, então as barreiras ficam sub-representadas.
3. **Campanha no site da CA.** O pico de nov–dez/2025 puxa o sabor para cima e energia, preço e barreiras para baixo. Use as colunas "sem o pico" e "fora do site".
4. **Desincoffee.** Só entram as 40 reviews mais recentes de cada página (o robots.txt impede paginar além disso), então não é uma amostra aleatória.
5. **Amostras pequenas.** BS (25) e UC (27) têm margem de ±20 p.p.; use só a ordem dos temas. VC e MC não têm dados.
6. **Margem de erro (95%):**

| Grupo | Margem |
|---|---|
| CA total | ±2,6 p.p. |
| DE total | ±4,8 p.p. |
| CA fora do site | ±10,6 p.p. |
| CA EUA | ±17 p.p. |
| BS e UC | ±20 p.p. |

7. **Marketplaces.** Ficaram de fora, exceto 33 linhas herdadas da v1. É lá que está o grosso das reviews das marcas menores.

## 7. Pipeline e reprodutibilidade

Os scripts estão em `scripts/` e rodam nesta ordem:

1. **Coleta:** `coleta_judgeme.py`, `coleta_loox_ssr.py`, `coleta_lojas_oficiais.py`, `coleta_varejo.py` e `coleta_mercadolivre.py`.
2. **`consolida.py`:** junta as fontes, deduplica e atribui IDs estáveis (`saida/trabalho/ids_v3.json`).
3. **`lotes.py`:** gera os lotes de reviews ainda não codificadas. A codificação de cada lote fica em `saida/trabalho/codificacao/`.
4. **`base_final.py`:** junta base e codificação e remove nomes e endereços.
5. **`validacao.py`:** calcula concordância e kappa.
6. **`monta_planilha.py`:** gera o xlsx. Em seguida, a planilha é recalculada com o LibreOffice.
7. **`confere.py`:** confere a planilha contra um recálculo independente. O resultado exigido é 0 erros e 0 divergências.
