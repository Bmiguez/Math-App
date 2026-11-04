# Reviews de café funcional: Caffeine Army x Desincoffee (v2)

04/11/2026 · base: `reviews_cafe_funcional_v2.xlsx`

## Conclusão

1. **Caffeine Army.** Quem compra pelo site fala de **sabor** (89% das reviews). Fora do site, o que se destaca é **energia** (53%), junto com **hábito** (30%), **treino** (21%) e **foco** (16%).
   - A principal barreira **não é preço**. Fora do pico de campanha, o que aparece é a **descontinuação de sabores** (10%, principalmente Beijinho e Chocolate) e **sabor de lançamento abaixo do esperado** (15%; 12 dos 19 casos são do Pistache).
   - **Preço** só aparece fora do site (7%).
2. **Desincoffee.** O perfil é estável em relação à v1:
   - motivos: sabor (49%), hábito (27%), elogio genérico (25%) e energia (18%);
   - barreira principal: **sabor** (11,5%), com queixas de doce demais, adoçante, artificial e "gosto de remédio".
3. **Comparação entre marcas.** Só vale comparar a **ordem dos temas**, não o percentual absoluto. As duas bases agora vêm quase só do site da própria marca: CA 95%, DE 99%.

## O que mudou em relação à v1

- **Volume de reviews válidas:** de 258 para 1.822 (CA de 66 para 1.404; DE de 192 para 418).
- **Caffeine Army:** 9 temas mudaram mais de 10 p.p.
  - Os maiores: ENE caiu de 53% para 14%, SAB subiu de 65% para 89%, SEF caiu de 15% para 2%, PRA subiu de 11% para 25%.
  - **A causa é a mudança de fonte, não de opinião.** A v1 era Thingtesting e Magalu. A v2 é o site da marca, onde 91% das reviews foram publicadas em nov–dez/2025 no formato "ranking de sabores", com cara de campanha de avaliação.
  - Fora do site (n = 73), os percentuais ficam próximos da v1.
- **Desincoffee:** nenhum tema mudou mais de 10 p.p.
- **Codificação:** os 24 códigos da v1 foram mantidos e entraram 4 novos.
  - **nDIS:** sabor indisponível ou descontinuado (1,4% CA; 9,8% no site da CA fora do pico).
  - **nATE:** atendimento ruim.
  - **nING:** crítica a ingrediente.
  - **ASS:** menciona a assinatura Prime. Inclui queixas de sabores exclusivos de assinante.
- **Achado novo, formulário do site da CA** (1.285 respostas):
  - objetivo de consumo: exercício 70%, autocuidado 63%, trabalho 42%, estudos 28%;
  - 62% têm de 25 a 34 anos;
  - 99% recomendariam o produto.

## Limitações

- **Marketplaces bloquearam e ficaram fora.** No Mercado Livre e na Amazon/Buscapé/Zoom, o robots.txt veta agentes Claude. Magalu, Drogasil/Raia/Panvel e Reclame Aqui responderam HTTP 403. Entraram apenas 33 linhas herdadas da v1.
  - Por isso, a pergunta "o Desincoffee só parece melhor por vir do próprio site?" **segue sem resposta**: o Desincoffee tem n = 4 fora do site.
- **Desincoffee, cobertura parcial:** cerca de 9% do volume anunciado. O robots.txt do Loox proíbe o endpoint paginado, então só entraram as 40 reviews mais recentes de cada página. A amostra não é aleatória nem estratificada por nota.
- **Viés positivo nas duas bases:** 94% (CA) e 83% (DE) das reviews são 5 estrelas, então as barreiras ficam subestimadas. O Reclame Aqui continua sendo a melhor fonte de barreiras de entrega. Os números daquela aba são de 03/11, sem atualização.
- **Validação da codificação:** recodificação cega de 238 reviews, com concordância ≥ 95,7% em todos os códigos (kappa mínimo de 0,72, em COR). Foi o mesmo codificador, ou seja, um teste-reteste e não um segundo codificador independente.
- **Próximo passo para fechar a lacuna:** exportar as avaliações do Mercado Livre e do Reclame Aqui pelo navegador de uma pessoa e rodar o mesmo pipeline (`scripts/`).
