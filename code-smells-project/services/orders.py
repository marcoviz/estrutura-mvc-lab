from collections import defaultdict
from domain.errors import DomainError
from domain.validation import number, object_data

DISCOUNT_BANDS = ((10000, .10), (5000, .05), (1000, .02))


class OrderService:
    def __init__(self, orders):
        self.orders = orders

    def create(self, data):
        data = object_data(data)
        user_id = number(data.get("usuario_id"), "Usuario ID", integer=True, minimum=1)
        items = data.get("itens")
        if not isinstance(items, list) or not items:
            raise DomainError("Pedido deve ter pelo menos 1 item")
        quantities = defaultdict(int)
        for item in items:
            item = object_data(item)
            product_id = number(item.get("produto_id"), "Produto ID", integer=True, minimum=1)
            quantities[product_id] += number(item.get("quantidade"), "Quantidade", integer=True, minimum=1)
        with self.orders.transaction():
            if not self.orders.user_exists(user_id):
                raise DomainError("Usuário não encontrado", 404)
            products = self.orders.products_by_ids(quantities)
            total = 0
            for product_id, quantity in quantities.items():
                product = products.get(product_id)
                if product is None:
                    raise DomainError(f"Produto {product_id} não encontrado")
                if product["estoque"] < quantity:
                    raise DomainError("Estoque insuficiente para " + product["nome"])
                total += product["preco"] * quantity
            order_id = self.orders.create(user_id, total)
            for product_id, quantity in quantities.items():
                self.orders.add_item(order_id, product_id, quantity, products[product_id]["preco"])
        return {"pedido_id": order_id, "total": total}

    def report(self):
        totals = self.orders.totals()
        revenue = totals["revenue"]
        rate = next((rate for threshold, rate in DISCOUNT_BANDS if revenue > threshold), 0)
        discount = revenue * rate
        return {"total_pedidos": totals["total"], "faturamento_bruto": round(revenue, 2), "desconto_aplicavel": round(discount, 2), "faturamento_liquido": round(revenue-discount, 2), "pedidos_pendentes": totals["pending"] or 0, "pedidos_aprovados": totals["approved"] or 0, "pedidos_cancelados": totals["cancelled"] or 0, "ticket_medio": round(revenue/totals["total"], 2) if totals["total"] else 0}
