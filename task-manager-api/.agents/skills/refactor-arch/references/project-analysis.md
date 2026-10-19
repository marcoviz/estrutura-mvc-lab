# Análise de projeto

## Evidência antes de escolher arquitetura

| Sinal | Inferência permitida | Verificação necessária |
|---|---|---|
| requirements/pyproject e imports Flask/Django/FastAPI | Stack Python e framework provável | Versão fixada ou lock versus runtime instalado; não inferir versão de um import |
| package.json/lock e require/import express | Backend JS/TS | CommonJS/ESM, versão resolvida e scripts reais |
| pom/gradle, csproj, go.mod, Cargo.toml | Outro ecossistema | Rotas, lifecycle, DI e ORM locais antes de aplicar exemplos Python/JS |
| sqlite3/ORM/driver SQL | Persistência provável | Configuração, schema e transações; URL de exemplo não prova produção |
| routes/controllers/models | Organização nominal | Seguir fluxo HTTP→regra→dados→response, sem concluir MVC só pelo nome da pasta |
| templates ou serializers/DTOs | Camada de representação | Em API JSON, View é o presenter/resposta; não gerar HTML só para preencher a sigla MVC |

Mapeie composição, estado mutável, dependências externas, validação, serialização e erros. Leia uma operação de escrita inteira, inclusive commits/rollback e efeitos colaterais. Procure consulta em loop e forma de montar relacionamentos, sem confundir uma consulta agregada com N+1.

## Saída da fase 1

Registrar: raiz e revisão; arquivos/linhas analisados; stack declarada e runtime medido; tabelas/entidades; domínio; endpoints método+caminho; desenho atual; dados necessários para boot; baseline de testes e limitações.

Liste rotas dinâmicas com parâmetros e exemplos de fixture. Para preservar contratos, capture sucesso, falha esperada e efeitos persistidos. Não chamar operações administrativas destrutivas em dados reais. Use cópia/DB temporário, bind em loopback e dependências fake. Seeds destrutivos só podem rodar contra banco descartável explicitamente identificado.
