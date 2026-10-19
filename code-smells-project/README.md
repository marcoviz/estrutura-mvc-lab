# E-commerce Flask em MVC

API de produtos, usuários, pedidos e relatórios refatorada a partir de `code-smells-project`. Os 19 pares método/caminho foram preservados, com as mudanças de segurança aprovadas no [relatório](../reports/audit-project-1.md).

## Executar

Use Python 3.12, no diretório deste projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export DATABASE_PATH="$PWD/loja.db"
export HOST=127.0.0.1
export PORT=5000
python app.py
```

O boot cria apenas o schema SQLite vazio; **não cria usuários ou produtos de exemplo** e não apaga registros existentes. Cadastre dados por `POST /usuarios` e `POST /produtos`. `APP_DEBUG` é falso por padrão; `APP_SECRET` e `ADMIN_TOKEN` vêm do ambiente, conforme `.env.example`. O arquivo `.env` não é carregado automaticamente por `python app.py`; exporte as variáveis necessárias.

`POST /admin/query` e `POST /admin/reset-db` exigem `Authorization: Bearer <ADMIN_TOKEN>`. Sem token configurado, o acesso fica negado. O console aceita somente contagens de tabelas permitidas; o reset apaga dados e é usado pelo smoke apenas no banco temporário. O login mantém o contrato do laboratório e não constitui uma plataforma de autenticação.

## Validar

```bash
python -m unittest discover -s tests -v
```

São cinco testes de senha/SQL, estoque e rollback, validação/admin e queries em lote. Para repetir boot HTTP e verificar os payloads e efeitos persistidos com banco descartável, execute `python3 scripts/verify_local.py` na raiz do repositório, após preparar os três ambientes conforme o [README principal](../README.md#como-executar).
