# Especificação do Produto - Escudo Digital IA
## 1. Visão geral

O Escudo Digital IA é um assistente educativo de segurança digital. O produto analisa mensagens fictícias ou anonimizadas, identifica sinais de risco e ensina o usuário a reconhecer possíveis golpes digitais.

O sistema não deve afirmar com certeza que uma mensagem é fraudulenta ou legítima. Toda análise deve ser apresentada como orientação educativa e recomendar a verificação por canais oficiais.

A versão atual oferece uma interface de terminal e uma interface web construída
com Streamlit. As análises utilizam a API do OpenRouter com resposta estruturada
em JSON. O Prompt V1 permanece ativo nas interfaces enquanto o Prompt V2 é
avaliado no laboratório de testes.

## 2. Problema

Golpes digitais utilizam urgência, ameaça, recompensa, imitação e pedidos de dados ou dinheiro para pressionar pessoas a tomar decisões rápidas. Muitos usuários têm dificuldade para reconhecer esses sinais e podem clicar em links, enviar senhas, compartilhar códigos ou realizar pagamentos antes de verificar a situação.

## 3. Público-alvo

O público principal é formado por:

- estudantes;
- famílias;
- pessoas com pouca experiência digital;
- usuários que recebem mensagens suspeitas por SMS, e-mail ou aplicativos de conversa.

## 4. Situações de uso

### 4.1 Falso banco

O usuário recebe uma mensagem dizendo que sua conta será bloqueada e solicitando senha ou código de autenticação.

### 4.2 Falso familiar

Uma pessoa afirma ter trocado de número, finge ser um familiar e pede um PIX urgente.

### 4.3 Falso prêmio

O usuário recebe uma promessa de prêmio condicionada ao pagamento antecipado de uma taxa.

## 5. Objetivo

Permitir que uma pessoa envie uma mensagem fictícia ou anonimizada e receba:

- classificação de risco;
- certeza da análise, isto é, confiança da IA na classificação escolhida;
- sinais encontrados;
- explicação em linguagem simples;
- recomendações seguras e verificáveis;
- aviso sobre as limitações da IA.

## 6. Funcionalidades obrigatórias

### 6.1 Analisar mensagem

O sistema deve receber o texto de uma mensagem fictícia ou anonimizada e produzir uma análise estruturada.

### 6.2 Proteger dados pessoais

Antes de enviar o texto para a API de IA, o sistema deve localizar e ocultar:

- CPF;
- telefone;
- e-mail;
- número de cartão;
- códigos de autenticação;
- links.

### 6.3 Classificar o risco

As classificações permitidas são:

- `baixo_risco`;
- `moderado`;
- `alto_risco`;
- `informacao_insuficiente`.

### 6.4 Explicar os sinais

O sistema deve identificar e explicar sinais como:

- urgência;
- ameaça;
- recompensa;
- pedido de segredo;
- imitação de pessoa ou instituição;
- pedido de senha ou código;
- pedido de dados pessoais;
- pedido de dinheiro;
- link desconhecido;
- tentativa de impedir a verificação.

### 6.5 Recomendar ações seguras

O sistema poderá recomendar:

- não clicar em links;
- não enviar senhas ou códigos;
- não realizar pagamentos;
- abrir diretamente o aplicativo ou site oficial;
- confirmar a situação por um telefone ou canal oficial;
- pedir ajuda a uma pessoa de confiança.

### 6.6 Modo educativo

O produto apresenta dez exercícios fictícios armazenados localmente. Após a
resposta do usuário, o sistema informa se a classificação está correta e explica
os sinais de risco, as recomendações e a classificação esperada. O modo
Aprender não consulta a API e não consome créditos.

### 6.7 Avaliação da resposta

Na interface web, o usuário pode informar se a análise foi `util` ou
`nao_util`. O sistema salva no SQLite somente o valor da avaliação e o horário,
nunca a mensagem integral. A apresentação de um resumo dessas avaliações ainda
não foi implementada.

### 6.8 Estatísticas

O avaliador executado pelo terminal apresenta e salva a quantidade de testes,
acertos, erros, falsos positivos, falsos negativos, respostas inválidas e taxa
de acerto. A exibição dessas estatísticas diretamente nas interfaces de uso é
uma melhoria futura.

### 6.9 Interfaces

O produto possui duas formas de uso:

- `main.py`: menu de terminal para analisar mensagens e executar o modo
  Aprender;
- `web.py`: interface web em Streamlit para analisar mensagens, executar o
  modo Aprender e registrar avaliação `util` ou `nao_util`.

As análises reais dependem da chave e dos créditos do OpenRouter. O modo
Aprender funciona localmente.

## 7. Fluxo do sistema

A arquitetura completa, incluindo fluxo de dados, responsabilidades, tratamento de falhas e fluxo de avaliação, está documentada em [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md).

```text
Usuário
  |
  v
main.py ou web.py
  |
  v
safety.py - validação e limite de tamanho
  |
  v
privacy.py - anonimização de dados
  |
  v
ai_service.py - chamada à API de IA
  |
  v
validator.py - validação da resposta
  |
  v
Resposta educativa e aviso de limitação
  |
  v
Avaliação opcional do usuário na interface web
```

O aviso completo de segurança é exibido no fluxo de terminal. Sua inclusão
completa na interface web, antes e depois de cada análise, permanece pendente.

## 8. Responsabilidades dos arquivos

| Arquivo | Responsabilidade |
| --- | --- |
| `main.py` | Receber a entrada do terminal e coordenar segurança, privacidade, API, armazenamento e validação. |
| `web.py` | Apresentar a interface Streamlit, receber entradas e integrar análise, modo Aprender e avaliação de utilidade. |
| `interface.py` | Formatar a introdução, o aviso e o resultado da interface de terminal. |
| `aprender.py` | Carregar, validar e executar os dez exercícios educativos locais. |
| `privacy.py` | Localizar e ocultar dados sensíveis. |
| `safety.py` | Aplicar limites de tamanho e regras de segurança. |
| `prompts.py` | Armazenar as versões dos prompts. |
| `ai_service.py` | Chamar a API e tratar timeout, autenticação e indisponibilidade. |
| `validator.py` | Conferir campos, tipos e valores da resposta. |
| `evaluator.py` | Comparar o resultado da IA com o resultado esperado. |
| `storage.py` | Salvar somente métricas e dados permitidos. |

## 9. Formato da resposta

A API deverá retornar uma estrutura JSON semelhante a:

```json
{
  "classificacao": "alto_risco",
  "confianca": 0.92,
  "sinais": [
    "urgencia",
    "pedido_de_senha",
    "link_desconhecido"
  ],
  "recomendacoes": [
    "nao_clicar",
    "usar_canal_oficial"
  ],
  "explicacao_simples": "A mensagem cria pressão e solicita uma informação que não deveria ser compartilhada.",
  "informacao_insuficiente": false
}
```

### 9.1 Regras de validação

- Todos os campos são obrigatórios.
- `classificacao` deve conter um dos quatro valores permitidos.
- `confianca` deve ser um número entre 0 e 1 e representar a certeza da IA sobre a classificação, não o quanto a mensagem é confiável ou segura.
- `sinais` e `recomendacoes` devem ser listas.
- `explicacao_simples` deve ser um texto não vazio.
- `informacao_insuficiente` deve ser um valor booleano.
- Respostas ausentes, incompletas ou inválidas devem ser rejeitadas pelo sistema.

## 10. Regras de segurança e privacidade

- Não utilizar mensagens reais contendo dados pessoais.
- Não salvar o texto integral analisado.
- Não enviar dados pessoais para a API.
- Manter a chave da API somente no arquivo `.env`.
- Manter `.env` no `.gitignore`.
- Disponibilizar apenas `.env.example`, sem chave verdadeira.
- Não abrir, visitar ou verificar links recebidos.
- Não solicitar dados adicionais ao usuário.
- Não recomendar pagamentos ou compartilhamento de informações.
- Recusar mensagens vazias ou com mais de 1.000 caracteres.
- Exibir o aviso de limitação em todas as análises.
- Em caso de dúvida, recomendar a verificação por canal oficial.

O armazenamento local utiliza SQLite para registrar apenas quantidade de
caracteres, estimativa de tokens, horário e avaliação de utilidade. O banco
local está no `.gitignore`. Os arquivos de resultados da avaliação registram
somente identificadores, classificações, validade do JSON e tipos de erro.

## 11. Mensagem fixa de segurança

> Esta análise é educativa e pode cometer erros. Não clique em links, não envie senhas ou códigos e confirme a situação diretamente no aplicativo, site ou telefone oficial da instituição.

## 12. Limitações

O sistema:

- pode classificar uma mensagem incorretamente;
- não confirma a identidade do remetente;
- não acessa sistemas bancários, policiais ou governamentais;
- não abre nem verifica links;
- não substitui profissionais de segurança;
- não garante que uma mensagem seja legítima ou fraudulenta;
- deve responder `informacao_insuficiente` quando não houver contexto suficiente;
- depende da disponibilidade, dos créditos e do modelo configurado no OpenRouter;
- utiliza anonimização baseada em padrões, que pode não reconhecer todos os formatos existentes;
- ainda não apresenta estatísticas ou resumo das avaliações de utilidade na interface;
- ainda precisa exibir o aviso fixo completo na interface web;
- mantém o Prompt V1 nas interfaces enquanto o Prompt V2 passa pela avaliação final.

## 13. Critérios de sucesso

O projeto será considerado funcional quando:

- ocultar os seis tipos obrigatórios de dados;
- retornar todos os campos da resposta estruturada;
- detectar e tratar respostas incompletas da API;
- tratar timeout, erro de autenticação e indisponibilidade da API;
- executar os 30 casos de teste;
- registrar acertos, falsos positivos e falsos negativos;
- priorizar a redução de falsos negativos;
- exibir recomendações seguras;
- exibir o aviso de limitação em todas as análises;
- não armazenar mensagens integrais;
- possuir modo educativo com pelo menos dez exercícios;
- poder ser instalado e executado seguindo o [`README.md`](../README.md).

## 14. Casos de teste

O conjunto de testes está armazenado em `data/casos_teste.json` e possui a seguinte composição:

| Categoria | Quantidade | Classificação esperada |
| --- | ---: | --- |
| Alto risco | 10 | `alto_risco` |
| Risco moderado | 6 | `moderado` |
| Legítima | 8 | `baixo_risco` |
| Ambígua | 6 | `informacao_insuficiente` |
| **Total** | **30** | - |

A classificação esperada de cada caso deve ser definida manualmente antes da execução da IA.

## 15. Métricas

As métricas mínimas são:

- taxa geral de acerto;
- quantidade de falsos positivos;
- quantidade de falsos negativos;
- quantidade de respostas inválidas;
- avaliação de utilidade da resposta.

Um falso positivo ocorre quando uma mensagem legítima é classificada como perigosa. Um falso negativo ocorre quando uma mensagem perigosa é classificada como segura e deve ser tratado como o erro mais grave do produto.

### 15.1 Resultados registrados

O Prompt V1 foi executado nos 30 casos e obteve:

- 26 acertos e 4 erros;
- taxa de acerto de 86,67%;
- 1 falso positivo;
- 0 falsos negativos;
- 0 respostas inválidas;
- 3 outros erros de classificação.

A primeira avaliação completa do Prompt V2 também obteve 26 acertos, 4 erros
e taxa de acerto de 86,67%. Essa versão corrigiu os quatro erros observados no
V1, mas criou quatro novas divergências. Por esse motivo, o resultado do V2 é
preliminar e a comparação final permanece pendente até a revisão do prompt e a
nova execução dos 30 casos.

Os resultados são preservados separadamente em
`data/resultados_prompt_v1.json` e `data/resultados_prompt_v2.json`.

## 16. Fora do escopo

Não fazem parte desta versão:

- investigar crimes;
- denunciar usuários automaticamente;
- bloquear contas ou transações;
- abrir ou testar links recebidos;
- processar mensagens reais com dados pessoais;
- garantir a detecção de todos os golpes;
- substituir bancos, autoridades ou especialistas.

## 17. Evidências de conclusão

| Evidência | Estado atual |
| --- | --- |
| `data/casos_teste.json` com 30 casos classificados | Concluído |
| Arquitetura documentada em `docs/ARQUITETURA.md` | Concluído |
| Seis tipos de dados anonimizados | Concluído |
| Testes automáticos dos principais módulos | Concluído |
| Modo Aprender com dez exercícios | Concluído |
| Interface de terminal | Concluído |
| Interface web em Streamlit | Funcional; aviso completo ainda pendente |
| Avaliação `util` ou `nao_util` | Registro concluído; resumo ainda pendente |
| Resultados registrados sem mensagens integrais | Concluído |
| Prompt V1 preservado | Concluído |
| Prompt V2 e comparação final | Em avaliação |
| Relatórios dos cinco dias | Dias 1 a 3 concluídos; Dia 4 em andamento; Dia 5 pendente |
| Relatório final | Pendente |
| Histórico de commits pequenos e compreensíveis | Concluído até a etapa atual |
| [`README.md`](../README.md) com instalação, configuração e execução | Atualizado; métricas finais do V2 ainda pendentes |

## 18. Resumo do escopo entregue

### Entregue

- integração com o OpenRouter e resposta estruturada;
- tratamento de timeout, autenticação, indisponibilidade e resposta inválida;
- anonimização dos seis tipos obrigatórios;
- validação de entrada e limite de 1.000 caracteres;
- terminal e interface web;
- modo Aprender com dez exercícios;
- avaliação de utilidade sem armazenamento da mensagem;
- armazenamento de métricas permitidas em SQLite;
- 30 casos classificados e avaliador V1/V2;
- testes automáticos;
- documentação dos Dias 1 a 3 concluída e documentação do Dia 4 em andamento.

### Parcialmente entregue

- Prompt V2: criado e avaliado, mas ainda precisa de revisão e avaliação final;
- estatísticas: disponíveis pelo avaliador e nos arquivos JSON, mas não na interface;
- avaliação de utilidade: registrada, mas sem resumo estatístico;
- aviso de segurança: completo no terminal e ainda incompleto na interface web;
- documentação final: README e SPEC atualizados, aguardando métricas finais e relatórios de encerramento.

### Não entregue

- relatório do Dia 5;
- relatório final concluído;
- apresentação final e versão de entrega marcada no Git.
