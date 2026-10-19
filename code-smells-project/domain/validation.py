import math
from .errors import DomainError

CATEGORIES = {"informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"}
ORDER_STATUSES = {"pendente", "aprovado", "enviado", "entregue", "cancelado"}
MIN_NAME = 2
MAX_NAME = 200


def object_data(data):
    if not isinstance(data, dict) or not data:
        raise DomainError("Dados inválidos")
    return data


def text(value, field, minimum=1, maximum=1000):
    if not isinstance(value, str) or not minimum <= len(value.strip()) <= maximum:
        raise DomainError(f"{field} inválido")
    return value.strip()


def password_value(value):
    if not isinstance(value, str) or not 1 <= len(value) <= 1024:
        raise DomainError("Senha inválida")
    return value


def number(value, field, integer=False, minimum=0):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        raise DomainError(f"{field} inválido")
    if value < minimum or (integer and not isinstance(value, int)):
        raise DomainError(f"{field} inválido")
    return value


def product_data(data):
    data = object_data(data)
    category = data.get("categoria", "geral")
    if not isinstance(category, str) or category not in CATEGORIES:
        raise DomainError("Categoria inválida")
    description = data.get("descricao", "")
    if not isinstance(description, str):
        raise DomainError("Descrição inválida")
    return (text(data.get("nome"), "Nome", MIN_NAME, MAX_NAME), description,
            number(data.get("preco"), "Preço"), number(data.get("estoque"), "Estoque", integer=True), category)


def product_filters(arguments):
    def amount(key):
        value = arguments.get(key)
        if value is None: return None
        try: result = float(value)
        except (TypeError, ValueError): raise DomainError("Filtro de preço inválido")
        if not math.isfinite(result): raise DomainError("Filtro de preço inválido")
        return result
    return {"term": arguments.get("q", ""), "category": arguments.get("categoria"),
            "minimum": amount("preco_min"), "maximum": amount("preco_max")}
