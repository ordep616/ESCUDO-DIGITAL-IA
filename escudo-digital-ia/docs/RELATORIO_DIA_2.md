# Relatório — Dia 2

## Objetivo do dia

O objetivo do segundo dia foi preparar a integração com a API de inteligência
artificial, definir uma resposta estruturada e validável, proteger a chave de
acesso, registrar métricas básicas de consumo e verificar o comportamento do
sistema com mensagens fictícias de diferentes níveis de risco.

## Divisão das tarefas

As tarefas foram divididas entre os dois integrantes para evitar alterações
simultâneas nos mesmos arquivos.
pedro fez a configuração da chave, o serviço de IA, a resposta em JSON, os cinco testes reais e o armazenamento em SQLite.

Enrico configurou o Poetry, criou o prompt, fez o validador e conectou o registro de consumo ao programa.

Juntos, vocês corrigiram erros do prompt, testaram o sistema e organizaram os commits no GitHub.

### Parte de Pedro

- criar e revisar `.env.example` e `.gitignore` antes de utilizar a chave real;
- implementar `ai_service.py` com tratamento de timeout, autenticação e
  indisponibilidade;
- solicitar uma resposta estruturada em JSON;
- executar pelo menos cinco casos fictícios no terminal;
- integrar e revisar o registro de consumo sem armazenar as mensagens.

### Parte do enrico

- configurar o ambiente e as dependências com Poetry;
- criar a primeira versão do prompt em `prompts.py`;
- implementar `validator.py` para detectar campos ausentes, tipos incorretos e
  valores inválidos;
- criar o registro inicial de quantidade de chamadas e tamanho aproximado das
  entradas;
- integrar o registro de consumo ao fluxo principal e simular essa dependência
  nos testes.

## O que foi concluído

- ambiente configurado com Python 3.11 ou superior e Poetry;
- dependências declaradas em `pyproject.toml` e `poetry.lock`;
- `.env.example` criado sem chave verdadeira;
- `.env` protegido pelo `.gitignore`;
- integração com o OpenRouter por meio do SDK da OpenAI;
- tratamento específico para timeout, falha de autenticação, conexão,
  indisponibilidade e resposta vazia;
- prompt de análise de risco criado e refinado;
- resposta estruturada com JSON Schema;
- validação dos seis campos obrigatórios da resposta;
- execução de cinco casos fictícios com chamadas reais;
- registro de chamadas, caracteres e tokens aproximados sem salvar o texto;
- integração do registro de consumo ao fluxo principal após a chamada à API;
- armazenamento local das métricas em SQLite, com o banco protegido pelo Git;
- testes automatizados para API, prompt, validação, privacidade, interface,
  fluxo principal e armazenamento.

## Formato estruturado utilizado

A resposta da IA deve conter obrigatoriamente:

- `classificacao`;
- `confianca`;
- `sinais`;
- `recomendacoes`;
- `explicacao_simples`;
- `informacao_insuficiente`.

As classificações permitidas são `baixo_risco`, `moderado`, `alto_risco` e
`informacao_insuficiente`. A confiança deve ser numérica e estar entre 0 e 1.

## Testes executados e resultados

Foram escolhidos cinco casos do conjunto de 30 mensagens fictícias:

| Caso | Classificação esperada | Resultado final |
| --- | --- | --- |
| `caso_01` | `alto_risco` | acerto |
| `caso_11` | `moderado` | acerto |
| `caso_17` | `baixo_risco` | acerto |
| `caso_25` | `informacao_insuficiente` | acerto |
| `caso_30` | `informacao_insuficiente` | acerto |

Resumo da execução final:

```text
Casos executados: 5
Respostas válidas: 5
Acertos: 5
Erros: 0
```

Também foi executada a suíte automatizada completa após a integração do
armazenamento:

```text
Testes automatizados: 45
Sucessos: 45
Falhas: 0
```

Os testes automatizados usam clientes simulados e não consomem créditos da API.
Somente a execução manual dos cinco casos realizou chamadas reais.

## Erros encontrados

Durante as primeiras execuções, foram observadas variações de classificação:

1. O `caso_30`, esperado como `informacao_insuficiente`, foi classificado como
   `moderado`.
2. Após um primeiro ajuste, o `caso_11`, esperado como `moderado`, foi
   classificado como `informacao_insuficiente`.
3. Em uma tentativa, a API retornou uma resposta vazia.
4. Os testes inicialmente apresentaram erro de importação quando foram
   executados a partir da pasta acima do projeto sem o caminho correto.
5. A configuração inicial do repositório remoto apontava para um endereço
   inexistente, impedindo o `git push`.

## Como os erros foram investigados

- os resultados obtidos foram comparados com as classificações definidas
  manualmente antes das chamadas;
- o prompt foi revisado sem reescrever os demais módulos;
- foi esclarecida a diferença entre uma mensagem vaga, que deve resultar em
  `informacao_insuficiente`, e um evento concreto pendente, que pode resultar
  em `moderado`;
- o tratamento de resposta vazia permaneceu no serviço de IA como erro
  controlado;
- os testes passaram a ser executados dentro da pasta `escudo-digital-ia` com
  Poetry;
- o endereço do remoto foi corrigido para o repositório da conta `ordep616`;
- depois de cada ajuste, os cinco casos e os testes automatizados foram
  executados novamente.

As respostas da IA podem variar entre chamadas. Por isso, o resultado de cinco
acertos não representa garantia de precisão e deve ser tratado apenas como uma
verificação inicial.

## Como a API de IA foi utilizada

A aplicação utiliza o endpoint compatível com OpenAI fornecido pelo
OpenRouter. A chave, o endpoint e o modelo são lidos do arquivo `.env`:

```dotenv
OPENROUTER_API_KEY=
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=openai/gpt-5-mini
```

O texto é anonimizado antes de ser enviado. A chamada recebe o prompt de
sistema e a mensagem fictícia ou anonimizada. O serviço solicita a resposta por
JSON Schema e devolve o conteúdo para `validator.py`. Erros técnicos são
convertidos em mensagens controladas, sem expor a chave ou detalhes internos.

## Privacidade e consumo

- a chave real permanece somente no `.env`;
- `.env` não é versionado;
- mensagens reais não devem ser utilizadas;
- CPF e telefone são anonimizados antes da chamada;
- a mensagem integral não é gravada;
- o armazenamento registra somente quantidade de chamadas, caracteres, tokens
  aproximados e horário;
- o banco SQLite local e seus arquivos auxiliares estão no `.gitignore`.

## Como o Codex foi utilizado

O Codex foi utilizado como apoio para:

- analisar a estrutura e a separação de responsabilidades;
- explicar os erros apresentados pelo Git, Poetry e testes;
- propor alterações pequenas e verificáveis;
- auxiliar na criação e revisão de testes automatizados;
- investigar as diferenças entre risco moderado e informação insuficiente;
- revisar riscos de privacidade e exposição da chave;
- orientar a integração do armazenamento ao fluxo principal;
- organizar a documentação do trabalho realizado.

Todas as alterações foram revisadas e testadas pela dupla antes dos commits.

## Decisões tomadas pela dupla

- utilizar Poetry para manter o ambiente reproduzível;
- utilizar OpenRouter com configuração por variáveis de ambiente;
- manter a comunicação com a API isolada em `ai_service.py`;
- solicitar JSON estruturado e validar novamente a resposta localmente;
- manter prompt, validação, privacidade, interface e armazenamento em módulos
  separados;
- não armazenar mensagens, mesmo depois da anonimização;
- registrar somente métricas mínimas de consumo;
- usar SQLite para o armazenamento local das métricas;
- usar mocks nos testes para evitar chamadas externas e alteração do banco real;
- tratar a análise como orientação educativa, nunca como confirmação de golpe.

## Commits relacionados

Entre os commits que registram o trabalho do período estão:

- `c053028` — criação dos artefatos de configuração e exemplo de ambiente;
- `7e03ce0` — implementação do serviço de IA e tratamento de falhas;
- `88a6b92` — prompt estruturado, métricas e testes de validação;
- `5693482` — migração do serviço de IA para OpenRouter;
- `ff29fcf` — configuração das dependências com Poetry;
- `5b65543`, `c052fe6` e `4e8c020` — refinamentos das regras de decisão;
- `4197ede` — integração do registro de consumo ao fluxo principal;
- `d467649` — armazenamento de consumo com SQLite.

## O que falta para o próximo dia

- ampliar a anonimização para e-mail, cartão, códigos de autenticação e links;
- implementar limites e regras gerais em `safety.py`;
- implementar `evaluator.py` e seus testes;
- executar os 30 casos e calcular acertos, falsos positivos, falsos negativos e
  respostas inválidas;
- implementar o modo educativo e a avaliação `util` ou `nao_util`;
- continuar atualizando os relatórios e o README conforme o projeto evoluir.
