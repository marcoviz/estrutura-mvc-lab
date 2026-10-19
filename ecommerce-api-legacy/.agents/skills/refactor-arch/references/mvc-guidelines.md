# Arquitetura MVC para backends

| Camada | Responsabilidade | Não deve conter |
|---|---|---|
| Models/domínio | Entidades, invariantes e regras de dados | Request/Response do framework, envio de HTTP, credenciais fixas |
| Repositories (quando úteis) | Consultas e mapeamento persistente | Códigos HTTP, execução de pagamento, templates |
| Controllers | Coordenar entrada validada/caso de uso e saída | SQL em linha, política complexa copiada, configuração global |
| Services/casos de uso (quando necessários) | Regras que coordenam modelos e unidade transacional | Dependência de request/res ou jsonify |
| Views/Routes/presenters | Métodos/caminhos, adaptação HTTP, representação JSON/HTML | Transações e políticas de negócio |
| Config/composition root | Instanciar adaptadores, injetar deps e iniciar servidor | Regras comerciais espalhadas e segredos em literais |
| Error boundary | Mapear erros de domínio para transporte e log seguro | Expor stack/SQL/segredos ou transformar todo erro em 200 |

Estrutura é consequência de responsabilidade, não meta estética. Preserve domínio, framework e banco. Em Flask já organizado, mantenha modelos úteis e extraia controllers de Blueprints. Em Express monolítico, separe router/controller/service/repository antes de adicionar abstrações genéricas. Em outras stacks, use convenções locais equivalentes.

Unidade de trabalho deve cobrir escritas relacionadas; contexto fecha conexões e rollback ocorre em falha. Serviços recebem abstrações simples de DB, relógio ou pagamentos quando isso permite isolar testes. Não construir um container DI só para eliminar `new`.

Compatibilidade: manter método, URL, nomes públicos, códigos e formas válidas, salvo correção de vulnerabilidade explicitamente registrada e aprovada. Remover senha de response é mudança intencional de segurança, não regressão a esconder. Documentar dados antigos que precisem migração; não resetar banco existente automaticamente. Um mock de pagamento deve continuar mock, sem chamar serviço real.
