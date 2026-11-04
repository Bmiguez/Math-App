# Reviews de café funcional: 6 marcas (v3)

04/11/2026 · base: `reviews_cafe_funcional_v3.xlsx` · 1.890 reviews válidas

## Conclusão

**Use só a ordem dos temas dentro de cada marca.** As bases vêm de fontes diferentes, quase sempre o site da própria marca, e as marcas novas têm n pequeno (margem de ±20 p.p.).

| Marca | n válido | Principais motivos | Principal barreira |
|---|---|---|---|
| SuperCoffee (Caffeine Army) | 1.417 | Sabor 89%, praticidade 24%, energia 14% (fora do site: energia 48%, sabor 55%, hábito 28%) | Sabor descontinuado/indisponível; preço só fora do site (6%) |
| Desincoffee (Desinchá) | 421 | Sabor 49%, hábito 27%, elogio genérico 25%, energia 18% | Sabor: doce, adoçante, artificial (11%) |
| Brainstorm (Essential) | 25 | Energia 52%, sabor 48%, foco 32%, treino 28% | Sabor: doce demais ou mudou (16%) |
| Ultracoffee (3corações) | 27 | Sabor 52%, energia 33%, treino 22%, saudável 19% | Preço (11%) |
| V-Coffee (Vitafor) | 0 | — | — |
| Mega Coffee (Allure) | 0 | — | — |

- **Brainstorm e Ultracoffee são lembrados mais pela função** (energia, foco, treino) do que pelo sabor. Na Caffeine Army, o sabor domina por causa da campanha de reviews de nov–dez/2025 no site dela.
- **No Brainstorm, foco aparece em 32% das reviews** e "sem taquicardia ou sem pico" também aparece, o que bate com o posicionamento "brain" da marca.
- **Preço pesa mais no Ultracoffee (11%)** do que nas demais. Na Caffeine Army, por exemplo, ele só aparece fora do site (6%). Quem reclama de preço no Ultracoffee chama o produto de "salgado" ou "um pouco carinho".

## O que mudou em relação à v2

- **Marcas novas:** entraram Brainstorm, Ultracoffee, V-Coffee e Mega Coffee.
- **Lojas novas:** Drogarias Pacheco, Americanas, Pague Menos, Drogal, Mercafé (a loja do Grupo 3corações) e o site da Essential.
- **A v2 ficou intacta:** nenhuma linha nem código mudou, e os IDs foram preservados. A Caffeine Army ganhou 13 reviews de varejo (fora do site, n passou de 73 para 86) e o Desincoffee ganhou 3.

## Lacunas

- **V-Coffee e Mega Coffee ficaram com zero reviews.** O site da Vitafor não tem nenhuma publicada, o da Allure bloqueia acesso automático (erro 403) e as farmácias acessíveis não têm avaliações desses produtos.
- **O grosso das reviews das 4 marcas novas está no Mercado Livre e na Amazon**, que bloqueiam agentes automáticos. Para fechar essa lacuna:
  - **Mercado Livre:** API oficial com credencial sua, gravada nas variáveis do ambiente (`ML_CLIENT_ID`, `ML_CLIENT_SECRET`).
  - **Amazon, Magalu e Reclame Aqui:** páginas salvas no seu navegador e anexadas no chat.
- **As 68 reviews novas não passaram por recodificação cega.** A validação de 10% vale para CA e DE.
