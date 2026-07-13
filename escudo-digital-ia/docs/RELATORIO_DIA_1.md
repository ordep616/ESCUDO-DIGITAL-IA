# Relatório - Dia 1

## Objetivo do dia
 [ ] Definir o público principal e três situações reais em que o produto ajudaria.
 [ ] Criar o SPEC.md completo com objetivo, funcionalidades, limites e critérios de sucesso.
 [ ] Desenhar o fluxo do usuário e a arquitetura do sistema.
 [ ] Criar 30 mensagens fictícias para o conjunto de testes.
 [ ] Classificar manualmente cada mensagem antes de consultar a IA.
 [ ] Definir os campos obrigatórios da resposta estruturada.
 [ ] Criar o repositório, a estrutura de pastas e o README inicial.
 [ ] Registrar pelo menos cinco commits pequenos e compreensíveis.
## O que foi concluído
O público principal é formado por:

- estudantes;
- famílias;
- pessoas com pouca experiência digital;
- usuários que recebem mensagens suspeitas por SMS, e-mail ou aplicativos de conversa.

o SPEC.md inicial foi completo 

o fluxo do usuario e arquitetura foi desenhado no ARQUITETURA.md
 as 30 mensagens foram concluidas
  
as 30 mensagens foram classificadas 
 
 repositorio foi criado cos todos os colaboradores 

 até então foram realizados varios commits com 3 banches


## Testes executados e resultados
| Área | Quantidade | Resultado |
| --- | ---: | --- |
| Serviço de IA                  | 12     | Aprovados |
| Anonimização de CPF e telefone | 9      | Aprovados |
| Armazenamento de métricas      | 5      | Aprovados |
| Validação da resposta          | 10     | Aprovados |
| **Total**                      | **36** | **Todos aprovados** |


## Como o Codex foi utilizado

o codex foi ultilizado para realizar testes, responder duvidas pendentes,
ajudou a orgarnizar o projeto e o fluxo do sistema

## Como a API de IA foi utilizada
A API foi utilizada por meio do OpenRouter

o ai_service.py carrega os dados do .env  onde estão as keys ocultadas do github 

## Decisões tomadas pela dupla
qual modelo de IA usar 
divisao de trabalho 

## O que falta para o próximo dia

 [ ] Criar funções para ocultar CPF, telefone, e-mail, cartão, códigos e links.
 [ ] Criar testes automáticos para cada tipo de dado mascarado.
 [ ] Garantir que o texto integral não seja salvo no histórico.
 [ ] Criar o modo “Aprender”, com no mínimo dez exercícios.
 [ ] Após cada exercício, explicar os sinais encontrados.
 [ ] Adicionar avaliação “útil / não útil” às análises.
 [ ] Criar interface no Telegram ou página web simples, conforme orientação da equipe.
 [ ] Revisar linguagem para pessoas sem conhecimento técnico.

## Commits realizados

foram realizados diversos commits com 3 branches
primeiro branch foi realizado a estrutura dos arquivos dentro do projeto
segundo branch foi realizado foi realizado o README.md
no terceiro branch ocultamos o .env e colocamos a key
no quarto branch o relatorio do dia 1 foi feito
