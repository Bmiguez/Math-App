# Handover: coleta de reviews de café funcional (sessão 2 → sessão 3)

Data: 04/11/2026 · Branch: `claude/inspiring-fermi-jfpt01` · Repositório: `bmiguez/math-app`

## 1. Como começar a sessão nova (para a usuária)

1. **GitHub:** o código já está no branch `claude/inspiring-fermi-jfpt01` (push feito em 04/11). Abra a sessão nova nesse branch.
2. **Mercado Livre (opcional):** siga `passo_a_passo_mercado_livre_v1.md` e grave `ML_CLIENT_ID` e `ML_CLIENT_SECRET` nas variáveis do ambiente. Libere também `api.mercadolibre.com` na rede do ambiente.
3. **Abra a sessão nova** no mesmo repositório e anexe:
   - **`pacote_nova_sessao_v1.zip`**: obrigatório. Traz os dados brutos e a base de trabalho, que ficam fora do Git por privacidade, e um bundle do código como reserva.
   - **Este arquivo**: `handover_coleta_reviews_v2.md`.
4. **Primeira mensagem sugerida:**
   > Leia o handover anexo e restaure o trabalho a partir do pacote. Depois: [escolha a tarefa, por exemplo "colete o Mercado Livre e gere a v4"].

## 2. Restauração (para o Claude da sessão nova)

O código está no GitHub (commit `4b55c7b` ou posterior): faça checkout do branch e copie `bruto/` e `trabalho/` do pacote. As linhas `git fetch` do bundle só são necessárias se o branch não estiver no GitHub.

```bash
mkdir -p /tmp/pacote && cd /tmp/pacote && unzip -q <caminho_do_anexo>/pacote_nova_sessao_v1.zip
cd /home/user/<repo>
git fetch /tmp/pacote/repositorio_math-app.bundle claude/inspiring-fermi-jfpt01:claude/inspiring-fermi-jfpt01
git checkout claude/inspiring-fermi-jfpt01
cp -r /tmp/pacote/bruto saida/
cp -r /tmp/pacote/trabalho/* saida/trabalho/
python scripts/confere.py saida/reviews_cafe_funcional_v3.xlsx   # tem que sair 0 erros / 0 divergências
```

Na sessão 2 o push deu 403 várias vezes antes de funcionar. Se voltar a dar 403, entregue um bundle como reserva.

## 3. Estado atual

**Última entrega:**
- `saida/reviews_cafe_funcional_v3.xlsx`, com 10 abas:
  - LEIA-ME
  - Resultados (19 grupos)
  - Comparacao_v1
  - Base_reviews
  - Textos
  - Livro_de_codigos
  - Cobertura
  - Reclame_Aqui
  - Formulario_CA
  - Validacao
- `saida/resumo_reviews_v3.md`

**Resultados v3 (n válido):**

| Marca | Prefixo do ID | n | Destaques |
|---|---|---|---|
| SuperCoffee (Caffeine Army) | CA | 1.417 | Sabor 89%, praticidade 24%. Fora do site (n=86): energia 48%, preço 6% |
| Desincoffee (Desinchá) | DE | 421 | Sabor 49%, hábito 27%. Barreira: sabor 11% |
| Brainstorm (Essential) | BS | 25 | Energia 52%, foco 32%. Barreira: sabor 16% |
| Ultracoffee (3corações) | UC | 27 | Sabor 52%, energia 33%. Barreira: preço 11% |
| V-Coffee (Vitafor) | VC | 0 | Nenhuma fonte acessível com reviews |
| Mega Coffee (Allure) | MC | 0 | Site com erro 403; varejo sem reviews |

**Fontes já coletadas:**

| Fonte | Coletor | Observação |
|---|---|---|
| Site Caffeine Army (Judge.me) | `scripts/coleta_judgeme.py` | |
| Site Desinchá (Loox SSR) | `scripts/coleta_loox_ssr.py` | |
| Essential (JSON-LD) | `scripts/coleta_lojas_oficiais.py` | 22 reviews |
| Mercafé (HTML) | `scripts/coleta_lojas_oficiais.py` | 14 reviews |
| Vitafor | `scripts/coleta_lojas_oficiais.py` | 0 reviews |
| Drogaria SP, Pacheco, Americanas (Konfidency) | `scripts/coleta_varejo.py` | Total do varejo: 35 reviews |
| Pague Menos, Drogal (Yourviews GraphQL) | `scripts/coleta_varejo.py` | Total do varejo: 35 reviews |
| Home Tester Club | — | Em `saida/bruto/hometesterclub/`; mostra 10 reviews por produto |
| Magalu, Amazon (via Buscapé/Zoom), Mercado Livre | — | 33 linhas herdadas da v1, só com paráfrase |

**Pipeline** (rodar nesta ordem; todos os scripts estão em `scripts/`):

1. `consolida.py`: junta os brutos, deduplica e gera `saida/trabalho/base_consolidada.json`. Os IDs estáveis vêm de `ids_v2.json`.
2. `lotes.py`: gera lotes com as reviews ainda não codificadas, em `saida/trabalho/lotes/`.
3. Codificação manual: um arquivo por lote em `saida/trabalho/codificacao/*.json`, no formato `{"id","c":[códigos],"inc":0/1,"obs"}`.
4. `base_final.py`: junta a codificação, redige nomes e endereços e herda as linhas da v1. Gera `base_final.json`.
5. `validacao.py` → `monta_planilha.py`:
   - O xlsx é recalculado com `soffice --headless --calc --convert-to xlsx`.
   - Em seguida roda `confere.py`, que tem que dar 0 erros e 0 divergências.

**Livro de códigos:** 28 códigos ao todo.
- 15 motivos: ENE, SAB, HAB, FOC, TRE, SEF, TEX, PRA, SAU, SUB, COR, CB, ENT, IND, GER.
- 11 barreiras: nPRE, nSAB, nEFE, nENT, nPED, nREN, nTEX, nOUT, nDIS, nATE, nING.
- 2 neutros: CON, ASS.
- Os rótulos estão em `base_final.py` e em `saida/trabalho/codigos.json`.

**Deduplicação** (em `consolida.py`), por quatro critérios:
- `ID_origem`;
- texto + data/hora + nota + hash do autor, que remove as cópias do Loox entre produtos;
- mesmo autor + mesmo texto;
- quase-duplicatas marcadas à mão.

## 4. Pendências, por prioridade

1. **Mercado Livre via API oficial:**
   - Use a variável de ambiente `ML_CLIENT_ID`/`ML_CLIENT_SECRET` (token do app). Se o endpoint `/reviews/item/{id}` recusar esse token, peça à usuária a Etapa 3 do passo a passo, que gera `ML_ACCESS_TOKEN`, válido por 6 horas.
   - Busca de anúncios: `/sites/MLB/search?q=` para as 6 marcas, com o mesmo filtro de marca de `coleta_varejo.py`.
   - Escreva um coletor novo, `scripts/coleta_mercadolivre.py`, com saída em `saida/bruto/mercadolivre/`.
   - Os IDs são prefixados por marca e continuam a numeração de `ids_v2.json`.
   - Integre ao `consolida.py` como fonte nova, `Tipo_fonte = 'Marketplace independente'`. Ao entrar dado novo do Mercado Livre, substitua as linhas herdadas da v1 com fonte "Mercado Livre".
2. **Amazon, Magalu e Reclame Aqui:** só por páginas que a usuária salvar no navegador (Ctrl+S, "Página completa") e anexar. A aba Reclame_Aqui ainda tem a contagem da v1, de 03/11.
3. **Recodificação cega das 68 reviews novas da v3** (BS 25, UC 27, CA 13, DE 3). A validação atual (kappa) cobre só CA e DE.
4. **Próxima entrega:** `saida/reviews_cafe_funcional_v4.xlsx` e `saida/resumo_reviews_v4.md`, no mesmo formato da v3. Não sobrescrever v2 nem v3.

## 5. Regras que valem para a sessão nova

- **Coleta:**
  - Respeitar o `robots.txt` e os termos de uso de cada site.
  - No máximo 1 requisição por segundo.
  - Não contornar CAPTCHA, login de terceiros nem bloqueios. Registrar cada bloqueio na aba Cobertura.
  - Preferir API oficial quando houver.
- **Privacidade:**
  - Sem nome nem foto de autor na base de análise. Usar IDs pseudônimos.
  - Texto bruto só em `saida/bruto/`, que fica fora do Git (ver `.gitignore`).
  - Remover e-mail, IP e ID de usuário já na coleta.
- **Credenciais:** nunca pedir chave ou token no chat. Elas entram só como variáveis do ambiente.
- **Pastas e versões:**
  - `entrada/` nunca é editada. Tudo o que for produzido vai para `saida/`.
  - Versões `_v1`, `_v2`…; uma versão já entregue nunca é sobrescrita.
- **Usuária:** responder em português, de forma direta, com a conclusão primeiro. Em tarefas complexas, listar o plano e os riscos antes de executar.
