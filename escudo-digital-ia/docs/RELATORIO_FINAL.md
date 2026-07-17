# Relatório Final — Escudo Digital IA

- **Equipe:** Pedro e Enrico
- **Período:** cinco dias de desenvolvimento
- **Data de conclusão:** 17 de julho de 2026

## 1. Resumo do projeto

O Escudo Digital IA é um assistente educativo criado para ajudar pessoas a
reconhecer sinais de possíveis golpes digitais. O sistema recebe mensagens
fictícias ou previamente anonimizadas, protege dados sensíveis, consulta uma
API de inteligência artificial e apresenta classificação de risco, confiança,
sinais encontrados, recomendações e explicação em linguagem simples.

A ferramenta não determina com certeza se uma mensagem é legítima ou
fraudulenta. Sua finalidade é educativa: indicar sinais de atenção e orientar o
usuário a confirmar a situação diretamente por canais oficiais.

O produto final possui interface de terminal, interface web em Streamlit, modo
educativo com dez exercícios, armazenamento seguro de métricas, avaliação
`util` ou `nao_util`, 30 casos fictícios e comparação entre duas versões do
prompt.

## 2. Problema e público-alvo

Golpes digitais utilizam urgência, ameaça, recompensa, imitação de pessoas ou
instituições e pedidos de dinheiro, senha ou código para pressionar a vítima a
agir antes de verificar a situação. Pessoas com pouca experiência digital
podem ter dificuldade para identificar esses sinais.

O público principal do projeto é formado por:

- estudantes;
- famílias;
- pessoas com pouca experiência digital;
- usuários que recebem mensagens suspeitas por SMS, e-mail ou aplicativos de
conversa.

O produto foi projetado para explicar riscos com linguagem acessível, sem
substituir bancos, autoridades, profissionais de segurança ou canais oficiais.

## 3. Solução desenvolvida

A construção foi organizada em cinco etapas:


| Dia | Entrega principal                                                                                                |
| --- | ---------------------------------------------------------------------------------------------------------------- |
| 1   | Definição do produto, público, arquitetura, resposta estruturada e 30 casos fictícios classificados manualmente. |
| 2   | Integração com o OpenRouter, Prompt V1, JSON estruturado, validação, tratamento de erros e métricas de consumo.  |
| 3   | Anonimização de seis tipos de dados, camada de segurança, modo Aprender, avaliação de utilidade e interface web. |
| 4   | Execução dos 30 casos, análise dos erros, criação e revisão do Prompt V2 e comparação numérica com o V1.         |
| 5   | Revisão da documentação, preparação das demonstrações e organização da entrega final.                            |


As principais ações disponíveis são:

- analisar uma mensagem fictícia ou previamente anonimizada;
- classificar o risco como `baixo_risco`, `moderado`, `alto_risco` ou
`informacao_insuficiente`;
- apresentar sinais, recomendações e explicação educativa;
- realizar dez exercícios locais no modo Aprender;
- registrar se uma análise foi útil ou não útil;
- executar o conjunto de avaliação com o Prompt V1 ou V2.



## 4. Arquitetura e fluxo do sistema

O projeto separa as responsabilidades para facilitar testes, manutenção e
revisão de segurança.

```text
Usuário
  |
  v
Terminal ou interface web
  |
  v
safety.py — valida a entrada e aplica o limite de tamanho
  |
  v
privacy.py — oculta dados sensíveis
  |
  v
ai_service.py + prompts.py — consultam o OpenRouter
  |
  v
validator.py — valida campos, tipos e valores do JSON
  |
  v
Resposta educativa
  |
  v
storage.py — registra somente métricas e avaliações permitidas
```

Outros componentes importantes são:

- `main.py`: coordena o fluxo e o menu de terminal;
- `web.py`: apresenta análise, modo Aprender e feedback no Streamlit;
- `interface.py`: formata avisos e resultados do terminal;
- `aprender.py`: carrega, valida e executa os exercícios locais;
- `evaluator.py`: compara classificações esperadas e obtidas;
- `data/casos_teste.json`: mantém os 30 casos classificados manualmente;
- `data/resultados_prompt_v1.json` e `data/resultados_prompt_v2.json`:
preservam resultados sem copiar as mensagens.



## 5. Funcionalidades entregues

Foram entregues:

- integração funcional com a API do OpenRouter;
- resposta estruturada por JSON Schema;
- validação local dos seis campos obrigatórios;
- tratamento de timeout, autenticação, conexão, indisponibilidade e resposta
vazia ou inválida;
- anonimização local de CPF, telefone, e-mail, cartão, código e link;
- validação de entrada vazia, tipo incorreto e limite de 1.000 caracteres;
- interface de terminal com menu principal;
- interface web construída com Streamlit;
- modo Aprender com exatamente dez exercícios e explicação após cada resposta;
- avaliação `util` ou `nao_util` sem vínculo com a mensagem analisada;
- armazenamento local de quantidade de chamadas, caracteres, tokens
aproximados e horário;
- 30 casos fictícios distribuídos entre quatro classificações;
- Prompt V1 e Prompt V2 preservados separadamente;
- avaliação automática de acertos, falsos positivos, falsos negativos,
respostas inválidas e outros erros;
- testes automáticos dos principais módulos.



## 6. Privacidade e segurança

A privacidade foi tratada antes da chamada à API. Os dados reconhecidos são
substituídos pelos seguintes marcadores:


| Tipo de dado | Marcador              |
| ------------ | --------------------- |
| CPF          | `[CPF OCULTADO]`      |
| Telefone     | `[TELEFONE OCULTADO]` |
| E-mail       | `[E-MAIL OCULTADO]`   |
| Cartão       | `[CARTÃO OCULTADO]`   |
| Código       | `[CÓDIGO OCULTADO]`   |
| Link         | `[LINK OCULTADO]`     |


Também foram aplicadas as seguintes medidas:

- chave real mantida somente no arquivo `.env`;
- `.env`, banco SQLite e arquivos auxiliares protegidos pelo `.gitignore`;
- `.env.example` sem chave verdadeira;
- uso exclusivo de mensagens fictícias ou previamente anonimizadas;
- links nunca são abertos ou verificados;
- mensagem integral não é armazenada no histórico;
- banco SQLite registra somente métricas, avaliação e horário;
- comandos SQL utilizam parâmetros;
- testes de armazenamento utilizam bancos temporários;
- arquivos de avaliação não possuem o campo `mensagem`;
- erros técnicos são apresentados sem expor chave ou detalhes internos;
- recomendações nunca incentivam clique, pagamento ou envio de dados.

Foi verificado no resultado final do Prompt V2 que os 30 registros contêm
somente identificador, classificações, validade do JSON, tipo de resultado e
erros de validação.

## 7. Utilização da API de IA

O projeto utiliza o endpoint compatível com OpenAI oferecido pelo OpenRouter.
A configuração é carregada do `.env` pelas variáveis:

```dotenv
OPENROUTER_API_KEY=
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=openai/gpt-5-mini
```

A chave verdadeira não foi registrada em código, documentação ou resultados.
O serviço envia o prompt de sistema e somente a versão protegida da mensagem. A
resposta é solicitada em JSON com os campos:

- `classificacao`;
- `confianca`;
- `sinais`;
- `recomendacoes`;
- `explicacao_simples`;
- `informacao_insuficiente`.

Os testes automáticos utilizam clientes simulados e não consomem créditos. As
chamadas reais foram reservadas para testes manuais e avaliações dos prompts.
Na avaliação final, os oito casos afetados foram testados antes da execução
completa dos 30 casos.

## 8. Metodologia de avaliação

As classificações esperadas foram definidas manualmente antes das consultas à
IA. O conjunto possui:


| Categoria      | Quantidade | Classificação esperada    |
| -------------- | ---------- | ------------------------- |
| Alto risco     | 10         | `alto_risco`              |
| Risco moderado | 6          | `moderado`                |
| Legítima       | 8          | `baixo_risco`             |
| Ambígua        | 6          | `informacao_insuficiente` |
| **Total**      | **30**     | —                         |


Para cada caso, o avaliador:

1. valida a mensagem;
2. anonimiza os dados reconhecidos;
3. consulta a API com a versão escolhida do prompt;
4. valida a resposta estruturada;
5. compara a classificação esperada com a obtida;
6. identifica acerto, falso positivo, falso negativo, resposta inválida ou
  outro erro de classificação;
7. calcula as métricas gerais;
8. salva somente campos permitidos.

Falsos negativos receberam prioridade máxima, pois representam mensagens de
alto risco classificadas como seguras.

## 9. Comparação entre Prompt V1 e Prompt V2

O Prompt V1 apresentou quatro erros. A primeira versão do Prompt V2 corrigiu
esses casos, mas criou quatro regressões em outras mensagens. A dupla analisou
as causas e revisou somente as regras de decisão responsáveis pelas
divergências, preservando integralmente o Prompt V1.

Antes da execução final, oito casos afetados pelas duas versões foram repetidos
com o Prompt V2 revisado. Os oito acertaram. Depois, os 30 casos foram
executados novamente.


| Métrica             | Prompt V1 | Prompt V2 revisado |
| ------------------- | --------- | ------------------ |
| Total de casos      | 30        | 30                 |
| Acertos             | 26        | 28                 |
| Erros               | 4         | 2                  |
| Taxa de acerto      | 86,67%    | 93,33%             |
| Falsos positivos    | 1         | 1                  |
| Falsos negativos    | 0         | 0                  |
| Respostas inválidas | 0         | 0                  |
| Outros erros        | 3         | 1                  |


O Prompt V2 revisado aumentou a taxa de acerto em 6,66 pontos percentuais e
reduziu o total de erros de quatro para dois. O número de falsos positivos
permaneceu em um. Nenhuma das versões apresentou falso negativo ou resposta
inválida nessa avaliação.

Os casos `caso_15`, `caso_20` e `caso_23`, que falharam no V1, foram corrigidos
na execução completa do V2 revisado. O `caso_24` permaneceu divergente, embora
tenha acertado durante a execução isolada.

## 10. Erros encontrados e limitações

Os erros restantes no Prompt V2 revisado foram:


| Caso      | Esperado      | Obtido                    | Tipo                  |
| --------- | ------------- | ------------------------- | --------------------- |
| `caso_12` | `moderado`    | `informacao_insuficiente` | erro de classificação |
| `caso_24` | `baixo_risco` | `moderado`                | falso positivo        |


O `caso_12` menciona uma atualização de cadastro, mas não identifica claramente
o remetente. A IA valorizou a falta de contexto, enquanto a classificação
manual considerou a possível consequência suficiente para risco moderado.

O `caso_24` informa que um extrato está disponível e recomenda consultar o
aplicativo oficial. Ele foi classificado corretamente no teste isolado e como
moderado na execução completa. Essa diferença demonstra que modelos
generativos podem variar mesmo com mensagem, prompt e modelo iguais.

Limitações conhecidas:

- a IA pode produzir classificações incorretas ou variar entre chamadas;
- confiança alta não significa que o resultado está correto;
- o sistema não confirma a identidade do remetente;
- links não são abertos, verificados ou classificados;
- a anonimização usa padrões locais e pode não reconhecer todos os formatos;
- a avaliação utiliza somente 30 casos fictícios;
- classificações esperadas definidas por pessoas também possuem subjetividade;
- o produto depende da disponibilidade, das regras e dos créditos do
OpenRouter;
- as interfaces de análise ainda utilizam o Prompt V1 enquanto o V2 permanece
como versão avaliada no laboratório;
- estatísticas e resumo do feedback ainda não são apresentados na interface;
- o aviso fixo completo de segurança ainda precisa ser incluído antes e depois
da análise na interface web;
- o produto não garante a detecção de golpes e não substitui canais oficiais.



## 11. Testes executados

A suíte final foi executada com:

```bash
poetry run python -m unittest discover -s tests -v
```

Resultado:

```text
Testes automatizados: 94
Sucessos: 94
Falhas: 0
```

Os testes cobrem:

- comunicação com a API e tratamento de falhas;
- anonimização dos seis tipos de dados;
- validação e limite da entrada;
- validação do JSON retornado;
- fluxo principal e interface de terminal;
- modo Aprender;
- armazenamento de consumo e avaliações;
- carregamento e avaliação dos 30 casos;
- preservação dos prompts;
- funções auxiliares da interface web;
- ausência de mensagens integrais nos resultados e no banco de testes.

Além da suíte automática, foram realizados:

- testes manuais da interface, do modo Aprender e do feedback;
- cinco chamadas iniciais com diferentes classificações;
- 30 chamadas com o Prompt V1;
- avaliações da primeira versão do Prompt V2;
- oito chamadas direcionadas com o Prompt V2 revisado;
- 30 chamadas para a avaliação final do Prompt V2 revisado.



### Demonstrações preparadas


| Demonstração                                  | Caso ou recurso | Resultado esperado                         |
| --------------------------------------------- | --------------- | ------------------------------------------ |
| Mensagem perigosa com pedido de código        | `caso_02`       | `alto_risco`                               |
| Mensagem legítima sobre aula                  | `caso_17`       | `baixo_risco`                              |
| Mensagem ambígua sem contexto                 | `caso_25`       | `informacao_insuficiente`                  |
| Mensagem com CPF, telefone e e-mail fictícios | `privacy.py`    | substituição pelos marcadores de ocultação |
| Caso melhorado entre V1 e V2                  | `caso_20`       | V1: `moderado`; V2: `baixo_risco`          |




## 12. Divisão de tarefas e colaboração



### Pedro

- organização inicial do produto, casos fictícios e documentação;
- configuração e proteção da chave;
- implementação e revisão do serviço de IA;
- solicitação de resposta estruturada;
- execução das chamadas reais iniciais;
- ampliação da privacidade e criação de seus testes;
- armazenamento seguro de consumo e avaliações;
- criação e classificação dos dez exercícios educativos;
- implementação do avaliador e das métricas;
- execução das avaliações V1 e V2;
- comparação dos resultados e elaboração dos relatórios.



### Enrico

- configuração do ambiente e das dependências com Poetry;
- criação e refinamento do Prompt V1;
- implementação do validador da resposta;
- integração inicial do registro de consumo;
- implementação da camada local de segurança;
- implementação do fluxo do modo Aprender;
- integração do menu principal;
- criação e correção da interface web;
- conexão do feedback à interface;
- criação, análise e revisão do Prompt V2;
- testes de integração das funcionalidades desenvolvidas.

## 13. Como o Codex foi utilizado

O Codex foi utilizado como apoio para:

- transformar as tarefas da missão em etapas menores;
- revisar a separação de responsabilidades dos módulos;
- explicar comandos de Git, Poetry, Python e SQLite;
- investigar erros de importação, indentação, integração e configuração;
- orientar a criação e a execução de testes;
- revisar riscos de exposição da chave e armazenamento de mensagens;
- analisar divergências entre classificações esperadas e obtidas;
- propor ajustes pequenos no prompt;
- comparar as métricas do Prompt V1 e do Prompt V2;
- organizar README, SPEC e relatórios.

As sugestões foram lidas, testadas e adaptadas antes dos commits. A dupla
permaneceu responsável pelas decisões, classificações esperadas, execução das
chamadas e validação do resultado final.

## 14. Melhorias futuras

- revisar os casos `caso_12` e `caso_24` sem prejudicar os outros 28 resultados;
- repetir avaliações para medir a variação entre chamadas;
- ampliar o conjunto de casos fictícios;
- testar as explicações com avaliadores internos;
- integrar o Prompt V2 à interface depois de nova revisão;
- exibir o aviso fixo completo na interface web;
- apresentar estatísticas do laboratório na interface;
- mostrar um resumo das avaliações `util` e `nao_util`;
- melhorar acessibilidade, navegação e mensagens de erro;
- ampliar os formatos reconhecidos pela anonimização;
- criar testes de interface de ponta a ponta;
- estudar controle de custo, latência e escolha de modelos.



## 15. Conclusão

O projeto atingiu o objetivo de construir uma ferramenta educativa, funcional e
testada para análise de mensagens suspeitas. O sistema utiliza uma API de IA,
protege a chave, anonimiza seis tipos de dados, valida a resposta estruturada,
trata falhas externas, não armazena mensagens integrais e oferece modos de
análise e aprendizagem.

A avaliação demonstrou evolução mensurável: a taxa de acerto passou de 86,67%
no Prompt V1 para 93,33% no Prompt V2 revisado. O total de erros caiu de quatro
para dois, sem falsos negativos ou respostas inválidas. Os erros restantes não
foram ocultados e permanecem documentados como evidência das limitações da IA.

O Escudo Digital IA deve ser utilizado como apoio educativo, nunca como
confirmação definitiva de fraude. A recomendação final continua sendo não
clicar em links, não compartilhar senhas ou códigos e confirmar a situação
diretamente pelo aplicativo, site ou telefone oficial da instituição.