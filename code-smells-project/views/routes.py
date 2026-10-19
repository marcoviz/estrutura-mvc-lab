from flask import Blueprint, request


def build_routes(controller):
    routes = Blueprint("store", __name__)
    def ok(data, **extra): return {"dados": data, "sucesso": True, **extra}
    @routes.get("/")
    def index():
        return {"mensagem": "Bem-vindo à API da Loja", "versao": "1.0.0", "endpoints": {"produtos":"/produtos", "usuarios":"/usuarios", "pedidos":"/pedidos", "login":"/login", "relatorios":"/relatorios/vendas", "health":"/health"}}
    @routes.get("/produtos")
    def products(): return ok(controller().products.list())
    @routes.get("/produtos/busca")
    def search():
        result = controller().search_products(request.args)
        return ok(result, total=len(result))
    @routes.get("/produtos/<int:product_id>")
    def product(product_id): return ok(controller().product(product_id))
    @routes.post("/produtos")
    def create_product(): return ok({"id": controller().create_product(request.get_json())}, mensagem="Produto criado"), 201
    @routes.put("/produtos/<int:product_id>")
    def update_product(product_id):
        controller().update_product(product_id, request.get_json())
        return {"sucesso": True, "mensagem": "Produto atualizado"}
    @routes.delete("/produtos/<int:product_id>")
    def delete_product(product_id):
        controller().delete_product(product_id)
        return {"sucesso": True, "mensagem": "Produto deletado"}
    @routes.get("/usuarios")
    def users(): return ok(controller().users.list())
    @routes.get("/usuarios/<int:user_id>")
    def user(user_id): return ok(controller().user(user_id))
    @routes.post("/usuarios")
    def create_user(): return ok({"id": controller().user_service.create(request.get_json())}), 201
    @routes.post("/login")
    def login(): return ok(controller().user_service.login(request.get_json()), mensagem="Login OK")
    @routes.post("/pedidos")
    def create_order(): return ok(controller().order_service.create(request.get_json()), mensagem="Pedido criado com sucesso"), 201
    @routes.get("/pedidos")
    def orders(): return ok(controller().orders.list())
    @routes.get("/pedidos/usuario/<int:user_id>")
    def user_orders(user_id): return ok(controller().orders.list(user_id))
    @routes.put("/pedidos/<int:order_id>/status")
    def update_status(order_id):
        controller().update_order(order_id, request.get_json())
        return {"sucesso": True, "mensagem": "Status atualizado"}
    @routes.get("/relatorios/vendas")
    def report(): return ok(controller().order_service.report())
    return routes
