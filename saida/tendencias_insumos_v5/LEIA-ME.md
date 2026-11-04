# Insumos da revisão v5 (04/11/2026)

- `rows.json`: 95 players da aba "Tendências por player" da v4, com Formato/Proposta/Observações/Site da aba Concorrentes.
- `fetch.py`: baixa a home, o catálogo Shopify (`/products.json`) e a página-fonte de cada player → `web.json`.
- `web.json`: snapshot do que foi baixado em 04/11/2026 (evidência das flags e do status).
- `build_v5.py`: aplica as correções (dicionário `C`), os status (dicionários `S`/`SP`), cria a aba "Revisão v5" e o bloco de status no Resumo.

```bash
python3 build_v5.py ../../entrada/Mapa_Concorrentes_SuperCoffee_v4.xlsx ../Mapa_Concorrentes_SuperCoffee_v5.xlsx web.json
```
