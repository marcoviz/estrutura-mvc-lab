# Template de relatório

Use este esquema, preenchendo dados observados em vez de exemplos fictícios.

```markdown
# Auditoria — <projeto>
Estado: Fases 1/2 concluídas; Fase 3 aguardando revisão humana.
Revisão de origem: <commit ou snapshot hash>

## Fase 1 — Análise
- Linguagem/runtime e framework (declarado/resolvido)
- Dependências e banco
- Domínio
- Arquitetura atual e dependências
- Arquivos efetivamente analisados e linhas
- Endpoints e contratos a preservar
- Validação baseline executada ou limitações

## Fase 2 — Achados
Resumo: CRITICAL <n>, HIGH <n>, MEDIUM <n>, LOW <n>.

### <ID> [<severidade>] <título>
- Arquivo: <path>:<linha inicial>–<linha final>, na revisão de origem
- Evidência: <snippet curto + fluxo concreto>
- Impacto: <efeito verificável>
- Recomendação: <transformação específica>
- Catálogo/playbook: <referência aplicável>
- Aceite da correção: <teste/observação esperado>

## Plano proposto e mudança de contratos
<estrutura alvo, sequência, compatibilidade, migração e mudanças de segurança>

## Checkpoint
Relatório apresentado: <evidência real>
Aprovação: pendente / <resposta humana real e escopo>
Nenhum código/configuração/teste da aplicação modificado antes do checkpoint.

## Fase 3 — Resultado
Preencher apenas após executar: mudanças, estado de cada finding,
comandos, boot, endpoints, efeitos de dados, regressões e pendências.
```

As linhas sempre se referem ao código auditado, não ao novo arquivo. Preserve commit/snapshot para leitura futura. Inclua no relatório o texto suficiente para entender o achado mesmo se o arquivo for removido. Para aplicação parcialmente organizada, apresente o que será mantido e o que será extraído.
