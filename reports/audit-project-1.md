# Auditoria — code-smells-project

Estado: **Refatoração e reauditoria concluídas após aprovação; validação final HTTP aprovada.**

Revisão de origem: `6d1ce6248c3e956801010a89d8bdaab48029bf30`. Inspeção realizada por Codex, com a skill `refactor-arch`; não constitui revisão humana simulada. A análise inicial anterior à criação da skill serviu de baseline, e a execução das fases 1/2 confrontou os achados com o catálogo. O código permaneceu intacto até a aprovação do plano, quando a fase 3 autorizada iniciou a refatoração documentada abaixo.

## Fase 1 — Análise

- Stack: Python / Flask 3.1.1 / flask-cors 5.0.1 / sqlite3 padrão.
- Domínio: API de e-commerce: produtos, usuários, pedidos e relatórios.
- Arquitetura atual: Separação nominal em app/controllers/models; models mistura quatro domínios e regras, controllers contêm validação e notificações, app inclui SQL administrativo.
- Escopo lido: **4 arquivos-fonte, 780 linhas** (inclui arquivos vazios/de inicialização; exclui dependências).
- Runtime alvo para validação: Python 3.12.14 / Node 24.19.0 disponíveis no ambiente; os frameworks ainda não foram executados nesta fase.

Arquivos lidos: `app.py`, `controllers.py`, `database.py`, `models.py`.

### Endpoints inventariados

| Método | Caminho | Localização original |
|---|---|---|
| GET | `/produtos` | `app.py:11` |
| GET | `/produtos/busca` | `app.py:12` |
| GET | `/produtos/<int:id>` | `app.py:13` |
| POST | `/produtos` | `app.py:14` |
| PUT | `/produtos/<int:id>` | `app.py:15` |
| DELETE | `/produtos/<int:id>` | `app.py:16` |
| GET | `/usuarios` | `app.py:18` |
| GET | `/usuarios/<int:id>` | `app.py:19` |
| POST | `/usuarios` | `app.py:20` |
| POST | `/login` | `app.py:21` |
| POST | `/pedidos` | `app.py:23` |
| GET | `/pedidos` | `app.py:24` |
| GET | `/pedidos/usuario/<int:usuario_id>` | `app.py:25` |
| PUT | `/pedidos/<int:pedido_id>/status` | `app.py:26` |
| GET | `/relatorios/vendas` | `app.py:28` |
| GET | `/health` | `app.py:30` |
| GET | `/` | `app.py:32` |
| POST | `/admin/reset-db` | `app.py:47` |
| POST | `/admin/query` | `app.py:59` |

Total: **19 combinações método/caminho**, sem contar HEAD/OPTIONS automáticos. Métodos, URLs, nomes públicos e efeitos válidos serão caracterizados antes da refatoração. O comportamento inseguro não será tratado como compatibilidade obrigatória quando sua correção for aprovada.

### Baseline

Inspeção estática e comparação de hashes realizadas. Boot/endpoints ainda não executados nesta fase; dependências de execução estão sendo preparadas. Testes usarão DB temporário e loopback, sem serviços externos reais.

## Fase 2 — Achados

Resumo: **CRITICAL: 3** | **HIGH: 2** | **MEDIUM: 3** | **LOW: 3**.

### P1-01 [CRITICAL] SQL composto com entrada externa

- Arquivo: [`code-smells-project/models.py:105–111`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/code-smells-project/models.py#L105-L111), na revisão de origem.
- Evidência: Email e senha são concatenados em SELECT; busca também concatena termo/categoria nas linhas 285–299.
- Impacto: Entrada controla sintaxe SQL e pode alterar o predicado de autenticação. Não é necessário executar ataque para confirmar o fluxo.
- Recomendação: Usar parâmetros em toda consulta e testar apóstrofos como dados.
- Catálogo/playbook: AP-01 / T01.
- Aceite da correção: Apóstrofos em busca/cadastro/login são tratados como dados, sem mudar predicado SQL.

### P1-02 [CRITICAL] Console SQL e reset sem autorização

- Arquivo: [`code-smells-project/app.py:47–78`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/code-smells-project/app.py#L47-L78), na revisão de origem.
- Evidência: POST /admin/query executa SQL recebido no body e /admin/reset-db apaga tabelas; não há guard.
- Impacto: Qualquer chamador pode ler ou modificar o banco.
- Recomendação: Manter rotas administrativas com autenticação explícita; restringir query a inspeção de leitura e bloquear instruções arbitrárias. Documentar mudança de segurança.
- Catálogo/playbook: AP-13 / T13.
- Aceite da correção: Anônimo recebe 401; token administrativo configurado opera apenas ações permitidas no banco descartável; SQL de escrita enviado ao console é recusado.

### P1-03 [CRITICAL] Senha e secret expostas em respostas

- Arquivo: [`code-smells-project/models.py:72–101`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/code-smells-project/models.py#L72-L101), na revisão de origem.
- Evidência: Serialização de usuários inclui senha; controllers.py:285–289 revela secret_key no health.
- Impacto: Endpoints expõem material de autenticação e segredo de aplicação.
- Recomendação: Usar DTOs públicos sem senha/hash/secret e armazenar hashes adaptativos; configurar secrets externamente.
- Catálogo/playbook: AP-02 / T02.
- Aceite da correção: Responses e logs não revelam password/senha/hash/secret/card; fluxo válido continua funcionando.

### P1-04 [HIGH] Conexão SQLite global compartilhada

- Arquivo: [`code-smells-project/database.py:4–10`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/code-smells-project/database.py#L4-L10), na revisão de origem.
- Evidência: Uma conexão mutável global é criada com check_same_thread=False.
- Impacto: Requisições concorrentes compartilham transações e estado; não há fechamento por request.
- Recomendação: Conexão por unidade de trabalho/contexto, teardown e rollback explícitos.
- Catálogo/playbook: AP-04 / T04.
- Aceite da correção: Falha injetada na segunda escrita reverte a primeira e a conexão é fechada; requests isolados não compartilham unidade transacional.

### P1-05 [HIGH] Pedidos misturam cálculo e persistência sem unidade transacional clara

- Arquivo: [`code-smells-project/models.py:133–169`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/code-smells-project/models.py#L133-L169), na revisão de origem.
- Evidência: Valida/calcúla totais, insere itens e atualiza estoque em loops, com commit final e sem rollback de exceção.
- Impacto: Falhas deixam transação parcialmente aplicada na conexão e duplicatas/quantidades negativas não são validadas.
- Recomendação: Separar caso de uso de pedido e repositórios; validar itens e agregar duplicatas antes de uma transação.
- Catálogo/playbook: AP-03/AP-05 / T03.
- Aceite da correção: Rotas não contêm SQL/transação; casos de uso testam sem HTTP; todos os endpoints originais funcionam.

### P1-06 [MEDIUM] Consultas N+1 na montagem de pedidos

- Arquivo: [`code-smells-project/models.py:171–233`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/code-smells-project/models.py#L171-L233), na revisão de origem.
- Evidência: Cada pedido consulta itens e cada item busca nome de produto novamente.
- Impacto: Número de queries cresce com pedidos e itens.
- Recomendação: JOIN/busca em lote e agrupamento preservando formato atual.
- Catálogo/playbook: AP-06 / T05.
- Aceite da correção: Fixtures crescentes não produzem uma consulta por item; contratos continuam com relações completas.

### P1-07 [MEDIUM] Validação de produto duplicada e divergente

- Arquivo: [`code-smells-project/controllers.py:24–96`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/code-smells-project/controllers.py#L24-L96), na revisão de origem.
- Evidência: Create verifica comprimento/categoria; update repete parte mas não essas regras.
- Impacto: Mesmo produto obedece restrições diferentes conforme endpoint.
- Recomendação: Validador compartilhado e controlador fino.
- Catálogo/playbook: AP-07 / T06.
- Aceite da correção: Create/update têm regras coerentes; tipos inválidos retornam 400 sem persistir.

### P1-08 [MEDIUM] Conversão de filtro produz erro interno

- Arquivo: [`code-smells-project/controllers.py:111–126`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/code-smells-project/controllers.py#L111-L126), na revisão de origem.
- Evidência: float(preco_min/max) sem tratamento específico; exceção é exposta em 500.
- Impacto: Entrada inválida vira falha de servidor e vaza detalhe interno.
- Recomendação: Converter na fronteira, retornar 400 e centralizar erro inesperado.
- Catálogo/playbook: AP-08 / T07.
- Aceite da correção: Erro inesperado tem resposta estável sem detalhe interno; entrada inválida não vira 500.

### P1-09 [LOW] Faixas de desconto como números sem nome

- Arquivo: [`code-smells-project/models.py:256–262`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/code-smells-project/models.py#L256-L262), na revisão de origem.
- Evidência: 10000/5000/1000 e 0.1/0.05/0.02 aparecem soltos no cálculo.
- Impacto: Difícil localizar a política e revisar fronteiras.
- Recomendação: Nomear tabela de faixas preservando comparadores e valores, testar limites.
- Catálogo/playbook: AP-10 / T09.
- Aceite da correção: Testes nos limites preservam descontos, tamanho e prioridade.

### P1-10 [LOW] Parâmetro id sombreia função nativa

- Arquivo: [`code-smells-project/controllers.py:14–16`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/code-smells-project/controllers.py#L14-L16), na revisão de origem.
- Evidência: Parâmetro genérico id usado em handler de produto e outros handlers.
- Impacto: Nome não comunica domínio e sombreia built-in Python.
- Recomendação: Renomear internamente para product_id/user_id sem mudar caminhos HTTP.
- Catálogo/playbook: AP-11 / T10.
- Aceite da correção: Nomes locais expressivos com as mesmas chaves e URLs públicas.

### P1-11 [LOW] Imports sem uso

- Arquivo: [`code-smells-project/database.py:1–2`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/code-smells-project/database.py#L1-L2), na revisão de origem.
- Evidência: os importado sem uso; models.py também importa sqlite3 sem usar.
- Impacto: Ruído dificulta perceber dependências reais.
- Recomendação: Remover imports mortos após testar importação e boot.
- Catálogo/playbook: AP-12 / T11.
- Aceite da correção: Imports/exports mortos removidos; boot e endpoints não regridem.

### APIs obsoletas

Nenhum uso de API formally deprecated foi confirmado no escopo analisado deste projeto. O catálogo ainda inclui essa detecção. Não se classifica código antigo, callback ou Buffer.from como API obsoleta sem fonte.

## Plano proposto e mudança de contratos

Config e factory Flask serão separados do entry point; um pacote de domínio terá models/repositories para produtos, usuários e pedidos, controllers de coordenação e views/routes para HTTP. Validação e error boundary ficarão compartilhados. O banco terá lifecycle por contexto e operações de pedido transacionais. Manteremos URLs, nomes dos campos e envelopes válidos existentes.

Mudanças intencionais para revisão: remover senha/hash e secret de responses; rejeitar tipos inválidos com 400; exigir token administrativo configurado nas duas rotas /admin; permitir apenas inspeção de leitura restrita em /admin/query, sem SQL arbitrário; gerar hashes de senhas e tratar dados legados por migração controlada; não ativar debug por padrão. Reset permanece uma ação explícita autenticada, nunca executada em banco não descartável nos testes.

## Checkpoint

**Aprovação recebida em 19/10/2026:** o usuário respondeu “Aprovo os três planos; pode refatorar” após a apresentação dos relatórios. A fase 3 iniciou somente após essa resposta. Antes do checkpoint, hashes confirmavam o código intacto; somente skill e relatórios haviam sido criados.

A skill exige: “apresente o relatório concreto e o plano, então pause e peça confirmação humana antes de modificar código, configuração ou testes do projeto”. Essa etapa vem do requisito explícito do desafio, não de uma autorização de publicação.

## Fase 3 — Resultado

Refatoração aplicada nas camadas `domain`, `models`, `services`, `controllers` e `views`. A reauditoria conferiu os 11 achados: P1-01 consultas parametrizadas; P1-02 rotas administrativas autenticadas e consulta de leitura restrita; P1-03 DTOs sem senha e hash de senha; P1-04 conexão por contexto de requisição; P1-05 pedido transacional e estoque agregado; P1-06 consultas em lote; P1-07 validação compartilhada; P1-08 filtros inválidos respondem 400; P1-09 faixas nomeadas; P1-10 nomes de domínio nos handlers; P1-11 imports mortos removidos.

Uma revisão comportamental posterior detectou que categoria JSON não textual e status de pedido como lista/objeto levantavam `TypeError` e viravam 500. A validação agora confirma `str` antes de consultar os conjuntos permitidos. Também detectou que `text()` removia espaços de senhas; cadastro e login agora validam tipo e comprimento sem normalizar o segredo, preservando compatibilidade com senhas legadas que contêm espaços.

Validação após a reauditoria: `python -m unittest tests.test_architecture` no venv do projeto, **5/5 testes aprovados**. A execução HTTP final registrou **20/20 verificações aprovadas, 0 falhas**, cobrindo os 19 pares método/caminho inventariados e uma verificação adicional. Evidências: [`evidence/http-project-1.json`](../evidence/http-project-1.json) e [`evidence/http-run-project-1.log`](../evidence/http-run-project-1.log).
