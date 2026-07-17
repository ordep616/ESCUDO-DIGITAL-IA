# Relatório — Dia 3

> Status: concluído. As atividades de Pedro, a camada de segurança, o modo
> “Aprender”, o menu principal, a avaliação e a interface web foram integrados.
> A suíte completa possui 94 testes aprovados e a interface foi verificada
> manualmente.

## Objetivo do dia

O objetivo do terceiro dia é ampliar a privacidade do sistema, garantir que o
histórico não armazene mensagens, permitir avaliações `util` ou `nao_util`,
criar um modo educativo com pelo menos dez exercícios e tornar a interface
compreensível para pessoas sem conhecimento técnico.

## Divisão das tarefas

### Parte de Pedro

- ampliar a anonimização para CPF, telefone, e-mail, cartão, códigos de
  autenticação e links;
- criar testes automáticos para todos os tipos de dado mascarado;
- verificar que o texto integral não é salvo no histórico;
- criar no SQLite o armazenamento das avaliações `util` e `nao_util`;
- criar e classificar os dez exercícios fictícios do modo “Aprender”;
- escrever os sinais, as explicações e as recomendações de cada exercício;
- testar a privacidade e o armazenamento e documentar essas atividades.

### Parte do colaborador

- implementar as regras locais em `safety.py` e criar seus testes;
- implementar o fluxo do modo “Aprender”, carregando e validando os exercícios
  preparados por Pedro;
- comparar a resposta do usuário, mostrar a explicação e calcular a pontuação;
- integrar o modo “Aprender” ao menu principal;
- criar a interface web em Streamlit;
- conectar `registrar_avaliacao()` à interface, revisar a linguagem e criar
  testes do fluxo educativo e da integração.

## Atividades concluídas por Pedro

- [x] ampliar a anonimização para CPF, telefone, e-mail, cartão, códigos de
  autenticação e links;
- [x] criar testes automáticos para cada tipo de dado mascarado;
- [x] manter compatibilidade com o fluxo existente em `main.py`;
- [x] confirmar que mensagens integrais não são gravadas no SQLite;
- [x] criar a tabela de avaliações no banco local;
- [x] implementar `registrar_avaliacao()` para aceitar somente `util` e
  `nao_util`;
- [x] testar avaliações válidas, inválidas e valores que não sejam texto;
- [x] confirmar que a tabela de avaliações não possui coluna para mensagem;
- [x] criar e classificar dez exercícios fictícios para o modo “Aprender”;
- [x] escrever os sinais, as explicações e as recomendações dos exercícios;
- [x] executar os testes específicos e a suíte completa;
- [x] realizar commits pequenos e enviar as alterações ao GitHub.

### Ampliação da anonimização

O arquivo `privacy.py` foi ampliado para ocultar:

- CPF: `[CPF OCULTADO]`;
- telefone: `[TELEFONE OCULTADO]`;
- e-mail: `[E-MAIL OCULTADO]`;
- cartão: `[CARTÃO OCULTADO]`;
- código de autenticação: `[CÓDIGO OCULTADO]`;
- link: `[LINK OCULTADO]`.

Foi criada a função `anonimizar_dados_sensiveis()`. A função antiga
`anonimizar_cpf_telefone()` foi mantida como ponto de compatibilidade e passou
a chamar a função nova. Dessa forma, o fluxo existente em `main.py` recebeu a
proteção ampliada sem precisar mudar o nome importado.

Os padrões apenas substituem links encontrados no texto. O sistema não abre,
visita ou verifica esses endereços.

### Testes de privacidade

Foram adicionados testes individuais para e-mail, cartão, código de
autenticação e link, além dos testes que já cobriam CPF e telefone.

Resultado dos testes específicos:

```text
Testes de privacidade: 13
Sucessos: 13
Falhas: 0
```

### Proteção do histórico

O armazenamento continua registrando somente métricas permitidas:

- quantidade de chamadas;
- caracteres da entrada;
- tokens aproximados;
- data e horário.

O teste `test_registra_consumo_sem_salvar_mensagem_integral` confirma que o
texto fornecido não aparece no arquivo SQLite. Os testes utilizam bancos
temporários e não modificam o banco real da aplicação.

### Avaliação `util` ou `nao_util`

Foi criada no SQLite a tabela:

```sql
CREATE TABLE avaliacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    valor TEXT NOT NULL CHECK (valor IN ('util', 'nao_util')),
    criado_em TEXT NOT NULL
);
```

A função `registrar_avaliacao()`:

- aceita apenas `util` e `nao_util`;
- normaliza espaços e letras maiúsculas;
- rejeita valores inválidos;
- utiliza parâmetros no comando SQL;
- salva somente a avaliação e o horário;
- não recebe nem armazena a mensagem analisada.

Os testes também conferem que a tabela `avaliacoes` possui somente as colunas
`id`, `valor` e `criado_em`.

## Material do modo “Aprender” criado por Pedro

O projeto possui `data/exercicios_aprender.json` como base local do modo
educativo. O arquivo contém dez exercícios fictícios, e cada exercício possui:

- identificador;
- mensagem fictícia;
- classificação esperada;
- sinais presentes;
- explicação educativa;
- recomendações seguras.

A distribuição inicial é:

| Classificação | Quantidade |
| --- | ---: |
| `alto_risco` | 4 |
| `moderado` | 2 |
| `baixo_risco` | 2 |
| `informacao_insuficiente` | 2 |
| **Total** | **10** |

O arquivo JSON contém conteúdo fixo e versionado. Ele não é armazenado dentro
do SQLite. O SQLite permanece reservado para informações geradas durante a
execução, como métricas e avaliações.

Pedro criou esse conjunto de exercícios no commit `ff7dfb6`. O colaborador
utilizou o arquivo como entrada para implementar o fluxo do modo “Aprender” em
`aprender.py`, mantendo separadas a criação do conteúdo educativo e a execução
do programa.

## Atividade concluída pelo enrico

### Regras locais de segurança

O colaborador implementou `safety.py` e seus testes. A camada de segurança:

- exige uma entrada do tipo texto;
- remove espaços externos;
- rejeita mensagens vazias;
- rejeita mensagens maiores que o limite permitido;
- impede que uma entrada inválida chegue ao serviço de IA.

Essa atividade está registrada no commit `2a0b4b6`.

### Modo “Aprender”

O colaborador implementou `aprender.py`, que carrega e valida os dez exercícios
criados por Pedro no arquivo JSON. Em cada exercício, o fluxo:

1. apresenta uma mensagem fictícia;
2. solicita uma das quatro classificações permitidas;
3. compara a resposta do usuário com a classificação esperada;
4. informa se houve acerto ou erro;
5. mostra os sinais, a explicação e as recomendações;
6. calcula a quantidade de acertos e o aproveitamento final.

O modo educativo utiliza somente o conteúdo local do JSON e não chama a API.
Essa implementação está registrada no commit `94e2d44`.

### Menu principal

O `main.py` passou a oferecer três opções no terminal:

1. analisar uma mensagem;
2. iniciar o modo “Aprender”;
3. encerrar o programa.

Uma opção inválida é rejeitada sem executar a análise nem o modo educativo.

### Interface web e avaliação

Foi criada uma página web simples com Streamlit em `web.py`. A interface possui
duas abas:

- **Analisar mensagem**, que reutiliza o fluxo seguro de `main.py`, apresenta a
  classificação, a confiança, os sinais, a explicação e as recomendações;
- **Modo Aprender**, que apresenta os dez exercícios locais, compara cada
  resposta e calcula o aproveitamento final.

Depois de uma análise, o usuário pode escolher `util` ou `nao_util`. A função
`registrar_feedback_analise()` encaminha somente esse valor para
`registrar_avaliacao()`. A mensagem analisada não é recebida nem armazenada
pela função de avaliação.

O estado da interface impede que a mesma resposta do modo educativo seja
contabilizada mais de uma vez. A linguagem apresentada foi revisada para
explicar classificações e recomendações sem exigir conhecimento técnico.

## Testes executados

Após a ampliação da privacidade, criação da avaliação e integração da camada de
segurança, a suíte completa apresentou:

```text
Testes automatizados: 58
Sucessos: 58
Falhas: 0
```

Os testes não realizam chamadas externas e não consomem créditos da API.

### Testes do modo “Aprender”

O arquivo `tests/test_aprender.py` contém oito testes automáticos. Eles
verificam:

- o carregamento da base oficial com dez exercícios;
- a validação dos campos obrigatórios;
- a rejeição de classificações esperadas inválidas;
- a rejeição de arquivos que não sejam listas;
- a rejeição de quantidades diferentes de dez exercícios;
- a apresentação do resultado final;
- a ausência de chamadas à API durante o fluxo educativo.

```text
Testes do modo Aprender: 8
Sucessos: 8
Falhas: 0
```

### Testes do menu e da interface web

Foram adicionados testes para as opções do menu principal e seis testes das
funções auxiliares da interface web. Eles verificam:

- rótulos de classificação em linguagem humana;
- formatação da confiança;
- registro do feedback sem receber a mensagem;
- contabilização de uma única resposta por exercício;
- ausência de incremento quando a resposta está errada;
- avanço seguro para o exercício seguinte.

Para executar esses testes, a `.venv` foi sincronizada com `poetry install`,
pois o Streamlit havia sido acrescentado ao `pyproject.toml` e ao
`poetry.lock` depois da criação do ambiente virtual.

Depois da instalação do Streamlit 1.59.2 e das integrações posteriores, a suíte
completa foi executada sem chamadas externas à API:

```text
Testes automatizados: 94
Sucessos: 94
Falhas: 0
```

### Validação manual da interface

A interface também foi verificada manualmente. Foram conferidos:

- abertura e navegação pelo menu principal;
- envio de uma mensagem fictícia pelo fluxo de análise;
- apresentação da classificação, confiança, sinais, recomendações e
  explicação;
- execução do modo “Aprender” e apresentação das explicações;
- registro das opções `util` e `nao_util` sem armazenamento da mensagem;
- retorno ao menu e encerramento da aplicação.

Com essa verificação, as atividades previstas para o Dia 3 foram consideradas
concluídas.

## Erros encontrados e aprendizados

Durante a implementação foram encontrados alguns erros de edição e execução:

1. O Poetry não encontrou `pyproject.toml` quando o comando foi executado na
   pasta externa `escudodigital`. A solução foi entrar em
   `escudo-digital-ia` antes de executar os comandos.
2. A função de compatibilidade da anonimização foi declarada duas vezes, o que
   fez a função externa retornar `None`. A declaração duplicada foi removida.
3. `registrar_avaliacao()` foi inicialmente colocada no meio de
   `_resumir_consumo()`, causando `NameError`. A função foi movida para o final
   do módulo.
4. Depois da movimentação, uma indentação incorreta causou `IndentationError`.
   A declaração foi alinhada como função de nível principal.
5. A primeira integração web alterou acidentalmente o `caso_02` e removeu a
   tabela e a função de avaliação do `storage.py`. As regressões foram
   identificadas pela suíte automática e corrigidas no commit `db84c0f`.
6. Depois do `pull`, o ambiente virtual ainda não possuía o Streamlit instalado.
   O código e o lock já declaram a dependência; falta executar `poetry install`
   antes da validação final.

Depois de cada correção, os testes específicos e a suíte completa foram
executados novamente.

## Privacidade e segurança

- foram utilizados somente dados e mensagens fictícias;
- nenhum link de exercício foi aberto ou verificado;
- a mensagem integral não é salva;
- avaliações não possuem ligação com mensagem, nome ou dado pessoal;
- o banco local continua protegido pelo `.gitignore`;
- os testes usam bancos temporários;
- o modo “Aprender” funciona localmente sem chamar a API;
- a interface web reutiliza a validação e a anonimização do fluxo principal;
- o feedback salva somente `util`, `nao_util` e o horário.

## Como o Codex foi utilizado

O Codex foi utilizado para:

- orientar a ampliação gradual dos padrões de anonimização;
- explicar expressões regulares e marcadores;
- diagnosticar erros de duplicação, posição e indentação de funções;
- criar e executar testes automáticos;
- revisar a separação entre conteúdo fixo em JSON e dados locais em SQLite;
- organizar a divisão de tarefas e a documentação do dia.

## Commits realizados

- `2a0b4b6` — implementa regras locais de segurança;
- `757ed43` — amplia a anonimização de dados sensíveis;
- `d2129e7` — adiciona o armazenamento de avaliações;
- `ff7dfb6` — Pedro adiciona e classifica os dez exercícios do modo “Aprender”;
- `94e2d44` — implementa o fluxo do modo “Aprender”;
- `91878a5` — cria a primeira versão da interface web;
- `db84c0f` — corrige regressões e integra menu, avaliação e testes web.
