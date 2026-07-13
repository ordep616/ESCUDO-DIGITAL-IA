# Especificação do Produto - Escudo Digital IA

## 1. Visão geral

O Escudo Digital IA é um assistente educativo de segurança digital. O produto analisa mensagens fictícias ou anonimizadas, identifica sinais de risco e ensina o usuário a reconhecer possíveis golpes digitais.

O sistema não deve afirmar com certeza que uma mensagem é fraudulenta ou legítima. Toda análise deve ser apresentada como orientação educativa e recomendar a verificação por canais oficiais.

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
- nível de confiança;
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

O produto deverá apresentar pelo menos dez exercícios fictícios. Após a resposta do usuário, o sistema deverá explicar os sinais de risco presentes em cada exercício.

### 6.7 Avaliação da resposta

O usuário poderá informar se a análise foi `util` ou `nao_util`. O sistema deve salvar apenas a avaliação e as métricas permitidas, nunca a mensagem integral.

### 6.8 Estatísticas

O sistema deverá apresentar a quantidade de testes executados, acertos, falsos positivos, falsos negativos e respostas inválidas.

## 7. Fluxo do sistema

A arquitetura completa, incluindo fluxo de dados, responsabilidades, tratamento de falhas e fluxo de avaliação, está documentada em [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md).

```text
Usuário
  |
  v
Interface e aviso de segurança
  |
  v
privacy.py - anonimização de dados
  |
  v
safety.py - limites e regras de segurança
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
Avaliação opcional do usuário
```

## 8. Responsabilidades dos arquivos

| Arquivo | Responsabilidade |
| --- | --- |
| `main.py` | Iniciar a aplicação e coordenar o fluxo principal. |
| `interface.py` | Receber a mensagem e apresentar o resultado. |
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
- `confianca` deve ser um número entre 0 e 1.
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
- Recusar ou limitar mensagens grandes demais.
- Exibir o aviso de limitação em todas as análises.
- Em caso de dúvida, recomendar a verificação por canal oficial.

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
- deve responder `informacao_insuficiente` quando não houver contexto suficiente.

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
- poder ser instalado e executado seguindo o `README.md`.

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

- `data/casos_teste.json` com 30 casos classificados;
- arquitetura documentada;
- testes automáticos de privacidade e avaliação;
- relatórios diários preenchidos;
- resultados registrados sem dados pessoais;
- histórico de commits pequenos e compreensíveis;
- `README.md` com instruções de instalação, configuração e execução.
