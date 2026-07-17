# Escudo Digital IA

O Escudo Digital IA é um assistente educativo que ajuda pessoas a reconhecer
sinais comuns de golpes em mensagens fictícias ou previamente anonimizadas.
Ele identifica situações como urgência, ameaça, pedido de dinheiro, solicitação
de senha ou código e imitação de pessoas ou instituições.

O projeto não determina com certeza se uma mensagem é legítima ou fraudulenta.
Sua função é apresentar sinais de risco, explicar o resultado em linguagem
simples e recomendar que a situação seja confirmada por canais oficiais.

## Problema que o projeto resolve

Golpes digitais frequentemente pressionam a vítima para agir rapidamente,
clicar em links, fornecer dados pessoais ou realizar pagamentos. Pessoas com
pouca experiência digital podem ter dificuldade para identificar esses sinais.

O Escudo Digital IA recebe uma mensagem, protege os dados sensíveis, consulta
uma API de inteligência artificial e apresenta:

- classificação como baixo risco, moderado, alto risco ou informação
  insuficiente;
- confiança da IA na classificação;
- sinais encontrados;
- recomendações de segurança;
- explicação em linguagem simples;
- aviso de que a análise pode cometer erros.

Os requisitos completos estão no [SPEC.md](escudo-digital-ia/SPEC.md).

## Funcionalidades entregues

- análise educativa de mensagens por meio da API do OpenRouter;
- resposta estruturada e validada em JSON;
- anonimização local de CPF, telefone, e-mail, cartão, códigos e links;
- limite de tamanho e validação da entrada antes da chamada à API;
- tratamento de timeout, autenticação, indisponibilidade e resposta inválida;
- interface de terminal;
- interface web construída com Streamlit;
- modo Aprender com dez exercícios e explicações;
- registro de avaliação `útil` ou `não útil` na interface web;
- armazenamento local de métricas sem salvar a mensagem integral;
- 30 casos fictícios para avaliação da IA;
- preservação dos prompts V1 e V2 para comparação;
- testes automáticos dos principais módulos.

## Fluxo do sistema

```text
Usuário
  -> interface de terminal ou web
  -> validação de segurança
  -> anonimização dos dados sensíveis
  -> API de IA pelo OpenRouter
  -> validação da resposta JSON
  -> resultado educativo e aviso de limitação
```

O modo Aprender utiliza exercícios locais e não precisa consultar a API.

## Requisitos

- Python 3.11 ou superior;
- Poetry;
- acesso ao terminal;
- chave de API do OpenRouter para análises reais;
- créditos e acesso ao modelo configurado no OpenRouter.

## Instalação

Clone o repositório:

```bash
git clone https://github.com/ordep616/ESCUDO-DIGITAL-IA.git
```

Entre na pasta que contém o `pyproject.toml`:

```bash
cd ESCUDO-DIGITAL-IA/escudo-digital-ia
```

Instale o ambiente e as dependências:

```bash
poetry install
```

Confira se o ambiente foi criado corretamente:

```bash
poetry run python --version
```

Todos os comandos das próximas seções devem ser executados dentro da pasta
`escudo-digital-ia`.

## Configuração do `.env`

Crie o arquivo local a partir do exemplo:

```bash
cp .env.example .env
```

Preencha o `.env`:

```dotenv
OPENROUTER_API_KEY=sua-chave-do-openrouter
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=openai/gpt-5-mini
```

O `.env` está ignorado pelo Git e não deve ser compartilhado. A chave verdadeira
nunca deve aparecer no `.env.example`, no código, em commits, relatórios,
capturas de tela ou mensagens.

Confirme que o arquivo está protegido:

```bash
git check-ignore -v .env
```

## Como executar

### Interface web

Inicie a aplicação Streamlit:

```bash
poetry run streamlit run web.py
```

Abra o endereço local mostrado no terminal. No menu da página é possível:

- analisar uma mensagem fictícia ou previamente anonimizada;
- realizar os dez exercícios do modo Aprender;
- registrar se uma análise foi útil ou não útil.

Encerre o servidor com `Ctrl+C` no terminal.

### Interface de terminal

Execute:

```bash
poetry run python main.py
```

Escolha uma das opções do menu:

1. analisar uma mensagem;
2. iniciar o modo Aprender;
3. sair.

A análise de mensagem utiliza a API real e pode consumir créditos. O modo
Aprender funciona localmente e não consome créditos.

## Como executar os testes automáticos

Execute toda a suíte sem realizar chamadas reais à API:

```bash
poetry run python -m unittest discover -s tests -v
```

Uma execução correta termina com `OK`.

Para testar somente um módulo, informe o nome do arquivo. Exemplo:

```bash
poetry run python -m unittest discover -s tests -p 'test_privacy.py' -v
```

Os testes automáticos utilizam clientes simulados quando verificam a integração
com a IA. Portanto, eles não precisam da chave e não consomem créditos.

## Como avaliar a IA

O avaliador compara a classificação retornada pela API com a classificação
esperada nos 30 casos fictícios. Essas execuções fazem chamadas reais e podem
consumir créditos.

Executar todos os casos com o Prompt V1:

```bash
poetry run python evaluator.py --prompt v1
```

Executar todos os casos com o Prompt V2:

```bash
poetry run python evaluator.py --prompt v2
```

Executar somente casos específicos:

```bash
poetry run python evaluator.py --prompt v2 --casos caso_01 caso_11 caso_30
```

Os resultados são gravados em:

- `data/resultados_prompt_v1.json`;
- `data/resultados_prompt_v2.json`.

Esses arquivos registram identificador, classificação esperada, classificação
obtida, validade do JSON e tipo de resultado. Eles não copiam o texto integral
das mensagens.

## Resultados registrados

O Prompt V1 foi executado nos 30 casos fictícios e obteve:

- 26 acertos;
- 4 erros;
- taxa de acerto de 86,67%;
- 1 falso positivo;
- 0 falsos negativos;
- 0 respostas inválidas.

A primeira avaliação completa do Prompt V2 também obteve 26 acertos e taxa de
86,67%. Ela corrigiu quatro erros do V1, mas criou quatro novas divergências.
Esse resultado é preliminar: a comparação final deve ser atualizada depois da
revisão do Prompt V2 e da nova execução dos 30 casos.

## Privacidade e segurança

Antes do envio à API, o projeto mascara localmente:

| Tipo | Substituição |
| --- | --- |
| CPF | `[CPF OCULTADO]` |
| Telefone | `[TELEFONE OCULTADO]` |
| E-mail | `[E-MAIL OCULTADO]` |
| Cartão | `[CARTÃO OCULTADO]` |
| Código | `[CÓDIGO OCULTADO]` |
| Link | `[LINK OCULTADO]` |

Outras proteções aplicadas:

- a chave permanece somente no `.env`;
- mensagens vazias ou grandes demais são recusadas;
- links não são abertos ou verificados;
- o histórico não armazena o texto integral recebido;
- o SQLite registra apenas métricas de tamanho, horário e avaliações;
- os resultados dos testes não armazenam as mensagens;
- erros de autenticação, timeout e indisponibilidade são apresentados de forma
  controlada;
- a resposta da IA é validada antes de ser exibida.

## Métricas locais

O arquivo local `data/escudo_digital.db` registra a quantidade de chamadas, o
tamanho aproximado das entradas e as avaliações de utilidade. Ele está no
`.gitignore` e não deve ser enviado ao repositório.

Para consultar um resumo legível do consumo:

```bash
poetry run python -c "import json; from storage import carregar_consumo; print(json.dumps(carregar_consumo(), ensure_ascii=False, indent=2))"
```

## Estrutura principal

```text
escudo-digital-ia/
├── main.py                 # interface de terminal e fluxo da análise
├── web.py                  # interface web em Streamlit
├── aprender.py             # funcionamento do modo Aprender
├── ai_service.py           # comunicação com o OpenRouter
├── privacy.py              # anonimização de dados sensíveis
├── safety.py               # validação e limite da entrada
├── prompts.py              # versões V1 e V2 do prompt
├── validator.py            # validação da resposta estruturada
├── evaluator.py            # execução e comparação dos casos
├── storage.py              # métricas permitidas em SQLite
├── data/                   # exercícios, casos e resultados
├── docs/                   # arquitetura e relatórios
└── tests/                  # testes automáticos
```

## Limitações

- A IA pode errar, mesmo quando apresenta confiança alta.
- A ferramenta não confirma se uma mensagem é realmente legítima ou
  fraudulenta.
- O sistema não verifica identidade, contas, pagamentos ou reputação de links.
- A anonimização usa padrões locais e pode não reconhecer todos os formatos
  possíveis.
- Mensagens com pouco contexto podem ser classificadas de forma incorreta.
- A análise depende da disponibilidade, das regras, dos créditos e do modelo do
  OpenRouter.
- O modelo configurado precisa aceitar a saída estruturada solicitada.
- As interfaces de análise utilizam atualmente o Prompt V1; o Prompt V2 está em
  avaliação antes de substituir a versão utilizada pelo produto.
- O produto é educativo e não substitui banco, polícia, suporte oficial ou
  orientação profissional.

## Melhorias futuras

- concluir a revisão e a comparação final do Prompt V2;
- reduzir divergências de classificação sem aumentar falsos negativos;
- ampliar os testes de integração do fluxo completo;
- melhorar a acessibilidade e a experiência da interface web;
- apresentar estatísticas de testes e feedback diretamente na interface;
- testar a ferramenta com avaliadores internos e registrar a utilidade das
  explicações;
- ampliar os formatos reconhecidos pela anonimização.

## Aviso de segurança

> Esta análise é educativa e pode cometer erros. Não clique em links, não envie
> senhas ou códigos e confirme a situação diretamente no aplicativo, site ou
> telefone oficial da instituição.

## Documentação

- [Especificação do produto](escudo-digital-ia/SPEC.md)
- [Arquitetura](escudo-digital-ia/docs/ARQUITETURA.md)
- [Relatório do Dia 1](escudo-digital-ia/docs/RELATORIO_DIA_1.md)
- [Relatório do Dia 2](escudo-digital-ia/docs/RELATORIO_DIA_2.md)
- [Relatório do Dia 3](escudo-digital-ia/docs/RELATORIO_DIA_3.md)
- [Relatório do Dia 4](escudo-digital-ia/docs/RELATORIO_DIA_4.md)
- [Relatório final](escudo-digital-ia/docs/RELATORIO_FINAL.md)
