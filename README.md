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

| Projeto | Escopo original | CRITICAL | HIGH | MEDIUM | LOW | Endpoints |
|---|---|---:|---:|---:|---:|---:|
| E-commerce Flask | 4 arquivos / 780 linhas | 3 | 2 | 3 | 3 | 19 |
| LMS Express | 3 arquivos / 180 linhas | 2 | 2 | 4 | 2 | 3 |
| Task Manager Flask | 15 arquivos / 1158 linhas | 1 | 2 | 4 | 3 | 22 |

### Estrutura antes e depois

As estruturas anteriores se referem à revisão original identificada nos relatórios; as posteriores correspondem ao código deste repositório.

| Projeto | Antes | Depois e responsabilidade |
|---|---|---|
| `code-smells-project` | `app.py`, `controllers.py`, `models.py`, `database.py`: SQL, validação, regras e HTTP misturados | `app.py` compõe a aplicação; `config.py` lê ambiente; `database.py` gerencia conexão; `models/` persiste; `services/` coordena pedidos e usuários; `controllers/` concentra fluxo; `views/` trata HTTP; `domain/` valida e define erros |
| `ecommerce-api-legacy` | `src/app.js`, `src/AppManager.js`, `src/utils.js`: God Class com schema, rotas, pagamentos e relatórios | `src/server.js` inicia; `src/app.js` compõe; `src/config.js` configura; `src/models/` encapsula SQLite; `src/services/checkout.js` coordena transação e gateway simulado; `src/controllers/` coordena HTTP; `src/views/` declara rotas; `src/domain/` valida/deriva senhas/trata erros |
| `task-manager-api` | `app.py`, `database.py`, `seed.py`, `models/`, `routes/`, `services/`, `utils/`: rotas com regras e consultas ORM | Factory/config separadas; `models/` preserva entidades; `repositories/` centraliza consultas e eager loading; `controllers/` coordena casos de uso; `domain/` centraliza regras; `services/` monta relatórios; `views/` apresenta DTOs; `routes/` mantém Blueprints |

### Checklist de validação por projeto

Os 19 itens do enunciado, separados nas três fases e preenchidos com evidências, estão em:

- [Projeto 1 — checklist completo](reports/audit-project-1.md#checklist-de-validação).
- [Projeto 2 — checklist completo](reports/audit-project-2.md#checklist-de-validação).
- [Projeto 3 — checklist completo](reports/audit-project-3.md#checklist-de-validação).

A skill adaptou o projeto 1 de módulos nominais para camadas reais, desfez a God Class no projeto 2 e preservou o ORM/Blueprints úteis no projeto 3. Não houve imposição de uma árvore única sobre as duas stacks. Na reauditoria, corrigimos tipos JSON inválidos, preservação literal de senhas e defaults de categoria. As views do projeto 1 agora usam métodos públicos dos controllers, inclusive no fluxo administrativo.

### Validação e evidências

As três suítes passaram novamente: **15 testes, cinco por projeto**. O verificador também confere o seed em bancos temporários: senha obrigatória, criação de uma amostra, recusa da segunda execução, hash verificável e recusa de banco que já contém apenas categoria, sem inserir ou apagar dados.

Os registros HTTP anteriores continuam em [projeto 1](evidence/http-project-1.json), [projeto 2](evidence/http-project-2.json) e [projeto 3](evidence/http-project-3.json), com 20/20, 3/3 e 22/22 verificações. Os respectivos logs `evidence/http-run-project-{1,2,3}.log` preservam a evidência da aplicação rodando.

O smoke ampliado em [scripts/smoke_http.py](scripts/smoke_http.py) verifica, além de status e ausência de segredos, valores persistidos, filtros, totais, estoque, joins, atualização parcial, exclusão e falhas sem efeitos. Os valores esperados derivam das entradas e contratos aprovados; isso não é uma alegação de equivalência byte a byte com todas as respostas do legado, cujos comportamentos inseguros foram alterados conforme os planos.

A execução final ampliada passou com **HTTP real**, bancos descartáveis e processos locais separados:

| Projeto | Requests HTTP | Checks de payload/efeitos | Resultado |
|---|---:|---:|---|
| E-commerce Flask | 31/31 | 20/20 | Aprovado |
| LMS Express | 9/9 | 8/8 | Aprovado |
| Task Manager Flask | 34/34 | 20/20 | Aprovado |

São **74 requests e 48 checks**, além dos 15 testes e cinco cenários de seed, sem falhas. [Resumo e logs finais](evidence/final-validation/summary.json). O campo `transport` diferencia HTTP real de `flask-test-client`; a execução final registra `http` nos três projetos. A opção `--flask-in-process` existe para ambientes que bloqueiem sockets, mas o Express ainda requer loopback.

O repositório contém a implementação commitada e publicada no GitHub. Submissão à avaliação da Full Cycle é uma ação separada; não foi realizada por este projeto.

## Como Executar

Pré-requisitos: Python **3.12** (validado em 3.12.14), Node.js **24** (validado em 24.19.0), npm e Codex configurado para usar skills. Cada Flask precisa de seu próprio ambiente virtual, pois os requirements usam versões diferentes. O Node usa SQLite nativo; se não houver binário pronto para seu sistema, a instalação requer as ferramentas de compilação da plataforma.

Na raiz do repositório, prepare os ambientes:

```bash
python3 -m venv code-smells-project/.venv
code-smells-project/.venv/bin/python -m pip install -r code-smells-project/requirements.txt
python3 -m venv task-manager-api/.venv
task-manager-api/.venv/bin/python -m pip install -r task-manager-api/requirements.txt
npm --prefix ecommerce-api-legacy ci
```

Os guias de cada aplicação mostram configuração, boot e teste individual: [E-commerce Flask](code-smells-project/README.md), [LMS Express](ecommerce-api-legacy/README.md) e [Task Manager](task-manager-api/README.md). As variáveis dos `.env.example` são referências; os comandos abaixo usam variáveis exportadas no shell. O seed do Task Manager é **opcional**, exige `DEMO_PASSWORD` e nunca deve ser usado para apagar/reinicializar um banco existente.

Para executar os testes isoladamente, na raiz:

```bash
cd code-smells-project
.venv/bin/python -m unittest discover -s tests -v
cd ../ecommerce-api-legacy
npm test
cd ../task-manager-api
.venv/bin/python -m unittest discover -s tests -v
cd ..
```

Para repetir toda a validação, sem iniciar as aplicações manualmente:

```bash
python3 scripts/verify_local.py
```

O verificador executa as três suítes, testa o seed, inicia cada servidor em porta local disponível, cria bancos descartáveis, roda os contratos HTTP e encerra os processos. O relatório vai para `evidence/final-validation/`; use `--output-dir /tmp/mvc-validation` para gravar fora do checkout. Os parâmetros `--python-project-1`, `--python-project-3` e `--node` permitem indicar runtimes já instalados. Não há API externa, pagamento real ou envio de email nesse fluxo. Não aponte o smoke avulso para um banco de trabalho: ele cria/exclui fixtures e chama o reset administrativo autenticado do projeto 1.

### Invocar a skill

No diretório de cada um dos três projetos, abra Codex e invoque:

```text
$refactor-arch Audite este projeto e apresente o relatório antes de refatorar.
```

A skill pode também ser citada pelo seu `.agents/skills/refactor-arch/SKILL.md`. Revise o relatório da fase 2 e confirme o plano concreto antes da fase 3. Na execução documentada neste repositório, essa autorização já foi recebida e registrada nos três relatórios.
