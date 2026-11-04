# Reviews de café funcional: 6 marcas (v4)

04/11/2026 · base: `reviews_cafe_funcional_v4.xlsx` · 1.890 reviews válidas

## Conclusão

**Os resultados são os mesmos da v3.** A v4 não acrescenta reviews. O que ela muda:
- a codificação das 4 marcas está validada;
- o Mercado Livre está documentado como fonte fechada.

Continue usando só a ordem dos temas dentro de cada marca.

| Marca | n válido | Principais motivos | Principal barreira |
|---|---|---|---|
| SuperCoffee (Caffeine Army) | 1.417 | Sabor 89%, praticidade 24%, energia 14% (fora do site: energia 48%, sabor 55%, hábito 28%) | Sabor descontinuado/indisponível; preço só fora do site (6%) |
| Desincoffee (Desinchá) | 421 | Sabor 49%, hábito 27%, elogio genérico 25%, energia 18% | Sabor: doce, adoçante, artificial (11%) |
| Brainstorm (Essential) | 25 | Energia 52%, sabor 48%, foco 32%, treino 28% | Sabor: doce demais ou mudou (16%) |
| Ultracoffee (3corações) | 27 | Sabor 52%, energia 33%, treino 22%, saudável 19% | Preço (11%) |
| V-Coffee (Vitafor) | 0 | — | — |
| Mega Coffee (Allure) | 0 | — | — |

## O que mudou em relação à v3

- **Recodificação cega das 68 reviews novas da v3** (BS 25, UC 27, CA 13, DE 3):
  - a inclusão bateu em 67 de 68;
  - os códigos ficaram idênticos em 51 de 68.
- **Concordância por código nas duas rodadas juntas** (306 reviews): ficou ≥ 96% em todos os códigos. O mais instável continua sendo praticidade (kappa 0,87).
- **Divergências da rodada nova:**
  - Em Brainstorm, a energia apareceu só na recodificação em 2 casos. Se a recodificação estiver certa, a energia passaria de 52% para 60% e reforçaria a leitura "função antes de sabor".
  - Hábito divergiu nos dois sentidos (3 casos), assim como CB, GER e PRA em casos limítrofes.
  - A codificação original foi mantida, como na v3: a recodificação mede a estabilidade e não altera os códigos.
- **Mercado Livre via API oficial: não dá.**
  - A busca no catálogo funciona: são 497 produtos das marcas, 182 com anúncio ativo, incluindo os 3 primeiros produtos de V-Coffee encontrados.
  - Já o endpoint de opiniões responde 403 com token de app e também com token de usuário (OAuth). A API não libera opiniões de anúncios de terceiros.
  - O detalhe está na aba Cobertura.

## Lacunas

- **V-Coffee e Mega Coffee continuam com zero reviews.** Brainstorm e Ultracoffee continuam com n abaixo de 30.
- **Os marketplaces seguem fora**, exceto as 33 linhas herdadas da v1:
  - Mercado Livre: sem API para opiniões, e o robots.txt bloqueia agentes;
  - Amazon e Magalu: bloqueiam agentes.
  - Única via restante: páginas salvas no navegador, uma por produto.
- **A aba Reclame_Aqui ainda tem as contagens da v1** (03/11).
