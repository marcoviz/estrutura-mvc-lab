from contextlib import contextmanager


class Orders:
    def __init__(self, connection):
        self.connection = connection

    def list(self, user_id=None):
        where, params = (" WHERE usuario_id=?", (user_id,)) if user_id is not None else ("", ())
        orders = [dict(row) for row in self.connection.execute("SELECT * FROM pedidos" + where + " ORDER BY id", params)]
        if not orders:
            return []
        ids = [order["id"] for order in orders]
        placeholders = ",".join("?" for _ in ids)
        rows = self.connection.execute("SELECT i.*,p.nome AS produto_nome FROM itens_pedido i LEFT JOIN produtos p ON p.id=i.produto_id WHERE i.pedido_id IN (" + placeholders + ") ORDER BY i.id", ids)
        grouped = {}
        for row in rows:
            grouped.setdefault(row["pedido_id"], []).append({"produto_id": row["produto_id"], "produto_nome": row["produto_nome"] or "Desconhecido", "quantidade": row["quantidade"], "preco_unitario": row["preco_unitario"]})
        for order in orders:
            order["itens"] = grouped.get(order["id"], [])
        return orders

    def get(self, order_id):
        return self.connection.execute("SELECT * FROM pedidos WHERE id=?", (order_id,)).fetchone()

    def update_status(self, order_id, status):
        with self.connection:
            self.connection.execute("UPDATE pedidos SET status=? WHERE id=?", (status, order_id))

    def totals(self):
        return dict(self.connection.execute("SELECT COUNT(*) AS total, COALESCE(SUM(total),0) AS revenue, SUM(status='pendente') AS pending, SUM(status='aprovado') AS approved, SUM(status='cancelado') AS cancelled FROM pedidos").fetchone())

    @contextmanager
    def transaction(self):
        with self.connection:
            self.connection.execute("BEGIN IMMEDIATE")
            yield

    def user_exists(self, user_id):
        return self.connection.execute("SELECT id FROM usuarios WHERE id=?", (user_id,)).fetchone() is not None

    def products_by_ids(self, product_ids):
        placeholders = ",".join("?" for _ in product_ids)
        rows = self.connection.execute("SELECT * FROM produtos WHERE id IN (" + placeholders + ")", list(product_ids))
        return {row["id"]: row for row in rows}

    def create(self, user_id, total):
        return self.connection.execute("INSERT INTO pedidos (usuario_id,status,total) VALUES (?, 'pendente', ?)", (user_id, total)).lastrowid

    def add_item(self, order_id, product_id, quantity, unit_price):
        self.connection.execute("INSERT INTO itens_pedido (pedido_id,produto_id,quantidade,preco_unitario) VALUES (?,?,?,?)", (order_id, product_id, quantity, unit_price))
        self.connection.execute("UPDATE produtos SET estoque=estoque-? WHERE id=?", (quantity, product_id))
