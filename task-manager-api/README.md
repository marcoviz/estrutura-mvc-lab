# Task Manager Flask em MVC

API de tarefas, usuários, categorias e relatórios com SQLAlchemy, controllers, repositories, services e presenters. Os 22 pares método/caminho originais foram mantidos. As mudanças de segurança e limites estão no [relatório](../reports/audit-project-3.md).

## Executar

Use Python 3.12, no diretório deste projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export DATABASE_URL="sqlite:///$PWD/tasks.db"
export HOST=127.0.0.1
export PORT=5001
python app.py
```

A API fica em `http://127.0.0.1:5001`; a porta acima permite rodá-la junto com o projeto 1. Sem `PORT`, o padrão é 5000. O schema é criado no boot e a aplicação funciona com banco vazio. O comando usa caminho SQLite absoluto; o default `sqlite:///tasks.db` do Flask-SQLAlchemy é relativo à pasta `instance/`. `APP_SECRET`, `APP_DEBUG` e variáveis opcionais estão em `.env.example`; exporte-as no shell (o comando `python app.py` não carrega `.env` automaticamente).

### Seed opcional

Para experimentar com uma pessoa, uma categoria e uma tarefa, em um banco **vazio**, substitua o placeholder por uma senha local de pelo menos quatro caracteres:

```bash
DEMO_PASSWORD='<sua-senha-local>' python seed.py
```

O usuário demonstrativo é `demo@example.test`. O seed exige a variável, grava hash de senha e recusa executar se qualquer usuário, categoria ou tarefa já existir. Não apaga dados. Não é necessário executá-lo antes do primeiro boot; cadastros também podem ser feitos pela API. Use o mesmo `DATABASE_URL` no seed e no servidor. A validação automatizada testa a criação e as recusas com bancos descartáveis.

O login conserva o `fake-jwt-token` do contrato didático: não é autenticação de produção. SMTP não é acionado pelas rotas HTTP nem pelos testes.

## Validar

```bash
python -m unittest discover -s tests -v
```

São cinco testes de senha e upgrade de hash legado, validação/rollback, queries e overdue, efeitos de exclusão e defaults de categoria. O comando `python3 scripts/verify_local.py` na raiz, depois do setup do [README principal](../README.md#como-executar), valida também seed, boot e contratos HTTP sem alterar seu banco de trabalho.
