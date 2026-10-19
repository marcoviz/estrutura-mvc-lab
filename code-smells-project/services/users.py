import hmac
from werkzeug.security import generate_password_hash, check_password_hash
from domain.errors import DomainError
from domain.validation import object_data, text, password_value


def public_user(user):
    return {key: value for key, value in user.items() if key != "senha"}


class UserService:
    def __init__(self, users):
        self.users = users

    def create(self, data):
        data = object_data(data)
        name = text(data.get("nome"), "Nome")
        email = text(data.get("email"), "Email")
        password = password_value(data.get("senha"))
        if "@" not in email:
            raise DomainError("Email inválido")
        if self.users.by_email(email):
            raise DomainError("Email já cadastrado", 409)
        return self.users.create(name, email, generate_password_hash(password))

    def login(self, data):
        data = object_data(data)
        email = text(data.get("email"), "Email")
        password = password_value(data.get("senha"))
        user = self.users.by_email(email)
        if not user:
            raise DomainError("Email ou senha inválidos", 401)
        stored = user["senha"]
        modern = stored.startswith(("scrypt:", "pbkdf2:"))
        valid = check_password_hash(stored, password) if modern else hmac.compare_digest(stored.encode(), password.encode())
        if not valid:
            raise DomainError("Email ou senha inválidos", 401)
        if not modern:
            self.users.upgrade_password(user["id"], generate_password_hash(password))
        return {key: user[key] for key in ("id", "nome", "email", "tipo")}
