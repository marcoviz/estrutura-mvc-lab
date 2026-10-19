---
name: refactor-arch
description: Auditar arquitetura de backends, localizar violações de MVC e refatorar após revisão do relatório, preservando contratos HTTP em diferentes linguagens e frameworks.
---

# Refactor Arch

Use a raiz do projeto informada; se não houver, confirme o alvo pelo diretório atual e seus manifests. O resultado é um relatório rastreável e uma refatoração MVC validada, sem trocar a stack nem adicionar funcionalidades comerciais.

## Fase 1 — Análise

Leia [análise de projeto](references/project-analysis.md). Inspecione código, configuração, manifests/locks e testes. Registre branch/commit e alterações já existentes; não as sobrescreva. Detecte linguagem, versão declarada/resolvida, framework, banco, domínio e direção das dependências. Conte arquivos-fonte efetivamente lidos, excluindo dependências/gerados.

Imprima o resumo de stack/arquitetura e inventarie método+caminho de todos os endpoints, payload/status e efeitos importantes. Quando não houver testes, prepare caracterização em área de trabalho isolada sem modificar a aplicação. Nunca use produção, gateways ou SMTP reais para validar um legado.

## Fase 2 — Auditoria e revisão

Leia [catálogo](references/anti-patterns.md), confronte os sinais com fluxos reais e produza o [relatório padrão](references/audit-template.md). Registre severidade, caminho e linhas da revisão original, evidência, impacto e transformação proposta por achado. Uma string suspeita não basta: confirme que a entrada alcança o sink, que a consulta está no loop, ou que a API é de fato obsoleta para a versão. Não copie quantidades de um relatório anterior.

Ordene CRITICAL → HIGH → MEDIUM → LOW e separe achado confirmado de hipótese. Cite documentação primária de depreciação e o substituto compatível. Liste alterações intencionais de segurança que mudam o contrato (por exemplo, remover hashes de responses ou proteger uma rota administrativa); preserve os demais comportamentos válidos.

**Checkpoint obrigatório:** apresente o relatório concreto e o plano, então pause e peça confirmação humana antes de modificar código, configuração ou testes do projeto. Os relatórios e a própria criação da skill são artefatos autorizados da auditoria. Uma autorização geral anterior à existência do relatório não representa sua revisão. Registre a resposta recebida sem inventar aprovador, data ou aceite. Se houver rejeição/ajuste, revise o plano. Prossiga somente no escopo confirmado.

## Fase 3 — Refatoração e validação

Após confirmação, leia [arquitetura alvo](references/mvc-guidelines.md) e apenas as transformações relevantes do [playbook](references/refactoring-playbook.md). Trabalhe em incrementos: caracterização → composição/config → fronteiras MVC → correções de dados/segurança → validação. Respeite a organização boa que já existe; não transforme toda aplicação em um template fixo.

Mantenha Models sem HTTP; Views/Routes mapeiam transporte/representação; Controllers coordenam casos de uso. Regras complexas podem ir para services e persistência para repositories, sem classes vazias. Faça entry point e injeção de dependências explícitos, transações consistentes e tratamento central de erros. Evite wrappers que só renomeiam a God Class original.

Inicie cada aplicação em ambiente temporário e acesse **todos os endpoints inventariados**. Compare status/payload e efeitos de dados com a caracterização, excetuando mudanças de segurança aprovadas. Inclua falhas relevantes (rollback, entrada inválida, ausência e duplicação), além do caminho feliz. Use receptor/gateway fake local e nunca envie email nem faça cobrança real. Uma importação ou lint não demonstra boot HTTP.

Reaudite os achados por ID, indique corrigido/parcial/pendente com evidência, registre comandos/saídas e atualize o relatório de resultado. Não declare "zero problemas" com base apenas em busca textual. Se uma dependência impedir executar, preserve trabalho e declare a lacuna; não invente testes. Commite apenas quando solicitado pelo trabalho e sem dados temporários/segredos.
