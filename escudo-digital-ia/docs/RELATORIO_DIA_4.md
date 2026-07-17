
# Relatório do Dia 4 — Avaliação e melhoria do prompt

> Status: concluído. O Prompt V1, o primeiro Prompt V2 e o Prompt V2 revisado
> foram avaliados. A versão revisada obteve 28 acertos em 30 casos, sem falsos
> negativos e sem respostas inválidas.

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
- disponibilizar o Prompt V2 para uma nova avaliação;
- revisar o Prompt V2 após as regressões encontradas na primeira avaliação.


## Metodologia de avaliação

Os 30 casos fictícios de `data/casos_teste.json` possuem uma classificação
esperada definida previamente. Cada mensagem foi analisada pela IA com o Prompt
V1 e, posteriormente, com as versões inicial e revisada do Prompt V2.

O `evaluator.py` realizou as seguintes etapas:

1. carregou e validou os 30 casos;
2. enviou cada mensagem para o fluxo seguro de análise;
3. comparou a classificação obtida com a classificação esperada;
4. identificou acertos, falsos positivos, falsos negativos, outros erros de classificação e respostas inválidas;
5. calculou as métricas gerais;
6. salvou os resultados sem armazenar o conteúdo integral das mensagens.

Os resultados finais foram armazenados separadamente em
`data/resultados_prompt_v1.json` e `data/resultados_prompt_v2.json`.

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

Após a integração do Prompt V2 revisado, foram executados 94 testes automáticos
e todos passaram.

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

Os testes automáticos utilizam simulações e não realizam chamadas reais à API.
As chamadas reais foram feitas separadamente durante as avaliações dos prompts.

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

## Primeira avaliação do Prompt V2

O primeiro Prompt V2 corrigiu os quatro erros encontrados no Prompt V1. Os
casos `caso_15`, `caso_20`, `caso_23` e `caso_24` acertaram quando foram
executados isoladamente. Uma amostra de cinco casos que já funcionavam também
permaneceu correta.

Entretanto, a nova execução dos 30 casos revelou quatro regressões:

| Caso | Classificação esperada | Classificação obtida | Tipo de resultado |
|---|---|---|---|
| caso_13 | moderado | baixo_risco | erro de classificação |
| caso_14 | moderado | baixo_risco | erro de classificação |
| caso_16 | moderado | informacao_insuficiente | erro de classificação |
| caso_27 | informacao_insuficiente | moderado | erro de classificação |

As métricas da primeira avaliação do Prompt V2 foram:

- total de casos: 30;
- acertos: 26;
- erros: 4;
- taxa de acerto: 86,67%;
- falsos positivos: 0;
- falsos negativos: 0;
- respostas inválidas: 0;
- outros erros de classificação: 4.

A regra relacionada a canais oficiais ficou forte demais e reduziu o risco de
algumas situações concretas. Ao mesmo tempo, uma mensagem vaga sobre a
confirmação de um pedido foi elevada para risco moderado. Assim, o primeiro
Prompt V2 alterou quais casos falharam, mas não melhorou a taxa geral de acerto.

Essas regressões foram encaminhadas ao colaborador. A revisão seguinte tornou
explícita a diferença entre situações concretas que precisam ser verificadas,
confirmações legítimas concluídas e mensagens genéricas sem contexto.

## Avaliação do Prompt V2 revisado

Antes da execução completa, foram repetidos os oito casos diretamente afetados
pelas duas versões do Prompt V2:

- `caso_13`;
- `caso_14`;
- `caso_15`;
- `caso_16`;
- `caso_20`;
- `caso_23`;
- `caso_24`;
- `caso_27`.

Os oito casos acertaram nessa execução isolada, com JSON válido. Em seguida, os
30 casos foram executados novamente. O resultado final foi:

- total de casos: 30;
- acertos: 28;
- erros: 2;
- taxa de acerto: 93,33%;
- falsos positivos: 1;
- falsos negativos: 0;
- respostas inválidas: 0;
- outros erros de classificação: 1.

Os dois erros finais foram:

| Caso | Classificação esperada | Classificação obtida | Tipo de resultado |
|---|---|---|---|
| caso_12 | moderado | informacao_insuficiente | erro de classificação |
| caso_24 | baixo_risco | moderado | falso positivo |

O `caso_12` descreve uma atualização de cadastro sem identificar claramente o
remetente. O modelo valorizou a falta de contexto e escolheu
`informacao_insuficiente`, enquanto a classificação manual considerou a
possível consequência e definiu risco moderado.

O `caso_24` informa que um extrato está disponível e recomenda consultar o
aplicativo oficial. Ele acertou como `baixo_risco` na execução isolada, mas foi
classificado como `moderado` na execução completa. Essa diferença demonstra que
modelos generativos podem variar entre chamadas mesmo quando mensagem, prompt e
modelo permanecem iguais.

Foi confirmado que `data/resultados_prompt_v2.json` contém exatamente 30
resultados e não armazena o campo `mensagem` nem o texto integral dos casos.

## Comparação final entre Prompt V1 e Prompt V2

| Métrica | Prompt V1 | Prompt V2 |
|---|---:|---:|
| Total de casos | 30 | 30 |
| Acertos | 26 | 28 |
| Erros | 4 | 2 |
| Taxa de acerto | 86,67% | 93,33% |
| Falsos positivos | 1 | 1 |
| Falsos negativos | 0 | 0 |
| Respostas inválidas | 0 | 0 |
| Outros erros | 3 | 1 |

O Prompt V2 revisado aumentou a taxa de acerto em 6,66 pontos percentuais e
reduziu a quantidade total de erros de quatro para dois. O número de falsos
positivos permaneceu em um, e nenhuma das versões apresentou falso negativo ou
resposta inválida nessa avaliação.

Os casos `caso_15`, `caso_20` e `caso_23`, que falharam no V1, foram corrigidos
na execução completa do V2 revisado. O `caso_24` continuou divergente, embora
tenha mudado de `informacao_insuficiente` para `moderado` e tenha acertado na
execução isolada. O `caso_12`, que acertava anteriormente, tornou-se um novo
erro de classificação.

## Decisões tomadas pela dupla

- preservar o Prompt V1 para permitir uma comparação verificável;
- revisar somente as regras responsáveis pelos erros, sem reescrever o prompt
  inteiro;
- testar primeiro os oito casos afetados antes de consumir 30 novas chamadas;
- aceitar o resultado completo de 28 acertos como evidência final, sem repetir
  chamadas apenas para buscar uma pontuação melhor;
- documentar a variação do `caso_24` como limitação real da IA;
- priorizar a ausência de falsos negativos e respostas inválidas;
- manter mensagens integrais fora dos arquivos de resultados.

## Como a API de IA foi utilizada

A API do OpenRouter foi utilizada somente com mensagens fictícias e após as
camadas locais de segurança e anonimização. O avaliador solicitou resposta
estruturada, validou os campos e registrou apenas classificações e métricas. As
oito chamadas de verificação foram realizadas antes das 30 chamadas da
avaliação final.

## Como o Codex foi utilizado

O Codex foi utilizado para revisar os resultados, comparar as versões do
prompt, conferir a ausência de mensagens integrais, executar os testes e
organizar a documentação. As classificações esperadas permaneceram as que
haviam sido definidas manualmente antes das consultas à IA.

## Conclusão

O Dia 4 foi concluído com uma comparação mensurável entre os prompts. O Prompt
V2 revisado apresentou melhora de 86,67% para 93,33%, manteve zero falsos
negativos e reduziu os outros erros de classificação. Os dois erros restantes e
a variação observada no `caso_24` foram preservados no relatório para evitar a
impressão de que a ferramenta possui comportamento determinístico ou garante
uma classificação correta.

## Evidências

- `data/resultados_prompt_v1.json` com 30 resultados do Prompt V1;
- `data/resultados_prompt_v2.json` com 30 resultados do Prompt V2 revisado;
- 94 testes automáticos aprovados;
- oito casos afetados aprovados na execução isolada;
- 30 casos executados na avaliação final;
- Prompt V1 preservado em `prompts.py`;
- revisão do Prompt V2 integrada pelo commit do colaborador `8dfd315`.
