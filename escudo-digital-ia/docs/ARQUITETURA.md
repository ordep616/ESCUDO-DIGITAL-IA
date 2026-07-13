# Arquitetura do Escudo Digital IA

## 1. Visão geral

O Escudo Digital IA recebe uma mensagem fictícia ou anonimizada, protege os dados sensíveis, aplica regras de segurança, consulta a API de inteligência artificial e valida a resposta antes de apresentá-la ao usuário.

A aplicação separa cada responsabilidade em um módulo para facilitar testes, manutenção e revisão de segurança.

## 2. Fluxo principal

```text
USUÁRIO
   |
   v
INTERFACE.PY
Recebe a mensagem e exibe o aviso de segurança
   |
   v
PRIVACY.PY
Oculta CPF, telefone, e-mail, cartão, códigos e links
   |
   v
SAFETY.PY
Verifica tamanho, conteúdo e limites de segurança
   |
   v
AI_SERVICE.PY + PROMPTS.PY
Envia somente o conteúdo anonimizado para a API
   |
   v
VALIDATOR.PY
Confere campos, tipos e valores da resposta JSON
   |
   v
INTERFACE.PY
Apresenta classificação, sinais, recomendações e limitações
   |
   v
EVALUATOR.PY + STORAGE.PY
Compara resultados e registra somente métricas permitidas
```

## 3. Responsabilidades dos componentes

| Componente | Responsabilidade |
| --- | --- |
| `main.py` | Iniciar a aplicação e coordenar o fluxo principal. |
| `interface.py` | Receber a mensagem, exibir avisos e apresentar o resultado. |
| `privacy.py` | Localizar e ocultar dados pessoais antes do uso da API. |
| `safety.py` | Aplicar limites de tamanho e regras de segurança. |
| `prompts.py` | Manter as versões dos prompts e os limites da IA. |
| `ai_service.py` | Comunicar-se com a API e tratar falhas externas. |
| `validator.py` | Validar o formato e os campos da resposta estruturada. |
| `evaluator.py` | Comparar a classificação obtida com a classificação esperada. |
| `storage.py` | Armazenar somente métricas e dados permitidos. |
| `data/casos_teste.json` | Manter os 30 casos fictícios e suas classificações esperadas. |
| `data/resultados.json` | Armazenar resultados e métricas sem mensagens integrais. |

## 4. Fluxo de dados

1. O usuário insere uma mensagem fictícia ou previamente anonimizada.
2. A interface alerta para não enviar dados pessoais, senhas ou códigos reais.
3. `privacy.py` substitui informações sensíveis por marcadores.
4. `safety.py` verifica o tamanho e as regras de segurança.
5. `prompts.py` fornece as instruções de classificação e os limites da IA.
6. `ai_service.py` envia somente a versão anonimizada para a API.
7. `validator.py` verifica se a resposta contém todos os campos obrigatórios.
8. A interface apresenta a análise educativa e o aviso de limitação.
9. Se o usuário avaliar a análise, `storage.py` registra apenas a métrica permitida.

## 5. Dados enviados à API

A API deve receber somente o texto depois da anonimização. Exemplos de substituição:

| Dado encontrado | Marcador enviado à API |
| --- | --- |
| CPF | `[CPF OCULTADO]` |
| Telefone | `[TELEFONE OCULTADO]` |
| E-mail | `[E-MAIL OCULTADO]` |
| Cartão | `[CARTÃO OCULTADO]` |
| Código | `[CÓDIGO OCULTADO]` |
| Link | `[LINK OCULTADO]` |

O texto integral recebido não deve ser armazenado em arquivos de resultados ou histórico.

## 6. Formato de saída

Depois da validação, a aplicação deve trabalhar com uma estrutura semelhante a:

```json
{
  "classificacao": "alto_risco",
  "confianca": 0.92,
  "sinais": ["urgencia", "pedido_de_senha"],
  "recomendacoes": ["nao_clicar", "usar_canal_oficial"],
  "explicacao_simples": "A mensagem cria pressão e solicita uma informação sigilosa.",
  "informacao_insuficiente": false
}
```

## 7. Tratamento de falhas

| Falha | Comportamento esperado |
| --- | --- |
| Dados sensíveis encontrados | Ocultar os dados antes de chamar a API. |
| Mensagem vazia | Recusar a análise e orientar o usuário. |
| Mensagem grande demais | Recusar ou limitar localmente, sem envio indevido. |
| Timeout da API | Informar indisponibilidade sem inventar uma resposta. |
| Erro de autenticação | Mostrar erro de configuração sem revelar a chave. |
| API indisponível | Orientar o usuário a tentar novamente mais tarde. |
| JSON inválido ou incompleto | Rejeitar a resposta e registrar uma resposta inválida. |
| Contexto insuficiente | Usar a classificação `informacao_insuficiente`. |

## 8. Limites de segurança

- A chave da API deve permanecer no arquivo `.env`.
- O arquivo `.env` não pode ser enviado ao Git.
- Links recebidos não devem ser abertos ou verificados.
- A aplicação não deve solicitar senhas, códigos ou dados bancários.
- A resposta não deve incentivar cliques, pagamentos ou compartilhamento de dados.
- Toda análise deve exibir o aviso de que a IA pode cometer erros.
- Em caso de dúvida, o sistema deve recomendar a verificação por canal oficial.

## 9. Fluxo de avaliação

```text
CASOS DE TESTE
   |
   v
EVALUATOR.PY
Compara resultado esperado e resultado obtido
   |
   +--> Acerto
   +--> Falso positivo
   +--> Falso negativo
   +--> Resposta inválida
   |
   v
STORAGE.PY
Registra somente métricas permitidas
```

Falsos negativos devem receber prioridade máxima, pois representam mensagens perigosas classificadas como seguras.
