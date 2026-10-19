# Estrutura MVC Lab

Uma skill de auditoria e refatoração arquitetural aplicada a três backends legados. As três refatorações foram implementadas após aprovação dos planos, e uma reauditoria independente levou a correções adicionais nos projetos 1 e 3.

## Análise Manual

A expressão é o nome exigido pelo desafio. A inspeção inicial do código foi realizada pelo agente Codex antes da criação da skill; ela não foi uma análise feita pelo usuário. Em 19/10/2026, o usuário revisou e autorizou os três planos com a frase: “Aprovo os três planos; pode refatorar”. A fase 3 foi executada após essa aprovação. As linhas referem-se ao commit original `6d1ce6248c3e956801010a89d8bdaab48029bf30`.

### code-smells-project

| ID | Severidade | Problema e relevância | Localização original |
|---|---|---|---|
| P1-01 | CRITICAL | SQL composto com entrada externa: Entrada controla sintaxe SQL e pode alterar o predicado de autenticação. Não é necessário executar ataque para confirmar o fluxo. | `code-smells-project/models.py:105–111` |
| P1-02 | CRITICAL | Console SQL e reset sem autorização: Qualquer chamador pode ler ou modificar o banco. | `code-smells-project/app.py:47–78` |
| P1-03 | CRITICAL | Senha e secret expostas em respostas: Endpoints expõem material de autenticação e segredo de aplicação. | `code-smells-project/models.py:72–101` |
| P1-04 | HIGH | Conexão SQLite global compartilhada: Requisições concorrentes compartilham transações e estado; não há fechamento por request. | `code-smells-project/database.py:4–10` |
| P1-05 | HIGH | Pedidos misturam cálculo e persistência sem unidade transacional clara: Falhas deixam transação parcialmente aplicada na conexão e duplicatas/quantidades negativas não são validadas. | `code-smells-project/models.py:133–169` |
| P1-06 | MEDIUM | Consultas N+1 na montagem de pedidos: Número de queries cresce com pedidos e itens. | `code-smells-project/models.py:171–233` |
| P1-07 | MEDIUM | Validação de produto duplicada e divergente: Mesmo produto obedece restrições diferentes conforme endpoint. | `code-smells-project/controllers.py:24–96` |
| P1-08 | MEDIUM | Conversão de filtro produz erro interno: Entrada inválida vira falha de servidor e vaza detalhe interno. | `code-smells-project/controllers.py:111–126` |
| P1-09 | LOW | Faixas de desconto como números sem nome: Difícil localizar a política e revisar fronteiras. | `code-smells-project/models.py:256–262` |
| P1-10 | LOW | Parâmetro id sombreia função nativa: Nome não comunica domínio e sombreia built-in Python. | `code-smells-project/controllers.py:14–16` |
| P1-11 | LOW | Imports sem uso: Ruído dificulta perceber dependências reais. | `code-smells-project/database.py:1–2` |

[Relatório completo e plano de correção](reports/audit-project-1.md).

### ecommerce-api-legacy

| ID | Severidade | Problema e relevância | Localização original |
|---|---|---|---|
| P2-01 | CRITICAL | God Class une toda a aplicação: Viola separação completa de responsabilidades e dificulta testes isolados. | `ecommerce-api-legacy/src/AppManager.js:4–138` |
| P2-02 | CRITICAL | Cartão e chave em log: Logs e código expõem dados sensíveis do pagamento simulado. | `ecommerce-api-legacy/src/AppManager.js:43–46` |
| P2-03 | HIGH | Hash próprio previsível e colidente: Muitas senhas produzem mesmo valor e não há sal/custo apropriado. | `ecommerce-api-legacy/src/utils.js:17–22` |
| P2-04 | HIGH | Checkout sem transação: Erro intermediário deixa matrícula sem pagamento ou usuário criado para checkout recusado. | `ecommerce-api-legacy/src/AppManager.js:50–71` |
| P2-05 | MEDIUM | Relatório com fan-out de queries: N+1 e coordenação manual por contadores aumentam custo e complexidade. | `ecommerce-api-legacy/src/AppManager.js:83–126` |
| P2-06 | MEDIUM | Erros de callbacks ignorados: Requisição pode falhar sem resposta consistente; delete também ignora err (131–136). | `ecommerce-api-legacy/src/AppManager.js:92–106` |
| P2-07 | MEDIUM | Entrada sem validação de tipo: Payload sintaticamente JSON válido pode causar TypeError ou cadastro inválido. | `ecommerce-api-legacy/src/AppManager.js:29–46` |
| P2-08 | MEDIUM | Exclusão deixa relações órfãs: Relatório perde integridade referencial. | `ecommerce-api-legacy/src/AppManager.js:131–136` |
| P2-09 | LOW | Variáveis abreviadas escondem domínio: Leitura e revisão de pagamento ficam frágeis. | `ecommerce-api-legacy/src/AppManager.js:29–33` |
| P2-10 | LOW | Código morto de faturamento global: Sugere duas fontes de verdade sem função real. | `ecommerce-api-legacy/src/utils.js:9–10` |

[Relatório completo e plano de correção](reports/audit-project-2.md).

### task-manager-api

| ID | Severidade | Problema e relevância | Localização original |
|---|---|---|---|
| P3-01 | CRITICAL | Hash de senha exposto e derivação MD5: Cadastro, detalhe e login podem expor hash, com derivação inadequada para senha. | `task-manager-api/models/user.py:16–32` |
| P3-02 | HIGH | Rotas acumulam lógica e persistência: Acoplamento impede testar caso de uso fora do transporte e duplica regras em PUT. | `task-manager-api/routes/task_routes.py:85–154` |
| P3-03 | HIGH | Configuração e debug embutidos: Reuso de segredo e debug exposto tornam configuração insegura fora do laboratório. | `task-manager-api/app.py:11–15` |
| P3-04 | MEDIUM | N+1 de responsáveis e categorias: Leituras crescem linearmente com quantidade e serialização duplicada. | `task-manager-api/routes/task_routes.py:41–55` |
| P3-05 | MEDIUM | Regras de prazo e status duplicadas: Correção precisa sincronizar múltiplos lugares. | `task-manager-api/routes/task_routes.py:30–39` |
| P3-06 | MEDIUM | API ORM legada/deprecated: Gera warnings e dificulta migração, sem significar que o endpoint está quebrado hoje. | `task-manager-api/routes/task_routes.py:65–67` |
| P3-07 | MEDIUM | Filtros não numéricos escapam como erro: Consulta inválida produz 500 em vez de erro do cliente. | `task-manager-api/routes/task_routes.py:260–264` |
| P3-08 | LOW | Imports agrupados sem uso: Distrai da lista real de dependências. | `task-manager-api/routes/task_routes.py:6–7` |
| P3-09 | LOW | Constantes repetidas como literais: Manutenção precisa procurar números em vários arquivos. | `task-manager-api/routes/task_routes.py:96–114` |
| P3-10 | LOW | Nomes p1 a p5 no relatório: Reduz legibilidade da regra de agregação. | `task-manager-api/routes/report_routes.py:24–28` |

[Relatório completo e plano de correção](reports/audit-project-3.md).

## Construção da Skill

A skill `refactor-arch` tem três fases sequenciais: detectar stack, auditar e pausar para revisão, refatorar/validar após confirmação. O entry point carrega cinco referências por necessidade: heurísticas de projeto, catálogo de 14 padrões, template de relatório, responsabilidades MVC e playbook com 14 transformações antes/depois.

O catálogo veio dos problemas observados, incluindo SQL interpolado, exposição de segredos, mistura de responsabilidades, transações, N+1, validações, erros, APIs obsoletas, nomes e políticas numéricas. A skill descreve responsabilidades e evidências, não uma árvore fixa de Flask. Exemplos em Python e JavaScript demonstram transformação; outras stacks usam suas convenções.

A versão está em `.agents/skills/refactor-arch/` dentro de cada um dos três projetos. As cópias são iguais. O caminho e a invocação seguem a [documentação oficial de skills do Codex](https://learn.chatgpt.com/docs/build-skills), consultada em 19/10/2026. Foi usada a skill de criação de skills do ambiente; nenhum serviço externo de pagamento ou email foi acionado.

## Resultados

- Projeto 1: 4 arquivos/780 linhas, 19 endpoints; 3 CRITICAL, 2 HIGH, 3 MEDIUM, 3 LOW.
- Projeto 2: 3 arquivos/180 linhas, 3 endpoints; 2 CRITICAL, 2 HIGH, 4 MEDIUM, 2 LOW.
- Projeto 3: 15 arquivos/1158 linhas, 22 endpoints; 1 CRITICAL, 2 HIGH, 4 MEDIUM, 3 LOW.

Os achados e a disposição por ID estão nos relatórios individuais. A reauditoria encontrou e corrigiu três regressões comportamentais: JSON com categoria/status não textual agora retorna 400; senha mantém espaços literais no cadastro/login e rejeita tipos/comprimentos inválidos; criação de categoria sem descrição restaura `description: ""`, e update parcial preserva a descrição existente. As três suítes locais passaram, **15/15 testes** no total (5 por projeto).

Os arquivos `evidence/http-project-{1,2,3}.json` registram a execução HTTP final após as correções: 20/20 verificações no projeto 1, 3/3 no projeto 2 e 22/22 no projeto 3, sem falhas. O projeto 1 inclui uma verificação adicional além dos 19 pares método/caminho inventariados. Os resumos das execuções estão em `evidence/http-run-project-{1,2,3}.log`. Nenhum commit, publicação, envio à avaliação ou operação GitHub foi realizado.

## Como Executar

Pré-requisitos: Codex com suporte a skills, Python compatível com os requirements dos projetos Flask e Node.js para o projeto Express. As dependências e configurações de cada aplicação serão descritas junto à execução da refatoração.

No diretório de cada projeto, abra Codex e invoque a skill:

```text
$refactor-arch Audite este projeto e apresente o relatório antes de refatorar.
```

A skill também pode ser citada por seu arquivo `SKILL.md`. Não é necessário chamar `claude /refactor-arch`; esse era apenas o exemplo do curso. Em uma nova aplicação, revise a fase 2 e confirme o plano concreto antes de executar a fase 3, que inicia a aplicação com banco descartável e verifica os endpoints inventariados.
