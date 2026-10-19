class Users:
    def __init__(self, connection):
        self.connection = connection

    def get(self, user_id):
        row = self.connection.execute("SELECT * FROM usuarios WHERE id=?", (user_id,)).fetchone()
        return dict(row) if row else None

    def by_email(self, email):
        row = self.connection.execute("SELECT * FROM usuarios WHERE email=?", (email,)).fetchone()
        return dict(row) if row else None

    def list(self):
        return [dict(row) for row in self.connection.execute("SELECT id,nome,email,tipo,criado_em FROM usuarios ORDER BY id")]

    def create(self, name, email, password_hash):
        with self.connection:
            cursor = self.connection.execute("INSERT INTO usuarios (nome,email,senha,tipo) VALUES (?,?,?,?)", (name, email, password_hash, "cliente"))
        return cursor.lastrowid

    def upgrade_password(self, user_id, password_hash):
        with self.connection:
            self.connection.execute("UPDATE usuarios SET senha=? WHERE id=?", (password_hash, user_id))
