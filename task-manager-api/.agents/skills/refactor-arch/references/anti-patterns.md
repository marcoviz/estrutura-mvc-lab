# Catálogo de anti-patterns

A severidade depende do impacto comprovado. A classificação abaixo segue a escala do laboratório: CRITICAL inclui exposição grave e separação de responsabilidades totalmente violada; HIGH inclui fortes violações MVC/SOLID; MEDIUM cobre duplicação/validação/performance moderada; LOW cobre legibilidade. Não elevar automaticamente toda classe extensa a CRITICAL.

| ID | Severidade típica | Sinal concreto | Confirmação e recomendação |
|---|---|---|---|
| AP-01 SQL interpolado | CRITICAL | Concatenação/f-string de entrada numa query | Seguir origem até execute; converter valores em parâmetros, identifiers por allowlist |
| AP-02 Segredos/credenciais/DTO sensível | CRITICAL | Literal de secret, senha/hash no JSON ou cartão em log | Confirmar uso/saída; config externa, KDF e DTO explícito, redaction |
| AP-03 God Class | CRITICAL ou HIGH | Schema, rotas, SQL, regras e resposta no mesmo componente | Enumerar responsabilidades concretas; separar composição, controller, domínio e dados |
| AP-04 Transação ausente/estado global | HIGH | Escritas relacionadas com commits separados ou conexão mutável global | Simular erro intermediário em DB temporário; unidade de trabalho e rollback |
| AP-05 Regra no transporte | HIGH | Handler decide política e monta várias queries/transações | Extrair caso de uso testável, sem só mover arquivo gigante |
| AP-06 N+1 | MEDIUM | Query/relationship lazy dentro de loop por entidades | Contar consultas sob fixtures crescentes; eager load/batch/JOIN |
| AP-07 Validação duplicada/ausente | MEDIUM | Mesmos limites espalhados ou casts sem tratamento | Comparar criação/edição e input malformado; validador único na fronteira |
| AP-08 Erro disperso | MEDIUM | catch genérico devolve stack/SQL ou callback ignora err | Testar erro real e status; boundary central preserva erros de domínio |
| AP-09 API deprecated/legacy | MEDIUM por padrão | API marcada deprecated para a versão efetiva | Confirmar fonte oficial e equivalente; não confundir estilo antigo com remoção |
| AP-10 Política como magic numbers | LOW | Literais de faixas/limites repetidos | Nomear constantes/políticas e testar fronteiras sem mudar regra |
| AP-11 Nomes opacos | LOW | Variáveis que escondem responsabilidade | Nomear por domínio preservando chaves públicas |
| AP-12 Código morto | LOW | Import/estado/helper sem usos | Inspecionar efeitos no import e reflection antes de remover |
| AP-13 Fronteira administrativa ausente | CRITICAL ou HIGH | Rota destrutiva/consulta privilegiada sem guard | Identificar ator e escopo; proteção explícita, sem inventar sistema de identidade completo |
| AP-14 Integridade referencial ausente | MEDIUM ou HIGH | Delete deixa relações inválidas ou escrita parcial | Definir cascade/restrict com evidência de domínio e executar em transação |

## Depreciação com evidência

- SQLAlchemy 2.x: `Query.get()` é legacy; preferir `Session.get(Model, id)`. Isso não implica que todo `Query` foi removido. [Documentação oficial](https://docs.sqlalchemy.org/en/20/orm/queryguide/query.html#sqlalchemy.orm.Query.get).
- Python >=3.12: `datetime.utcnow()` é deprecated; preferir `datetime.now(UTC)`. Converta deliberadamente na fronteira se o banco existente usa UTC sem timezone; comparar aware e naive sem migração causa erro. [Documentação oficial](https://docs.python.org/3.12/library/datetime.html#datetime.datetime.utcnow).
- Em outras stacks, consultar o guia de migração/API da versão realmente instalada antes de afirmar depreciação. `Buffer.from` em Node é API atual, não um smell de depreciação por estar em um helper criptográfico ruim.

Registrar versão, URL, localização e substituto no finding. Se falta evidência, escrever hipótese e não "deprecated confirmado".
