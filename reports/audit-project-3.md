# Auditoria — task-manager-api

Estado: **Refatoração e reauditoria concluídas após aprovação; validação final HTTP aprovada.**

Revisão de origem: `6d1ce6248c3e956801010a89d8bdaab48029`. Inspeção realizada por Codex, com a skill `refactor-arch`; não constitui revisão humana simulada. A análise inicial anterior à criação da skill serviu de baseline, e a execução das fases 1/2 confrontou os achados com o catálogo. O código permaneceu intacto até a aprovação do plano, quando a fase 3 autorizada iniciou a refatoração documentada abaixo.

## Fase 1 — Análise

- Stack: Python / Flask 3.0.0 / Flask-SQLAlchemy 3.1.1 / SQLite.
- Domínio: Task Manager: tarefas, usuários, categorias, relatórios e login.
- Arquitetura atual: Há models/routes/services/utils, mas rotas fazem validação, regras, SQL, transações e serialização; notificações não estão ligadas às rotas.
- Escopo lido: **15 arquivos-fonte, 1158 linhas** (inclui arquivos vazios/de inicialização; exclui dependências).
- Runtime alvo para validação: Python 3.12.14 / Node 24.19.0 disponíveis no ambiente; os frameworks ainda não foram executados nesta fase.

Arquivos lidos: `app.py`, `database.py`, `models/__init__.py`, `models/category.py`, `models/task.py`, `models/user.py`, `routes/__init__.py`, `routes/report_routes.py`, `routes/task_routes.py`, `routes/user_routes.py`, `seed.py`, `services/__init__.py`, `services/notification_service.py`, `utils/__init__.py`, `utils/helpers.py`.

### Endpoints inventariados

| Método | Caminho | Localização original |
|---|---|---|
| GET | `/health` | `app.py:22` |
| GET | `/` | `app.py:26` |
| GET | `/reports/summary` | `routes/report_routes.py:12` |
| GET | `/reports/user/<int:user_id>` | `routes/report_routes.py:103` |
| GET | `/categories` | `routes/report_routes.py:157` |
| POST | `/categories` | `routes/report_routes.py:167` |
| PUT | `/categories/<int:cat_id>` | `routes/report_routes.py:190` |
| DELETE | `/categories/<int:cat_id>` | `routes/report_routes.py:211` |
| GET | `/tasks` | `routes/task_routes.py:11` |
| GET | `/tasks/<int:task_id>` | `routes/task_routes.py:65` |
| POST | `/tasks` | `routes/task_routes.py:85` |
| PUT | `/tasks/<int:task_id>` | `routes/task_routes.py:156` |
| DELETE | `/tasks/<int:task_id>` | `routes/task_routes.py:225` |
| GET | `/tasks/search` | `routes/task_routes.py:240` |
| GET | `/tasks/stats` | `routes/task_routes.py:273` |
| GET | `/users` | `routes/user_routes.py:10` |
| GET | `/users/<int:user_id>` | `routes/user_routes.py:27` |
| POST | `/users` | `routes/user_routes.py:42` |
| PUT | `/users/<int:user_id>` | `routes/user_routes.py:92` |
| DELETE | `/users/<int:user_id>` | `routes/user_routes.py:134` |
| GET | `/users/<int:user_id>/tasks` | `routes/user_routes.py:153` |
| POST | `/login` | `routes/user_routes.py:185` |

Total: **22 combinações método/caminho**, sem contar HEAD/OPTIONS automáticos. Métodos, URLs, nomes públicos e efeitos válidos serão caracterizados antes da refatoração. O comportamento inseguro não será tratado como compatibilidade obrigatória quando sua correção for aprovada.

### Baseline

Inspeção estática e comparação de hashes realizadas. Boot/endpoints ainda não executados nesta fase; dependências de execução estão sendo preparadas. Testes usarão DB temporário e loopback, sem serviços externos reais.

## Fase 2 — Achados

Resumo: **CRITICAL: 1** | **HIGH: 2** | **MEDIUM: 4** | **LOW: 3**.

### P3-01 [CRITICAL] Hash de senha exposto e derivação MD5

- Arquivo: [`task-manager-api/models/user.py:16–32`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/task-manager-api/models/user.py#L16-L32), na revisão de origem.
- Evidência: to_dict devolve password; set_password/check_password usam MD5 sem sal.
- Impacto: Cadastro, detalhe e login podem expor hash, com derivação inadequada para senha.
- Recomendação: DTO sem password e KDF adaptativa com verificação e estratégia explícita para hashes legados.
- Catálogo/playbook: AP-02 / T12.
- Aceite da correção: Senhas iguais geram hashes diferentes; verificação correta aceita, incorreta rejeita; hash nunca sai no JSON.

### P3-02 [HIGH] Rotas acumulam lógica e persistência

- Arquivo: [`task-manager-api/routes/task_routes.py:85–154`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/task-manager-api/routes/task_routes.py#L85-L154), na revisão de origem.
- Evidência: Handler valida todas as regras, consulta entidades, grava e serializa.
- Impacto: Acoplamento impede testar caso de uso fora do transporte e duplica regras em PUT.
- Recomendação: Extrair controllers/casos de uso e validação, manter Blueprint apenas como roteamento.
- Catálogo/playbook: AP-03/AP-05 / T03.
- Aceite da correção: Rotas não contêm SQL/transação; casos de uso testam sem HTTP; todos os endpoints originais funcionam.

### P3-03 [HIGH] Configuração e debug embutidos

- Arquivo: [`task-manager-api/app.py:11–15`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/task-manager-api/app.py#L11-L15), na revisão de origem.
- Evidência: SECRET_KEY fixa; app.run ativa debug em 0.0.0.0 (34); serviço SMTP tem password fixa.
- Impacto: Reuso de segredo e debug exposto tornam configuração insegura fora do laboratório.
- Recomendação: Config por ambiente, debug desabilitado por padrão, bind local e SMTP desativado sem configuração; não enviar emails durante testes.
- Catálogo/playbook: AP-02 / T02.
- Aceite da correção: Config vem do ambiente, debug é opt-in e inicialização não realiza conexão SMTP real.

### P3-04 [MEDIUM] N+1 de responsáveis e categorias

- Arquivo: [`task-manager-api/routes/task_routes.py:41–55`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/task-manager-api/routes/task_routes.py#L41-L55), na revisão de origem.
- Evidência: Lista tasks faz Query.get para User e Category a cada item.
- Impacto: Leituras crescem linearmente com quantidade e serialização duplicada.
- Recomendação: Eager loading ou consultas em lote, usando um presenter.
- Catálogo/playbook: AP-06 / T05.
- Aceite da correção: Fixtures crescentes não produzem uma consulta por item; contratos continuam com relações completas.

### P3-05 [MEDIUM] Regras de prazo e status duplicadas

- Arquivo: [`task-manager-api/routes/task_routes.py:30–39`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/task-manager-api/routes/task_routes.py#L30-L39), na revisão de origem.
- Evidência: Regra overdue repetida em detalhe (71–80), model e relatórios; listas de status também se repetem.
- Impacto: Correção precisa sincronizar múltiplos lugares.
- Recomendação: Política de domínio única com relógio injetável e constantes.
- Catálogo/playbook: AP-07 / T06.
- Aceite da correção: Create/update têm regras coerentes; tipos inválidos retornam 400 sem persistir.

### P3-06 [MEDIUM] API ORM legada/deprecated

- Arquivo: [`task-manager-api/routes/task_routes.py:65–67`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/task-manager-api/routes/task_routes.py#L65-L67), na revisão de origem.
- Evidência: Task.query.get usa Query.get, marcado legacy desde SQLAlchemy2.0; há ocorrências equivalentes em usuários/categorias.
- Impacto: Gera warnings e dificulta migração, sem significar que o endpoint está quebrado hoje.
- Recomendação: Usar db.session.get(Model,id), confirmando retorno None e identidade de sessão.
- Catálogo/playbook: AP-09 / T08.
- Aceite da correção: Busca por ID preserva sucesso/ausência e não gera LegacyAPIWarning.

### P3-07 [MEDIUM] Filtros não numéricos escapam como erro

- Arquivo: [`task-manager-api/routes/task_routes.py:260–264`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/task-manager-api/routes/task_routes.py#L260-L264), na revisão de origem.
- Evidência: int(priority/user_id) sem validação nem boundary específico.
- Impacto: Consulta inválida produz 500 em vez de erro do cliente.
- Recomendação: Validador de query e respostas 400 estáveis.
- Catálogo/playbook: AP-08 / T07.
- Aceite da correção: Erro inesperado tem resposta estável sem detalhe interno; entrada inválida não vira 500.

### P3-08 [LOW] Imports agrupados sem uso

- Arquivo: [`task-manager-api/routes/task_routes.py:6–7`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/task-manager-api/routes/task_routes.py#L6-L7), na revisão de origem.
- Evidência: json, os, sys e time não são utilizados nesse módulo.
- Impacto: Distrai da lista real de dependências.
- Recomendação: Remover imports mortos e agrupar segundo o estilo escolhido.
- Catálogo/playbook: AP-12 / T11.
- Aceite da correção: Imports/exports mortos removidos; boot e endpoints não regridem.

### P3-09 [LOW] Constantes repetidas como literais

- Arquivo: [`task-manager-api/routes/task_routes.py:96–114`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/task-manager-api/routes/task_routes.py#L96-L114), na revisão de origem.
- Evidência: Limites 3/200, prioridade 1/5 e default3 repetem políticas já declaradas em helpers.py:110–116.
- Impacto: Manutenção precisa procurar números em vários arquivos.
- Recomendação: Consolidar constantes com nomes de domínio e preservar limites.
- Catálogo/playbook: AP-10 / T09.
- Aceite da correção: Testes nos limites preservam descontos, tamanho e prioridade.

### P3-10 [LOW] Nomes p1 a p5 no relatório

- Arquivo: [`task-manager-api/routes/report_routes.py:24–28`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/task-manager-api/routes/report_routes.py#L24-L28), na revisão de origem.
- Evidência: Contadores p1…p5 dependem do leitor decorar nível/prioridade.
- Impacto: Reduz legibilidade da regra de agregação.
- Recomendação: Usar agrupamento por prioridade com nomes ao montar response.
- Catálogo/playbook: AP-11 / T10.
- Aceite da correção: Nomes locais expressivos com as mesmas chaves e URLs públicas.

### APIs obsoletas confirmadas

Query.get é legacy desde SQLAlchemy 2.0; substituição por Session.get documentada na [API oficial](https://docs.sqlalchemy.org/en/20/orm/queryguide/query.html#sqlalchemy.orm.Query.get). A base também usa datetime.utcnow (por exemplo task_routes.py:31 e models/task.py:15–16), deprecated no runtime Python 3.12 alvo: usar datetime.now(UTC), adaptando conscientemente a fronteira naive UTC do SQLite. [Documentação Python](https://docs.python.org/3.12/library/datetime.html#datetime.datetime.utcnow). Isso não é evidência de que a aplicação já deixou de funcionar.

## Plano proposto e mudança de contratos

Preservar modelos SQLAlchemy e Blueprints onde úteis. Extrair controllers/casos de uso de tarefas, usuários, categorias e relatórios; centralizar regras de validação e apresentação. Repositórios/consultas tratarão eager loading e agrupamentos. Uma factory com config explícita controlará ambiente e banco, sem apagar dados no boot.

Mudanças intencionais para revisão: retirar password/hash dos responses; substituir MD5 por KDF com estratégia de upgrade de hashes existentes; retirar secrets fixos e desabilitar debug por padrão; normalizar entradas inválidas para 400; migrar Query.get para Session.get e remover utcnow deprecated preservando semântica UTC da base. SMTP será injetável/desativado durante testes e não serão enviados emails. O token fake e ausência de autorização completa da base serão registrados como limite do laboratório, sem prometer autenticação de produção.

## Checkpoint

**Aprovação recebida em 19/10/2026:** o usuário respondeu “Aprovo os três planos; pode refatorar” após a apresentação dos relatórios. A fase 3 iniciou somente após essa resposta. Antes do checkpoint, hashes confirmavam o código intacto; somente skill e relatórios haviam sido criados.

A skill exige: “apresente o relatório concreto e o plano, então pause e peça confirmação humana antes de modificar código, configuração ou testes do projeto”. Essa etapa vem do requisito explícito do desafio, não de uma autorização de publicação.

## Fase 3 — Resultado

Refatoração aplicada nas camadas `domain`, `models`, `repositories`, `services`, `controllers`, `views` e `routes`. A reauditoria conferiu os dez achados: P3-01 DTO sem senha e hash atualizado; P3-02 regras e persistência extraídas das rotas; P3-03 configuração por factory, secrets externos e debug desligado por padrão; P3-04 relações carregadas em lote; P3-05 regras de prazo/status centralizadas; P3-06 `Session.get` e relógio UTC atualizado; P3-07 filtros inválidos respondem 400; P3-08 imports não usados removidos; P3-09 constantes nomeadas; P3-10 nomes descritivos no relatório.

Uma revisão comportamental detectou que criação de categoria sem `description` não preservava o default público vazio. `category_data` agora retorna `description: ""` em criação; atualização parcial continua incluindo somente os campos enviados. Testes verificam o default e a preservação durante update.

Validação após a reauditoria: `python -m unittest tests.test_architecture` no venv do projeto, **5/5 testes aprovados**. A execução HTTP final registrou **22/22 verificações aprovadas, 0 falhas**, cobrindo os 22 pares método/caminho inventariados. Evidências: [`evidence/http-project-3.json`](../evidence/http-project-3.json) e [`evidence/http-run-project-3.log`](../evidence/http-run-project-3.log).
