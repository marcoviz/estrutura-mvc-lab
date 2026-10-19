import hmac
from flask import Blueprint, current_app, request
from domain.errors import DomainError


def build_admin(controller):
    routes = Blueprint("admin", __name__)
    def require_admin():
        expected = current_app.config.get("ADMIN_TOKEN")
        supplied = request.headers.get("Authorization", "")
        if not expected or not hmac.compare_digest(supplied.encode(), ("Bearer " + expected).encode()):
            raise DomainError("Acesso administrativo não autorizado", 401)
    @routes.get("/health")
    def health():
        return {"status":"ok", "database":"connected", "counts":controller().counts(), "versao":"1.0.0"}
    @routes.post("/admin/query")
    def inspect():
        require_admin()
        return {"dados":controller().inspect(request.get_json()), "sucesso":True}
    @routes.post("/admin/reset-db")
    def reset():
        require_admin(); controller().reset()
        return {"mensagem":"Banco de dados resetado", "sucesso":True}
    return routes
