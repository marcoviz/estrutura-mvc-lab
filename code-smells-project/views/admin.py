import hmac
from flask import Blueprint, current_app, request
from domain.errors import DomainError
from domain.validation import object_data


def build_admin(repository):
    routes = Blueprint("admin", __name__)
    def require_admin():
        expected = current_app.config.get("ADMIN_TOKEN")
        supplied = request.headers.get("Authorization", "")
        if not expected or not hmac.compare_digest(supplied.encode(), ("Bearer " + expected).encode()):
            raise DomainError("Acesso administrativo não autorizado", 401)
    @routes.get("/health")
    def health():
        return {"status":"ok", "database":"connected", "counts":repository().counts(), "versao":"1.0.0"}
    @routes.post("/admin/query")
    def inspect():
        require_admin()
        data = object_data(request.get_json())
        return {"dados":repository().inspect(data.get("sql")), "sucesso":True}
    @routes.post("/admin/reset-db")
    def reset():
        require_admin(); repository().reset()
        return {"mensagem":"Banco de dados resetado", "sucesso":True}
    return routes
