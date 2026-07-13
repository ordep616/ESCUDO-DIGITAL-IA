# Escudo Digital IA

O Escudo Digital IA é um projeto educativo de segurança digital que analisa
mensagens fictícias ou previamente anonimizadas. seu objetivo é ajudar pessoas
a reconhecer sinais comuns de golpes, como urgência, ameaças, pedidos de
dinheiro, solicitação de códigos e imitação de instituições.

O sistema oferece orientação educativa. Ele não confirma se uma mensagem é
legítima ou fraudulenta e não substitui a verificação por canais oficiais.

## Problema que o projeto resolve

Golpes digitais costumam pressionar a vítima para agir rapidamente, clicar em
links, enviar dados pessoais ou realizar pagamentos. O projeto analisa o texto
recebido, identifica sinais de risco e retorna recomendações simples para que o
usuário possa tomar uma decisão mais segura.

O formato esperado da análise contém:

- classificação de risco;
- nível de confiança;
- sinais encontrados;
- recomendações de segurança;
- explicação em linguagem simples;
- indicação de informação insuficiente.

Mais detalhes estão disponíveis no [SPEC.md](SPEC.md).

## Estado atual

Atualmente, o projeto possui:

- anonimização local de CPF e telefone brasileiro;
- integração com o OpenRouter usando o SDK da OpenAI;
- resposta estruturada e validada em JSON;
- tratamento de timeout, autenticação e indisponibilidade da API;
- armazenamento de métricas básicas sem salvar a mensagem integral;
- testes automáticos para API, privacidade, armazenamento e validação.

Ainda não existe uma interface de terminal ou interface gráfica completa. Os
arquivos `main.py`, `interface.py`, `safety.py` e `evaluator.py` ainda precisam
ser implementados. Por isso, neste momento o projeto é executado por testes ou
por uma chamada direta aos módulos Python.

## Requisitos

- Python 3.9 ou superior;
- acesso ao terminal;
- uma chave de API do OpenRouter para chamadas reais;
- créditos e acesso ao modelo escolhido no OpenRouter.

## Instalação

Entre na pasta do projeto:

```bash
cd escudo-digital-ia
```

Crie o ambiente virtual:

```bash
python3 -m venv .venv
```

Ative o ambiente no macOS ou Linux:

```bash
source .venv/bin/activate
```

No Windows PowerShell, use:

```powershell
.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
python3 -m pip install -r requirements.txt
```

Para sair do ambiente virtual:

```bash
deactivate
```

## Configuração do `.env`

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

Preencha o `.env` desta forma:

```dotenv
OPENROUTER_API_KEY=sua-chave-do-openrouter
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=openai/gpt-5-mini
```

O arquivo `.env` está no `.gitignore` e não deve ser enviado ao Git. Nunca
coloque a chave verdadeira no `.env.example`, no README, em capturas de tela ou
em mensagens compartilhadas.

É possível confirmar que o arquivo está ignorado com:

```bash
git check-ignore -v .env
```

## Comandos disponíveis

O projeto ainda não oferece comandos próprios de uma aplicação CLI. Os
principais comandos de desenvolvimento disponíveis são:

| Comando | Finalidade |
| --- | --- |
| `python3 -m unittest discover -s tests -v` | Executar todos os testes automáticos. |
| `python3 -m unittest discover -s tests -p 'test_ai_service.py' -v` | Testar somente o serviço de IA sem chamada externa. |
| `python3 -m unittest discover -s tests -p 'test_privacy.py' -v` | Testar a anonimização de CPF e telefone. |
| `git check-ignore -v .env` | Confirmar que o arquivo com a chave está protegido pelo Git. |

## Como rodar o projeto

Como a interface principal ainda não foi implementada, executar
`python3 main.py` não inicia uma aplicação neste momento. Para verificar o
projeto sem consumir créditos, execute a suíte de testes:

```bash
python3 -m unittest discover -s tests -v
```

Uma execução correta termina com `OK`.

## Como testar a IA

O comando abaixo realiza uma chamada real ao OpenRouter com uma mensagem
fictícia e valida o JSON retornado:

```bash
python3 -B -c 'import json; from ai_service import analisar_mensagem; from prompts import SYSTEM_PROMPT_V1; from validator import validar_resposta_ia; resposta = analisar_mensagem("Mensagem fictícia: envie seu código agora para evitar o bloqueio da conta.", SYSTEM_PROMPT_V1); dados = json.loads(resposta); print(json.dumps(dados, ensure_ascii=False, indent=2)); print("JSON válido:", not validar_resposta_ia(dados))'
```

O resultado esperado inclui:

```text
JSON válido: True
```

Esse comando usa a API real e pode consumir créditos. Utilize apenas mensagens
fictícias ou anonimizadas. Não insira CPF, telefone, senha, código de
autenticação, dados bancários ou outras informações pessoais.

## Privacidade e segurança

- A chave da API deve permanecer somente no `.env`.
- A mensagem integral não deve ser salva nas métricas.
- CPF e telefone devem ser anonimizados antes da chamada à IA.
- Links recebidos não devem ser abertos ou verificados pelo sistema.
- Senhas, códigos e dados bancários nunca devem ser solicitados.
- Toda análise deve recomendar confirmação por um canal oficial.

## Limitações atuais

- A IA pode produzir classificações incorretas.
- O sistema não confirma a identidade do remetente.
- O sistema não verifica se um link é seguro.
- A anonimização atual cobre somente CPF e telefone brasileiro.
- E-mail, cartão, links e códigos de autenticação ainda não são anonimizados.
- A camada geral de segurança em `safety.py` ainda não foi implementada.
- A interface e o fluxo completo em `main.py` ainda não foram implementados.
- O avaliador de resultados ainda não foi implementado.
- O projeto depende da disponibilidade, das regras e dos créditos do OpenRouter.
- O modelo configurado precisa oferecer suporte à saída estruturada solicitada.

## Melhorias futuras

- implementar o fluxo principal em `main.py`;
- criar uma interface segura e acessível;
- ampliar a anonimização para e-mail, cartão, links e códigos;
- implementar limites de tamanho e outras regras em `safety.py`;
- integrar anonimização, IA, validação e aviso de segurança em um único fluxo;
- implementar avaliação com falsos positivos e falsos negativos;
- executar os casos fictícios de `data/casos_teste.json` automaticamente;
- adicionar testes de integração do fluxo completo;
- melhorar mensagens de erro apresentadas ao usuário;
- documentar métricas de qualidade, custo e consumo.

## Aviso

> Esta análise é educativa e pode cometer erros. Não clique em links, não envie
> senhas ou códigos e confirme a situação diretamente no aplicativo, site ou
> telefone oficial da instituição.
