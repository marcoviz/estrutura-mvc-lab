import re
from datetime import datetime
from domain.errors import DomainError
from domain.rules import STATUSES, ROLES, TITLE_MIN, TITLE_MAX, PASSWORD_MIN, PRIORITY_MIN, PRIORITY_MAX


def object_data(data):
    if not isinstance(data, dict) or not data:
        raise DomainError('Dados inválidos')
    return data


def text(value, name, minimum=0, maximum=10000):
    if not isinstance(value, str) or not minimum <= len(value) <= maximum:
        raise DomainError(f'{name} inválido')
    return value


def integer(value, name, minimum=1, maximum=2147483647):
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise DomainError(f'{name} inválido')
    return value


def choice(value, choices, name):
    if not isinstance(value, str) or value not in choices:
        raise DomainError(f'{name} inválido')
    return value


def task_data(data, partial=False):
    data = object_data(data)
    values = dict(data) if partial else {'description': '', 'status': 'pending', 'priority': 3, **data}
    if not partial and 'title' not in values:
        raise DomainError('Título é obrigatório')
    result = {}
    for key, value in values.items():
        if key == 'title': result[key] = text(value, 'Título', TITLE_MIN, TITLE_MAX)
        elif key == 'description': result[key] = text(value, 'Descrição') if value is not None else None
        elif key == 'status': result[key] = choice(value, STATUSES, 'Status')
        elif key == 'priority': result[key] = integer(value, 'Prioridade', PRIORITY_MIN, PRIORITY_MAX)
        elif key in ('user_id', 'category_id'): result[key] = integer(value, key) if value is not None else None
        elif key == 'due_date':
            try: result[key] = datetime.strptime(value, '%Y-%m-%d') if value else None
            except (TypeError, ValueError): raise DomainError('Formato de data inválido. Use YYYY-MM-DD')
        elif key == 'tags':
            if isinstance(value, list):
                if not all(isinstance(tag, str) and ',' not in tag for tag in value):
                    raise DomainError('Tags devem ser textos sem vírgulas')
                value = ','.join(value)
            result[key] = text(value, 'Tags', maximum=500) if value is not None else None
    return result


def user_data(data, partial=False):
    data = object_data(data)
    if not partial and not all(key in data for key in ('name', 'email', 'password')):
        raise DomainError('Nome, email e senha são obrigatórios')
    result = {}
    for key, value in data.items():
        if key == 'name': result[key] = text(value, 'Nome', 1, 100)
        elif key == 'email':
            value = text(value, 'Email', 3, 150)
            if not re.fullmatch(r'[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+', value): raise DomainError('Email inválido')
            result[key] = value
        elif key == 'password': result[key] = text(value, 'Senha', PASSWORD_MIN, 1024)
        elif key == 'role': result[key] = choice(value, ROLES, 'Role')
        elif key == 'active':
            if not isinstance(value, bool): raise DomainError('Active deve ser booleano')
            result[key] = value
    return result


def category_data(data, partial=False):
    data = object_data(data)
    if not partial and 'name' not in data: raise DomainError('Nome é obrigatório')
    if not partial and 'description' not in data: data = {'description': '', **data}
    result = {}
    for key, value in data.items():
        if key == 'name': result[key] = text(value, 'Nome', 1, 100)
        elif key == 'description': result[key] = text(value, 'Descrição', maximum=300) if value is not None else None
        elif key == 'color':
            if not isinstance(value, str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', value): raise DomainError('Cor inválida')
            result[key] = value
    return result


def search_data(args):
    result = {'q': args.get('q', '')}
    if args.get('status'): result['status'] = choice(args['status'], STATUSES, 'Status')
    for key in ('priority', 'user_id'):
        if args.get(key):
            try: value = int(args[key])
            except (ValueError, TypeError): raise DomainError(f'{key} inválido')
            result[key] = integer(value, key, 1, 5 if key == 'priority' else 2147483647)
    return result
