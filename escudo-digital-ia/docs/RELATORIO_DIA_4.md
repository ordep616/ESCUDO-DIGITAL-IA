
# Relatório do Dia 4 — Avaliação e melhoria do prompt

## Objetivo do dia

Avaliar o comportamento da inteligência artificial usando os 30 casos fictícios, comparar as classificações esperadas com as obtidas, identificar os tipos de erro e preparar melhorias para uma segunda versão do prompt.

## Divisão de tarefas

### Atividades de Pedro

- implementar o carregamento e a validação dos casos de teste;
- executar os 30 casos utilizando o Prompt V1;
- comparar as classificações esperadas e obtidas;
- calcular acertos, falsos positivos, falsos negativos e respostas inválidas;
- salvar os resultados sem armazenar as mensagens integrais;
- preparar a comparação entre o Prompt V1 e o Prompt V2.

### Atividades do colaborador

- analisar os erros encontrados com o Prompt V1;
- criar o Prompt V2 sem apagar ou modificar o Prompt V1;
- explicar quais regras foram acrescentadas ou alteradas;
- disponibilizar o Prompt V2 para uma nova avaliação.


## Metodologia de avaliação

Os 30 casos fictícios de `data/casos_teste.json` possuem uma classificação esperada definida previamente. Cada mensagem foi analisada pela IA utilizando o Prompt V1.

O `evaluator.py` realizou as seguintes etapas:

1. carregou e validou os 30 casos;
2. enviou cada mensagem para o fluxo seguro de análise;
3. comparou a classificação obtida com a classificação esperada;
4. identificou acertos, falsos positivos, falsos negativos, outros erros de classificação e respostas inválidas;
5. calculou as métricas gerais;
6. salvou os resultados sem armazenar o conteúdo integral das mensagens.

Os resultados foram armazenados em `data/resultados_prompt_v1.json`.

## Resultados do Prompt V1

Foram executados 30 casos com chamadas reais à API.

- total de casos: 30;
- acertos: 26;
- erros: 4;
- taxa de acerto: 86,67%;
- falsos positivos: 1;
- falsos negativos: 0;
- respostas inválidas: 0;
- outros erros de classificação: 3.

A API retornou JSON válido em todos os 30 casos. Também foi verificado que o arquivo de resultados não contém as mensagens integrais analisadas.


## Erros encontrados no Prompt V1

| Caso | Classificação esperada | Classificação obtida | Tipo de resultado |
|---|---|---|---|
| caso_15 | moderado | informacao_insuficiente | erro de classificação |
| caso_20 | baixo_risco | moderado | falso positivo |
| caso_23 | baixo_risco | informacao_insuficiente | erro de classificação |
| caso_24 | baixo_risco | informacao_insuficiente | erro de classificação |

Não foram encontrados falsos negativos nem respostas com JSON inválido.

## Análise das possíveis causas

### caso_15

A mensagem apresenta uma oportunidade de trabalho sem identificar claramente a empresa ou fornecer detalhes da vaga. O Prompt V1 orientou o modelo a usar `informacao_insuficiente` para mensagens vagas. Entretanto, o pedido para responder a uma oportunidade não solicitada foi considerado suficiente na classificação manual para indicar risco moderado.

### caso_20

A mensagem informa que um pedido foi entregue e orienta o usuário a consultar o histórico diretamente no aplicativo usado para a compra. A IA possivelmente valorizou o tema de entrega como um sinal de risco e classificou como moderado. Como a mensagem recomenda o uso do aplicativo oficial e não pede dados, dinheiro ou acesso a links, a classificação esperada era `baixo_risco`.

### caso_23

A mensagem confirma uma inscrição e informa que o resultado será publicado no portal oficial. A ausência de um remetente identificado pode ter levado a IA a escolher `informacao_insuficiente`. Porém, não existe solicitação perigosa e a orientação para consultar um portal oficial reduz o risco.

### caso_24

A mensagem informa que um extrato está disponível e orienta a abertura do aplicativo oficial do banco. A IA tratou a falta de detalhes como informação insuficiente. Entretanto, não existe link, pedido de senha, código ou dado bancário, justificando a classificação esperada como `baixo_risco`.

## Hipótese geral

O Prompt V1 utiliza regras fortes para mensagens vagas, mas não explica claramente que orientações para consultar diretamente um aplicativo ou portal oficial são sinais de menor risco. Isso pode ter provocado o uso excessivo de `informacao_insuficiente`.

O Prompt V2 deverá melhorar essa distinção sem reduzir a segurança e sem transformar mensagens realmente suspeitas em baixo risco.


## Testes executados

A suíte completa de testes automáticos foi executada com:

```bash
poetry run python -m unittest discover -s tests -v
```

Foram executados 67 testes automáticos e todos passaram.

Os testes verificaram:

- comunicação e tratamento de erros da API;
- anonimização de dados pessoais;
- regras locais de segurança;
- validação da resposta estruturada;
- armazenamento seguro de consumo e avaliações;
- funcionamento do fluxo principal;
- carregamento dos casos;
- classificação dos resultados;
- cálculo das métricas;
- ausência das mensagens integrais no arquivo de resultados.

Os testes automáticos utilizam simulações e não realizam chamadas reais à API. As 30 chamadas reais foram feitas separadamente durante a avaliação do Prompt V1.

## Limitações identificadas

- As classificações podem variar entre chamadas da IA.
- Os resultados dependem do modelo utilizado e da qualidade do prompt.
- Mensagens curtas ou ambíguas podem receber classificações diferentes.
- O conjunto de avaliação possui somente 30 casos fictícios.
- A classificação esperada foi definida manualmente e também pode possuir subjetividade.
- A taxa de acerto não garante que o sistema reconhecerá todos os golpes reais.
- Não ocorreram falsos negativos nesta execução, mas eles podem acontecer em outros casos.
- O sistema possui finalidade educativa e não confirma se uma mensagem é legítima ou fraudulenta.
- Links não são abertos ou verificados pelo sistema.
- Informações importantes devem ser confirmadas diretamente por canais oficiais.

## Comparação entre Prompt V1 e Prompt V2

| Métrica | Prompt V1 | Prompt V2 |
|---|---:|---:|
| Total de casos | 30 | Pendente |
| Acertos | 26 | Pendente |
| Erros | 4 | Pendente |
| Taxa de acerto | 86,67% | Pendente |
| Falsos positivos | 1 | Pendente |
| Falsos negativos | 0 | Pendente |
| Respostas inválidas | 0 | Pendente |
| Outros erros | 3 | Pendente |

A coluna do Prompt V2 será preenchida depois que a nova versão for implementada e avaliada.
