# Passo a passo: liberar a coleta de avaliações do Mercado Livre

Objetivo: permitir que o Claude Code na nuvem leia as opiniões públicas dos produtos das 6 marcas pela API oficial do Mercado Livre.

**Regra de segurança:** nenhuma chave, token ou código vai no chat. Tudo fica nas variáveis do ambiente da nuvem.

Tempo estimado: 15 minutos.

---

## Etapa 0. Reconectar o GitHub (2 min)

Sem isso, a sessão nova não recebe o trabalho da v3.

1. Acesse https://claude.ai/connect-github e reconecte sua conta.
2. Se aparecer a pergunta sobre o repositório, autorize o app do Claude no repositório `bmiguez/math-app`. Página de instalação: https://github.com/apps/claude/installations/select_target
3. Volte a esta sessão e me avise. Eu envio os commits da v3 para o GitHub.

---

## Etapa 1. Criar o app no Mercado Livre (5 min)

1. Abra o portal de desenvolvedores: https://developers.mercadolivre.com.br
2. Clique em **Entrar** (canto superior direito) e use sua conta normal do Mercado Livre.
   - Se o portal pedir validação de dados (CPF, telefone, e-mail), complete.
   - A documentação recomenda usar a conta do dono da solução. Para pesquisa, sua conta pessoal serve.
3. Abra **Minhas aplicações** (no menu do seu perfil). Link direto: https://developers.mercadolivre.com.br/devcenter
4. Clique em **Criar uma aplicação** e preencha:

| Campo | O que colocar |
|---|---|
| Nome | `pesquisa-reviews-cafe` (precisa ser único; se já existir, acrescente um número) |
| Nome curto | `pesquisareviews` |
| Descrição | `Leitura de avaliações públicas de produtos para pesquisa de mercado` |
| Logo | opcional |
| URIs de redirect | `https://www.google.com` (precisa ser https; o endereço não importa) |
| PKCE | deixe desmarcado |
| Unidade de negócio | Mercado Livre |
| Escopos | marque **Leitura** (read). Não marque escrita (write) |
| Tópicos | nenhum |
| URL de retorno de notificações | deixe em branco; se for obrigatória, use `https://www.google.com` |

5. Aceite os termos e clique em **Criar**.
6. Você volta para **Minhas aplicações**. Na linha do app aparecem dois valores. Deixe essa aba aberta:
   - **App ID / Client ID**: um número com cerca de 16 dígitos.
   - **Chave secreta / Client Secret**: uma sequência de letras e números.

Documentação oficial desta etapa: https://developers.mercadolivre.com.br/pt-br/crie-uma-aplicacao-no-mercado-livre

---

## Etapa 2. Gravar as credenciais no ambiente da nuvem (3 min)

1. No Claude Code (web ou app), no topo da sessão, clique no **nome do ambiente** e depois em **Edit**.
   - Se não achar: em claude.ai/code, abra as configurações do ambiente que esta sessão usa.
2. No campo de **variáveis de ambiente**, adicione duas linhas, trocando pelos valores da Etapa 1:

```
ML_CLIENT_ID=coloque_aqui_o_app_id
ML_CLIENT_SECRET=coloque_aqui_a_chave_secreta
```

3. **Salve.**
4. Confira se a política de rede do ambiente libera `api.mercadolibre.com`. Se ela estiver em lista de domínios permitidos, inclua esse domínio.
5. Abra uma **sessão nova** nesse ambiente. As variáveis só valem em sessões criadas depois de salvas.
6. Na sessão nova, escreva: *"Continue a coleta do Mercado Livre da v3 (handover em saida/resumo_reviews_v3.md)."*

---

## Etapa 3. Só se eu pedir: gerar um token de usuário (5 min)

Faça esta etapa **apenas se, na sessão nova, eu disser que o token do app não bastou**. A API de opiniões (`/reviews/item/{id}`) exige token, e a documentação não deixa claro se o token gerado só pelo app é aceito.

O token de usuário vale por 6 horas. Por isso, faça a etapa e abra a sessão logo em seguida.

1. **Autorize o app.** No navegador, abra o link abaixo, trocando `SEU_APP_ID` pelo número da Etapa 1:

```
https://auth.mercadolivre.com.br/authorization?response_type=code&client_id=SEU_APP_ID&redirect_uri=https://www.google.com
```

2. Faça login se for pedido e clique em **Permitir**.
3. **Copie o código.** O navegador vai abrir o Google com um endereço assim:
   `https://www.google.com/?code=TG-xxxxxxxxxxxxxxxx-123456`
   Copie só a parte depois de `code=`, que começa com `TG-`. O código expira em cerca de 10 minutos e só pode ser usado uma vez.
4. **Troque o código pelo token no seu computador.** Não faça isso no chat.
   - **Windows:** abra o *Prompt de Comando*. Digite `cmd` no menu Iniciar.
   - **Mac:** abra o *Terminal*.

   Cole o comando abaixo em uma linha só, trocando os três valores:

```
curl.exe -X POST https://api.mercadolibre.com/oauth/token -H "content-type: application/x-www-form-urlencoded" -d "grant_type=authorization_code&client_id=SEU_APP_ID&client_secret=SUA_CHAVE&code=TG-SEU_CODIGO&redirect_uri=https://www.google.com"
```

   No Mac, troque `curl.exe` por `curl`.

5. A resposta traz um trecho `"access_token":"APP_USR-..."`. Copie o valor entre aspas, que começa com `APP_USR-`.
6. **Grave o token no ambiente.** Volte ao **Edit** do ambiente (Etapa 2), adicione a linha abaixo, salve e abra uma sessão nova:

```
ML_ACCESS_TOKEN=APP_USR-...
```

Documentação oficial: https://developers.mercadolivre.com.br/obtencao-do-access-token

---

## O que eu faço depois, na sessão nova

- Busco os anúncios das 6 marcas (SuperCoffee, Desincoffee, Brainstorm, Ultracoffee, V-Coffee e Mega Coffee) e leio as opiniões pela API oficial: https://developers.mercadolivre.com.br/pt_br/Opinioes-sobre-um-produto
  - Os campos disponíveis são nota, título, texto e datas.
  - O autor já vem anonimizado pela própria API.
- Mantenho até 1 requisição por segundo, deduplico, codifico com o mesmo livro de códigos e entrego `reviews_cafe_funcional_v4.xlsx` no mesmo formato da v3.

## Depois da coleta (opcional)

- Para encerrar o acesso, apague o app em **Minhas aplicações** ou renove a chave secreta.
- Remova as variáveis `ML_*` do ambiente.
