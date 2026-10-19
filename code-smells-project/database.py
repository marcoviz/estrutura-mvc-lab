import sqlite3
from flask import current_app, g

SCHEMA = "CREATE TABLE IF NOT EXISTS produtos (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                nome TEXT,\n                descricao TEXT,\n                preco REAL,\n                estoque INTEGER,\n                categoria TEXT,\n                ativo INTEGER DEFAULT 1,\n                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n            );\nCREATE TABLE IF NOT EXISTS usuarios (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                nome TEXT,\n                email TEXT,\n                senha TEXT,\n                tipo TEXT DEFAULT 'cliente',\n                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n            );\nCREATE TABLE IF NOT EXISTS pedidos (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                usuario_id INTEGER,\n                status TEXT DEFAULT 'pendente',\n                total REAL,\n                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n            );\nCREATE TABLE IF NOT EXISTS itens_pedido (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                pedido_id INTEGER,\n                produto_id INTEGER,\n                quantidade INTEGER,\n                preco_unitario REAL\n            )"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"], timeout=10)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.rollback()
        connection.close()


def init_db():
    connection = get_db()
    connection.executescript(SCHEMA)
    connection.commit()
