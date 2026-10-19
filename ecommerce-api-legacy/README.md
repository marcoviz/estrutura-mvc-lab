# LMS Express em MVC

API de checkout, relatório financeiro e exclusão de usuário, refatorada a partir da God Class `AppManager`. Contratos `usr`, `eml`, `pwd`, `c_id` e `card` permanecem iguais. As mudanças aprovadas estão no [relatório](../reports/audit-project-2.md).

## Executar

Use Node.js 24 e npm, no diretório deste projeto:

```bash
npm ci
npm start
```

O servidor escuta `http://127.0.0.1:3000`. `HOST`, `PORT` e `DATABASE_PATH` são lidos do ambiente; `.env.example` é uma referência e não é carregado automaticamente. O banco padrão é SQLite em memória, perdido ao encerrar. Para persistir localmente, exporte `DATABASE_PATH` com o caminho de um arquivo antes do boot.

No banco inicial são criados dois cursos, uma pessoa demonstrativa e uma matrícula paga. A senha demonstrativa é aleatória, sem credencial fixa publicada. O gateway é simulado: cartão iniciado por `4` aprova; os demais recusam sem persistir checkout parcial. Não há cobrança ou integração externa. Exemplos estão em [api.http](api.http).

Os três endpoints mantêm o escopo de autorização do laboratório; este projeto não implementa uma plataforma de identidade. A exclusão agora remove matrícula e pagamento vinculados, conforme o plano aprovado.

## Validar

```bash
npm test
```

São cinco testes de KDF, tipos, rollback, concorrência/relatório e exclusão. Para repetir também o HTTP com banco temporário, execute `python3 scripts/verify_local.py` na raiz, após preparar os ambientes do [README principal](../README.md#como-executar). O smoke confere o valor do checkout e o relatório antes/depois de aprovação, recusa e exclusão.
