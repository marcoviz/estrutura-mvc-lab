# Auditoria — ecommerce-api-legacy

Estado: **Refatoração e reauditoria concluídas após aprovação; validação final HTTP aprovada.**

Revisão de origem: `6d1ce6248c3e956801010a89d8bdaab48029bf30`. Inspeção realizada por Codex, com a skill `refactor-arch`; não constitui revisão humana simulada. A análise inicial anterior à criação da skill serviu de baseline, e a execução das fases 1/2 confrontou os achados com o catálogo. O código permaneceu intacto até a aprovação do plano, quando a fase 3 autorizada iniciou a refatoração documentada abaixo.

## Fase 1 — Análise

Registro da análise anterior à implementação; as afirmações de execução pendente abaixo descrevem aquele momento. Os resultados posteriores estão na Fase 3 e no checklist final.

- Stack: JavaScript CommonJS / Express / sqlite3; versões exatas verificadas no package-lock.
- Domínio: LMS: checkout, matrícula, pagamento simulado e relatório financeiro.
- Arquitetura atual: God Class AppManager contém schema/seeds, rotas, checkout, acesso SQL e agregação; utils mistura configuração, cache e criptografia.
- Escopo lido: **3 arquivos-fonte, 180 linhas** (inclui arquivos vazios/de inicialização; exclui dependências).
- Runtime alvo para validação: Python 3.12.14 / Node 24.19.0 disponíveis no ambiente; os frameworks ainda não foram executados nesta fase.
- Lock: Express 4.22.1 e sqlite3 5.1.7; package.json permite versões compatíveis.

Arquivos lidos: `src/AppManager.js`, `src/app.js`, `src/utils.js`.

### Endpoints inventariados

| Método | Caminho | Localização original |
|---|---|---|
| POST | `/api/checkout` | `src/AppManager.js:28` |
| GET | `/api/admin/financial-report` | `src/AppManager.js:80` |
| DELETE | `/api/users/:id` | `src/AppManager.js:131` |

Total: **3 combinações método/caminho**, sem contar HEAD/OPTIONS automáticos. Métodos, URLs, nomes públicos e efeitos válidos serão caracterizados antes da refatoração. O comportamento inseguro não será tratado como compatibilidade obrigatória quando sua correção for aprovada.

### Baseline

Inspeção estática e comparação de hashes realizadas. Boot/endpoints ainda não executados nesta fase; dependências de execução estão sendo preparadas. Testes usarão DB temporário e loopback, sem serviços externos reais.

## Fase 2 — Achados

Resumo: **CRITICAL: 2** | **HIGH: 2** | **MEDIUM: 4** | **LOW: 2**.

### P2-01 [CRITICAL] God Class une toda a aplicação

- Arquivo: [`ecommerce-api-legacy/src/AppManager.js:4–138`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/ecommerce-api-legacy/src/AppManager.js#L4-L138), na revisão de origem.
- Evidência: AppManager cria banco, configura rotas e executa checkout/relatório/exclusão.
- Impacto: Viola separação completa de responsabilidades e dificulta testes isolados.
- Recomendação: Separar config, models/repositories, controllers, routes e serviço de checkout.
- Catálogo/playbook: AP-03/AP-05 / T03.
- Aceite da correção: Rotas não contêm SQL/transação; casos de uso testam sem HTTP; todos os endpoints originais funcionam.

### P2-02 [CRITICAL] Cartão e chave em log

- Arquivo: [`ecommerce-api-legacy/src/AppManager.js:43–46`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/ecommerce-api-legacy/src/AppManager.js#L43-L46), na revisão de origem.
- Evidência: Log interpola card e config.paymentGatewayKey; utils.js:1–6 guarda credenciais fixas.
- Impacto: Logs e código expõem dados sensíveis do pagamento simulado.
- Recomendação: Remover dados sensíveis do log e ler configuração externa, sem conectar gateway real.
- Catálogo/playbook: AP-02 / T02.
- Aceite da correção: Responses e logs não revelam password/senha/hash/secret/card; fluxo válido continua funcionando.

### P2-03 [HIGH] Hash próprio previsível e colidente

- Arquivo: [`ecommerce-api-legacy/src/utils.js:17–22`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/ecommerce-api-legacy/src/utils.js#L17-L22), na revisão de origem.
- Evidência: Repete dois caracteres base64 e corta para dez; não é derivação segura de senha.
- Impacto: Muitas senhas produzem mesmo valor e não há sal/custo apropriado.
- Recomendação: Usar scrypt com sal aleatório e formato versionado; eliminar senha default de checkout.
- Catálogo/playbook: AP-02 / T12.
- Aceite da correção: Senhas iguais geram hashes diferentes; verificação correta aceita, incorreta rejeita; hash nunca sai no JSON.

### P2-04 [HIGH] Checkout sem transação

- Arquivo: [`ecommerce-api-legacy/src/AppManager.js:50–71`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/ecommerce-api-legacy/src/AppManager.js#L50-L71), na revisão de origem.
- Evidência: Usuário, matrícula, pagamento e auditoria são gravados separadamente.
- Impacto: Erro intermediário deixa matrícula sem pagamento ou usuário criado para checkout recusado.
- Recomendação: Validar antes das escritas e envolver conjunto em transação com rollback; não pagar externamente no teste.
- Catálogo/playbook: AP-04 / T04.
- Aceite da correção: Falha injetada na segunda escrita reverte a primeira e a conexão é fechada; requests isolados não compartilham unidade transacional.

### P2-05 [MEDIUM] Relatório com fan-out de queries

- Arquivo: [`ecommerce-api-legacy/src/AppManager.js:83–126`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/ecommerce-api-legacy/src/AppManager.js#L83-L126), na revisão de origem.
- Evidência: Loop de cursos, loop de matrículas, queries de usuário e pagamento por matrícula.
- Impacto: N+1 e coordenação manual por contadores aumentam custo e complexidade.
- Recomendação: Consulta JOIN única e agrupamento por curso.
- Catálogo/playbook: AP-06 / T05.
- Aceite da correção: Fixtures crescentes não produzem uma consulta por item; contratos continuam com relações completas.

### P2-06 [MEDIUM] Erros de callbacks ignorados

- Arquivo: [`ecommerce-api-legacy/src/AppManager.js:92–106`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/ecommerce-api-legacy/src/AppManager.js#L92-L106), na revisão de origem.
- Evidência: enrollments.length é acessado antes de tratar err; erros internos podem lançar fora do fluxo HTTP.
- Impacto: Requisição pode falhar sem resposta consistente; delete também ignora err (131–136).
- Recomendação: Promisificar acesso SQL e centralizar middleware de erro assíncrono.
- Catálogo/playbook: AP-08 / T07.
- Aceite da correção: Erro inesperado tem resposta estável sem detalhe interno; entrada inválida não vira 500.

### P2-07 [MEDIUM] Entrada sem validação de tipo

- Arquivo: [`ecommerce-api-legacy/src/AppManager.js:29–46`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/ecommerce-api-legacy/src/AppManager.js#L29-L46), na revisão de origem.
- Evidência: card pode ser número; startsWith assume string; course id e senha não têm validação de tipo.
- Impacto: Payload sintaticamente JSON válido pode causar TypeError ou cadastro inválido.
- Recomendação: Schema/validação de fronteira com 400 previsível e mesmos nomes públicos.
- Catálogo/playbook: AP-07 / T06.
- Aceite da correção: Create/update têm regras coerentes; tipos inválidos retornam 400 sem persistir.

### P2-08 [MEDIUM] Exclusão deixa relações órfãs

- Arquivo: [`ecommerce-api-legacy/src/AppManager.js:131–136`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/ecommerce-api-legacy/src/AppManager.js#L131-L136), na revisão de origem.
- Evidência: Deleta usuário sem limpar matrículas/pagamentos; schema não define FKs (12–16).
- Impacto: Relatório perde integridade referencial.
- Recomendação: Definir política transacional de exclusão em cascata das relações vinculadas e testar.
- Catálogo/playbook: AP-14 / T14.
- Aceite da correção: Exclusão limpa somente relações vinculadas em transação e não deixa órfãos.

### P2-09 [LOW] Variáveis abreviadas escondem domínio

- Arquivo: [`ecommerce-api-legacy/src/AppManager.js:29–33`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/ecommerce-api-legacy/src/AppManager.js#L29-L33), na revisão de origem.
- Evidência: u/e/p/cid/cc obscurecem significado local.
- Impacto: Leitura e revisão de pagamento ficam frágeis.
- Recomendação: Usar nomes locais userName/email/password/courseId/card; preservar campos externos usr/eml/pwd/c_id/card.
- Catálogo/playbook: AP-11 / T10.
- Aceite da correção: Nomes locais expressivos com as mesmas chaves e URLs públicas.

### P2-10 [LOW] Código morto de faturamento global

- Arquivo: [`ecommerce-api-legacy/src/utils.js:9–10`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill/blob/6d1ce6248c3e956801010a89d8bdaab48029bf30/ecommerce-api-legacy/src/utils.js#L9-L10), na revisão de origem.
- Evidência: totalRevenue inicializado/exportado e importado sem uso no AppManager.
- Impacto: Sugere duas fontes de verdade sem função real.
- Recomendação: Remover variável e import; calcular receita a partir de dados persistidos.
- Catálogo/playbook: AP-12 / T11.
- Aceite da correção: Imports/exports mortos removidos; boot e endpoints não regridem.

### APIs obsoletas

Nenhum uso de API formally deprecated foi confirmado no escopo analisado deste projeto. O catálogo ainda inclui essa detecção. Não se classifica código antigo, callback ou Buffer.from como API obsoleta sem fonte.

## Plano proposto e mudança de contratos

Manter Express, CommonJS, sqlite3 e os três endpoints. Separar config/DB, repositórios, serviço transacional de checkout, controllers e routes. O gateway continuará uma simulação local que aceita cartão iniciado por 4; não haverá integração de pagamento real. O relatório será agrupado a partir de consulta em lote.

Mudanças intencionais para revisão: retirar cartão/chave dos logs e credenciais do código; exigir senha explícita para criação em checkout em vez do default oculto; validar tipos; usar scrypt; excluir matrículas e pagamentos ligados ao usuário na mesma transação; corrigir falhas de callback para resposta controlada. As chaves públicas usr/eml/pwd/c_id/card e a resposta de checkout permanecem. A proteção de autenticação dos endpoints não é ampliada implicitamente para uma plataforma de identidade nova; o caráter de laboratório será documentado.

## Checkpoint

**Aprovação recebida em 19/10/2026:** o usuário respondeu “Aprovo os três planos; pode refatorar” após a apresentação dos relatórios. A fase 3 iniciou somente após essa resposta. Antes do checkpoint, hashes confirmavam o código intacto; somente skill e relatórios haviam sido criados.

A skill exige: “apresente o relatório concreto e o plano, então pause e peça confirmação humana antes de modificar código, configuração ou testes do projeto”. Essa etapa vem do requisito explícito do desafio, não de uma autorização de publicação.

## Fase 3 — Resultado

Refatoração aplicada em `config`, `models`, `services`, `controllers`, `views` e `domain`. A reauditoria conferiu os dez achados: P2-01 responsabilidades foram separadas; P2-02 cartão e chave saíram de logs/configuração fixa; P2-03 senhas usam scrypt; P2-04 checkout usa transação; P2-05 relatório usa consulta agrupada; P2-06 erros assíncronos têm tratamento HTTP; P2-07 payloads validam tipos; P2-08 exclusão remove relações na mesma transação; P2-09 nomes abreviados foram substituídos; P2-10 faturamento global morto foi removido.

Validação final HTTP: **3/3 endpoints aprovados, 0 falhas**. Evidências: [`evidence/http-project-2.json`](../evidence/http-project-2.json) e [`evidence/http-run-project-2.log`](../evidence/http-run-project-2.log). A suíte local passou **5/5 testes**.

## Comparação explícita da estrutura

| Antes, na revisão de origem | Depois, no código entregue |
|---|---|
| AppManager concentrava banco/seeds, rotas, checkout, SQL e relatórios; utils misturava configuração e hash. | Server/composição/config, Database/Repository, CheckoutService/gateway simulado, Controller, Routes e domínio de validação/senhas/erros. |

## Checklist de Validação

Checklist literal do enunciado, preenchido após a revisão de 19/10/2026. Os números de arquivos/linhas descrevem o escopo original, não a quantidade maior de módulos produzida pela refatoração. A fase 2 e o checkpoint acima preservam o histórico do plano aprovado.

### Fase 1 — Análise

- [x] Linguagem detectada corretamente — JavaScript (CommonJS); arquivos inventariados na Fase 1.
- [x] Framework detectado corretamente — Express 4.22.1, confirmado no lock; manifests e imports conferidos.
- [x] Domínio da aplicação descrito corretamente — LMS: checkout, matrícula, pagamento simulado e relatório financeiro.
- [x] Número de arquivos analisados condiz com a realidade — 3 arquivos / 180 linhas; lista nominal na Fase 1 e revisão original indicada no início do relatório.

### Fase 2 — Auditoria

- [x] Relatório segue o template definido nos arquivos de referência — Fases 1/2, resumo, evidência, impacto, recomendação, catálogo/playbook, aceite e checkpoint, conforme [audit-template.md](../ecommerce-api-legacy/.agents/skills/refactor-arch/references/audit-template.md).
- [x] Cada finding tem arquivo e linhas exatos — os findings acima ligam o arquivo e intervalo na revisão original.
- [x] Findings ordenados por severidade (CRITICAL → LOW) — ordem e resumo da Fase 2.
- [x] Mínimo de 5 findings identificados — 10 findings (2 CRITICAL, 2 HIGH, 4 MEDIUM, 2 LOW).
- [x] Detecção de APIs deprecated incluída (se aplicável) — Verificação registrada em “APIs obsoletas”: nenhum caso confirmado; callbacks não foram classificados como deprecated apenas por estilo.
- [x] Skill pausa e pede confirmação antes da Fase 3 — [SKILL.md](../ecommerce-api-legacy/.agents/skills/refactor-arch/SKILL.md) exige o checkpoint; a autorização “Aprovo os três planos; pode refatorar” está registrada acima antes do resultado.

### Fase 3 — Refatoração

- [x] Estrutura de diretórios segue padrão MVC — comparação antes/depois acima e camadas descritas na Fase 3.
- [x] Configuração extraída para módulo de config (sem hardcoded) — [src/config.js](../ecommerce-api-legacy/src/config.js) lê ambiente; defaults locais são explícitos, credenciais reais não estão no código.
- [x] Models criados para abstrair dados — `src/models/database.js e src/models/lms-repository.js`.
- [x] Views/Routes separadas para visualização ou roteamento — `src/views/routes.js`.
- [x] Controllers concentram o fluxo da aplicação — src/controllers/lms-controller.js coordena as entradas e o serviço src/services/checkout.js mantém a unidade de trabalho.
- [x] Error handling centralizado — src/domain/errors.js e middleware de src/app.js.
- [x] Entry point claro — `src/server.js; composição em src/app.js / createApp()`; comandos no [README do projeto](../ecommerce-api-legacy/README.md).
- [x] Aplicação inicia sem erros — servidor real iniciado pelo verificador em porta local e banco temporário; [log de boot/requests](../evidence/final-validation/server-project-2.log).
- [x] Endpoints originais respondem corretamente — **3 pares método/caminho cobertos, 9/9 requests e 8/8 checks de payload/efeitos aprovados**, com as mudanças de segurança do plano; [resultado HTTP](../evidence/final-validation/http-project-2.json) e [log](../evidence/final-validation/http-run-project-2.log).

Validação adicional: [cinco testes locais aprovados](../evidence/final-validation/unit-project-2.log). Todos os testes do repositório totalizam 15; o [resumo reproduzível](../evidence/final-validation/summary.json) também registra cinco verificações do seed e o HTTP dos três projetos. O verificador usa somente bancos descartáveis, gateway simulado e serviços locais.
