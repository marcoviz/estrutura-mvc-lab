from domain.errors import DomainError
from domain.validation import product_data, object_data, ORDER_STATUSES, product_filters
from services.users import public_user


class StoreController:
    def __init__(self, products, users, orders, user_service, order_service):
        self.products, self.users, self.orders = products, users, orders
        self.user_service, self.order_service = user_service, order_service

    def list_products(self):
        return self.products.list()

    def list_users(self):
        return self.users.list()

    def create_user(self, data):
        return self.user_service.create(data)

    def login(self, data):
        return self.user_service.login(data)

    def create_order(self, data):
        return self.order_service.create(data)

    def list_orders(self, user_id=None):
        return self.orders.list(user_id)

    def sales_report(self):
        return self.order_service.report()

    def product(self, product_id):
        product = self.products.get(product_id)
        if product is None: raise DomainError("Produto não encontrado", 404)
        return product

    def create_product(self, data):
        return self.products.create(product_data(data))

    def update_product(self, product_id, data):
        self.product(product_id)
        self.products.update(product_id, product_data(data))

    def delete_product(self, product_id):
        self.product(product_id)
        self.products.delete(product_id)

    def user(self, user_id):
        user = self.users.get(user_id)
        if user is None: raise DomainError("Usuário não encontrado", 404)
        return public_user(user)

    def update_order(self, order_id, data):
        status = object_data(data).get("status")
        if not isinstance(status, str) or status not in ORDER_STATUSES: raise DomainError("Status inválido")
        if self.orders.get(order_id) is None: raise DomainError("Pedido não encontrado", 404)
        self.orders.update_status(order_id, status)

    def search_products(self, arguments):
        return self.products.list(**product_filters(arguments))
