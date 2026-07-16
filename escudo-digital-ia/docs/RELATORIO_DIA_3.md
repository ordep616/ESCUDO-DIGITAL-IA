# Relatório — Dia 3

> Status: relatório parcial. As atividades de Pedro, a camada de segurança e o
> modo “Aprender” já foram registrados. A integração da avaliação, o menu
> principal e a interface final ainda aguardam o trabalho do colaborador.

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
- criar no SQLite o armazenamento das avaliações `util` e `nao_util`.

### Parte do colaborador

- implementar as regras locais em `safety.py`;
- criar o modo “Aprender” com no mínimo dez exercícios fictícios;
- carregar e validar os exercícios utilizados no modo educativo;
- mostrar os sinais, a explicação e as recomendações após cada resposta;
- conectar `registrar_avaliacao()` à interface;
- criar uma página web simples ou uma interface no Telegram, conforme a
  decisão da equipe;
- revisar a linguagem para usuários sem conhecimento técnico;
- criar testes automáticos para o fluxo educativo e para a integração da
  avaliação.

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

## Material do modo “Aprender”

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

## Atividade concluída pelo colaborador

### Regras locais de segurança

O colaborador implementou `safety.py` e seus testes. A camada de segurança:

- exige uma entrada do tipo texto;
- remove espaços externos;
- rejeita mensagens vazias;
- rejeita mensagens maiores que o limite permitido;
- impede que uma entrada inválida chegue ao serviço de IA.

Essa atividade está registrada no commit `2a0b4b6`.

### Modo “Aprender”

O colaborador implementou `aprender.py`, que carrega e valida exatamente dez
exercícios do arquivo JSON. Em cada exercício, o fluxo:

1. apresenta uma mensagem fictícia;
2. solicita uma das quatro classificações permitidas;
3. compara a resposta do usuário com a classificação esperada;
4. informa se houve acerto ou erro;
5. mostra os sinais, a explicação e as recomendações;
6. calcula a quantidade de acertos e o aproveitamento final.

O modo educativo utiliza somente o conteúdo local do JSON e não chama a API.
Essa implementação está registrada no commit `94e2d44`.

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

Depois de cada correção, os testes específicos e a suíte completa foram
executados novamente.

## Privacidade e segurança

- foram utilizados somente dados e mensagens fictícias;
- nenhum link de exercício foi aberto ou verificado;
- a mensagem integral não é salva;
- avaliações não possuem ligação com mensagem, nome ou dado pessoal;
- o banco local continua protegido pelo `.gitignore`;
- os testes usam bancos temporários;
- o modo “Aprender” funciona localmente sem chamar a API.

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
- `ff7dfb6` — adiciona os exercícios do modo “Aprender”;
- `94e2d44` — implementa o fluxo do modo “Aprender”.

## O que Pedro deve saber explicar da parte do colaborador

- o problema resolvido por `safety.py`;
- por que a validação ocorre antes da chamada à IA;
- como mensagens vazias e grandes são rejeitadas;
- como o modo “Aprender” carrega e valida o JSON;
- como a escolha do usuário é comparada com a resposta esperada;
- por que a explicação deve aparecer tanto em acertos quanto em erros;
- como a pontuação é calculada sem chamar a API.

## O que o colaborador deve saber explicar da parte de Pedro

- como os seis tipos de dados são localizados e substituídos;
- por que a função antiga de privacidade foi mantida;
- por que mensagens não são armazenadas;
- diferença entre conteúdo fixo no JSON e dados de execução no SQLite;
- como `registrar_avaliacao()` valida e salva apenas `util` ou `nao_util`;
- como os testes temporários protegem o banco real.

## Pendências para concluir o Dia 3

- [ ] conectar o modo “Aprender” ao menu principal;
- [ ] conectar `registrar_avaliacao()` à interface;
- [ ] criar a página web simples ou integração com Telegram;
- [ ] revisar toda a linguagem apresentada ao usuário;
- [ ] criar testes do menu e das integrações pendentes;
- [ ] executar a suíte completa após a integração;
- [ ] completar este relatório com os resultados finais do colaborador.
