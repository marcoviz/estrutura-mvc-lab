import re
from domain.errors import DomainError

PUBLIC_TABLES = {"produtos", "usuarios", "pedidos", "itens_pedido"}


class AdminRepository:
    def __init__(self, connection): self.connection = connection

    def counts(self):
        return {table: self.connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in ("produtos", "usuarios", "pedidos")}

    def inspect(self, sql):
        if not isinstance(sql, str): raise DomainError("Query inválida")
        # Deliberately narrow inspection language; never execute submitted SQL.
        match = re.fullmatch(r"\s*SELECT\s+COUNT\(\*\)\s+(?:AS\s+count\s+)?FROM\s+(produtos|usuarios|pedidos|itens_pedido)\s*;?\s*", sql, re.I)
        if not match: raise DomainError("Somente SELECT COUNT(*) AS count FROM tabela é permitido")
        table = match.group(1).lower()
        if table not in PUBLIC_TABLES: raise DomainError("Tabela inválida")
        count = self.connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        return [{"count": count}]

    def reset(self):
        with self.connection:
            for table in ("itens_pedido", "pedidos", "produtos", "usuarios"):
                self.connection.execute(f"DELETE FROM {table}")
