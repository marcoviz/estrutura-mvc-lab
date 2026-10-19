class Products:
    def __init__(self, connection):
        self.connection = connection

    def get(self, product_id):
        row = self.connection.execute("SELECT * FROM produtos WHERE id = ?", (product_id,)).fetchone()
        return dict(row) if row else None

    def list(self, term="", category=None, minimum=None, maximum=None):
        clauses, values = [], []
        if term:
            clauses.append("(nome LIKE ? OR descricao LIKE ?)")
            values.extend([f"%{term}%", f"%{term}%"])
        if category:
            clauses.append("categoria = ?"); values.append(category)
        if minimum is not None:
            clauses.append("preco >= ?"); values.append(minimum)
        if maximum is not None:
            clauses.append("preco <= ?"); values.append(maximum)
        sql = "SELECT * FROM produtos" + (" WHERE " + " AND ".join(clauses) if clauses else "") + " ORDER BY id"
        return [dict(row) for row in self.connection.execute(sql, values)]

    def create(self, values):
        with self.connection:
            cursor = self.connection.execute("INSERT INTO produtos (nome,descricao,preco,estoque,categoria) VALUES (?,?,?,?,?)", values)
        return cursor.lastrowid

    def update(self, product_id, values):
        with self.connection:
            self.connection.execute("UPDATE produtos SET nome=?,descricao=?,preco=?,estoque=?,categoria=? WHERE id=?", (*values, product_id))

    def delete(self, product_id):
        with self.connection:
            self.connection.execute("DELETE FROM produtos WHERE id=?", (product_id,))
