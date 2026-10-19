"""Verify HTTP contracts and persisted effects on a disposable database only."""
import argparse
import json
import os
from pathlib import Path
import urllib.error
import urllib.request

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('project', type=int, choices=(1, 2, 3))
parser.add_argument('base_url')
parser.add_argument('--output', required=True)
parser.add_argument('--refactored', action='store_true')
parser.add_argument('--flask-root', help='Use Flask test client without a network socket (projects 1/3).')
args = parser.parse_args()
output = Path(args.output).resolve()
client = None
if args.flask_root:
    import sys
    flask_root = str(Path(args.flask_root).resolve())
    os.chdir(flask_root)
    sys.path.insert(0, flask_root)
    from app import app
    client = app.test_client()
results, checks = [], []


def check(name, actual, expected):
    passed = actual == expected
    checks.append({'name': name, 'actual': actual, 'expected': expected, 'passed': passed})
    assert passed, (name, actual, expected)


def fields(name, value, expected):
    check(name, {key: value.get(key) for key in expected}, expected)


def inspect_public(value):
    if isinstance(value, dict):
        assert not set(value) & {'password', 'passwordHash', 'senha', 'secret_key', 'card', 'pass'}, 'Secret field leaked'
        for child in value.values():
            inspect_public(child)
    elif isinstance(value, list):
        for child in value:
            inspect_public(child)


def call(method, path, expected, body=None, *, admin=True):
    headers = {'Content-Type': 'application/json'}
    if args.refactored and path.startswith('/admin/') and admin:
        headers['Authorization'] = 'Bearer ' + os.environ['TEST_ADMIN_TOKEN']
    if client:
        response = client.open(path, method=method, json=body, headers=headers)
        status, raw = response.status_code, response.get_data(as_text=True)
    else:
        request = urllib.request.Request(args.base_url + path, data=json.dumps(body).encode() if body is not None else None, method=method, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=8) as response:
                status, raw = response.status, response.read().decode()
        except urllib.error.HTTPError as error:
            status, raw = error.code, error.read().decode()
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        value = raw
    result = {'method': method, 'path': path, 'status': status, 'expected': expected,
              'shape': list(value) if isinstance(value, dict) else ('array' if isinstance(value, list) else 'text'),
              'passed': status == expected}
    results.append(result)
    assert status == expected, (method, path, status, raw[:200])
    if args.refactored:
        try:
            inspect_public(value)
        except AssertionError:
            result['passed'] = False
            raise
    return value


def project_one():
    fields('index contract', call('GET', '/', 200), {'versao': '1.0.0'})
    initial = call('GET', '/health', 200)['counts']
    call('GET', '/produtos', 200)
    product_data = {'nome': 'Produto Teste', 'descricao': 'Contrato', 'preco': 25.5, 'estoque': 10, 'categoria': 'geral'}
    product = call('POST', '/produtos', 201, product_data)['dados']['id']
    fields('product persisted', call('GET', f'/produtos/{product}', 200)['dados'], product_data)
    updated = {**product_data, 'nome': 'Produto Atualizado', 'preco': 30}
    call('PUT', f'/produtos/{product}', 200, updated)
    fields('product update persisted', call('GET', f'/produtos/{product}', 200)['dados'], updated)
    found = call('GET', '/produtos/busca?q=Atualizado&preco_min=29&preco_max=31', 200)
    check('search finds updated product', product in [row['id'] for row in found['dados']], True)
    check('search count matches rows', found['total'], len(found['dados']))
    user_data = {'nome': 'Pessoa Teste', 'email': 'contrato@example.test', 'senha': 'SenhaTeste123'}
    user = call('POST', '/usuarios', 201, user_data)['dados']['id']
    users = call('GET', '/usuarios', 200)['dados']
    check('user appears in list', user in [row['id'] for row in users], True)
    expected_user = {'id': user, 'nome': user_data['nome'], 'email': user_data['email'], 'tipo': 'cliente'}
    fields('public user contract', call('GET', f'/usuarios/{user}', 200)['dados'], expected_user)
    fields('login user contract', call('POST', '/login', 200, {'email': user_data['email'], 'senha': user_data['senha']})['dados'], expected_user)
    before_report = call('GET', '/relatorios/vendas', 200)['dados']
    order = call('POST', '/pedidos', 201, {'usuario_id': user, 'itens': [{'produto_id': product, 'quantidade': 2}]})['dados']
    check('order total uses persisted price', order['total'], 60)
    check('order decrements stock', call('GET', f'/produtos/{product}', 200)['dados']['estoque'], 8)
    orders = call('GET', '/pedidos', 200)['dados']
    check('order appears in list', order['pedido_id'] in [row['id'] for row in orders], True)
    owned = call('GET', f'/pedidos/usuario/{user}', 200)['dados']
    check('order belongs to user', len(owned), 1)
    fields('order details', owned[0], {'usuario_id': user, 'total': 60, 'status': 'pendente'})
    check('order item contract', owned[0]['itens'], [{'produto_id': product, 'produto_nome': updated['nome'], 'quantidade': 2, 'preco_unitario': 30}])
    call('PUT', f"/pedidos/{order['pedido_id']}/status", 200, {'status': 'aprovado'})
    check('status update persisted', call('GET', f'/pedidos/usuario/{user}', 200)['dados'][0]['status'], 'aprovado')
    report = call('GET', '/relatorios/vendas', 200)['dados']
    fields('sales aggregate effects', report, {'total_pedidos': before_report['total_pedidos'] + 1,
           'faturamento_bruto': before_report['faturamento_bruto'] + 60,
           'pedidos_aprovados': before_report['pedidos_aprovados'] + 1})
    if args.refactored:
        call('POST', '/pedidos', 400, {'usuario_id': user, 'itens': [{'produto_id': product, 'quantidade': 9}]})
        check('rejected order leaves stock', call('GET', f'/produtos/{product}', 200)['dados']['estoque'], 8)
        check('rejected order leaves report', call('GET', '/relatorios/vendas', 200)['dados'], report)
        call('POST', '/admin/query', 401, {'sql': 'SELECT COUNT(*) AS count FROM produtos'}, admin=False)
        call('POST', '/admin/query', 400, {'sql': 'DELETE FROM produtos'})
    unused = call('POST', '/produtos', 201, {'nome': 'Excluir Teste', 'preco': 2, 'estoque': 2, 'categoria': 'geral'})['dados']['id']
    call('DELETE', f'/produtos/{unused}', 200)
    call('GET', f'/produtos/{unused}', 404)
    count = call('POST', '/admin/query', 200, {'sql': 'SELECT COUNT(*) AS count FROM produtos'})['dados'][0]['count']
    check('create and delete effects', count, initial['produtos'] + 1)
    call('POST', '/admin/reset-db', 200, {})
    check('reset clears domain tables', call('GET', '/health', 200)['counts'], {'produtos': 0, 'usuarios': 0, 'pedidos': 0})


def project_two():
    before = call('GET', '/api/admin/financial-report', 200)
    payload = {'usr': 'Pessoa Teste', 'eml': 'contrato@example.test', 'pwd': 'SenhaTeste123', 'c_id': 2, 'card': '4111222233334444'}
    receipt = call('POST', '/api/checkout', 200, payload)
    fields('checkout contract', receipt, {'msg': 'Sucesso'})
    check('checkout returns enrollment id', isinstance(receipt.get('enrollment_id'), int), True)
    report = call('GET', '/api/admin/financial-report', 200)
    check('checkout retains course list', [row['course'] for row in report], [row['course'] for row in before])
    check('paid checkout increases revenue', report[1]['revenue'], before[1]['revenue'] + 497)
    check('paid checkout adds student', report[1]['students'], before[1]['students'] + [{'student': 'Pessoa Teste', 'paid': 497}])
    if args.refactored:
        call('POST', '/api/checkout', 400, {**payload, 'eml': 'denied@example.test', 'card': '5111222233334444'})
        check('denied checkout leaves report unchanged', call('GET', '/api/admin/financial-report', 200), report)
    # Fresh fixture has demo id=1 and the first checkout user id=2.
    call('DELETE', '/api/users/2', 200)
    check('deleting checkout user removes payment and enrollment', call('GET', '/api/admin/financial-report', 200), before)
    call('DELETE', '/api/users/1', 200)
    final = call('GET', '/api/admin/financial-report', 200)
    check('deleting demo removes dependent rows', [(row['revenue'], row['students']) for row in final], [(0, []), (0, [])])


def project_three():
    fields('index contract', call('GET', '/', 200), {'message': 'Task Manager API', 'version': '1.0'})
    fields('health contract', call('GET', '/health', 200), {'status': 'ok'})
    category = call('POST', '/categories', 201, {'name': 'Categoria Contrato', 'description': 'Teste', 'color': '#123456'})['id']
    check('category appears in list', category in [row['id'] for row in call('GET', '/categories', 200)], True)
    expected_user = {'name': 'Pessoa Teste', 'email': 'contrato@example.test', 'role': 'user'}
    user = call('POST', '/users', 201, {**expected_user, 'password': 'SenhaTeste123'})['id']
    check('user appears in list', user in [row['id'] for row in call('GET', '/users', 200)], True)
    fields('user persisted', call('GET', f'/users/{user}', 200), expected_user)
    fields('login user contract', call('POST', '/login', 200, {'email': expected_user['email'], 'password': 'SenhaTeste123'})['user'], expected_user)
    payload = {'title': 'Contrato de tarefa', 'description': 'Teste', 'priority': 2, 'user_id': user, 'category_id': category, 'tags': ['teste'], 'due_date': '2030-01-01'}
    task = call('POST', '/tasks', 201, payload)['id']
    detail = call('GET', f'/tasks/{task}', 200)
    fields('task persisted', detail, {k: v for k, v in payload.items() if k != 'due_date'})
    check('due date preserved', detail['due_date'][:10], payload['due_date'])
    listed = next(row for row in call('GET', '/tasks', 200) if row['id'] == task)
    fields('task joins contract', listed, {'user_name': expected_user['name'], 'category_name': 'Categoria Contrato'})
    check('search matches task and priority', [row['id'] for row in call('GET', '/tasks/search?q=Contrato&priority=2', 200)], [task])
    stats = call('GET', '/tasks/stats', 200)
    call('PUT', f'/tasks/{task}', 200, {'title': 'Contrato atualizado', 'status': 'done', 'priority': 3})
    fields('task update persisted', call('GET', f'/tasks/{task}', 200), {'title': 'Contrato atualizado', 'status': 'done', 'priority': 3, 'description': 'Teste', 'tags': ['teste']})
    owned = call('GET', f'/users/{user}/tasks', 200)
    check('user task contract', [row['id'] for row in owned], [task])
    fields('stats reflect completed task', call('GET', '/tasks/stats', 200), {'total': stats['total'], 'done': stats['done'] + 1})
    summary = call('GET', '/reports/summary', 200)
    check('summary status matches stats', summary['tasks_by_status']['done'], stats['done'] + 1)
    fields('user report matches task', call('GET', f'/reports/user/{user}', 200)['statistics'], {'total_tasks': 1, 'done': 1, 'completion_rate': 100})
    call('PUT', f'/users/{user}', 200, {'name': 'Pessoa Atualizada'})
    fields('partial user update preserves email', call('GET', f'/users/{user}', 200), {'name': 'Pessoa Atualizada', 'email': expected_user['email']})
    call('PUT', f'/categories/{category}', 200, {'name': 'Categoria Atualizada'})
    changed = next(row for row in call('GET', '/categories', 200) if row['id'] == category)
    fields('partial category update preserves fields', changed, {'name': 'Categoria Atualizada', 'description': 'Teste', 'color': '#123456', 'task_count': 1})
    if args.refactored:
        call('POST', '/tasks', 400, {'title': 'Invalid task', 'priority': True})
        check('invalid task leaves total unchanged', call('GET', '/tasks/stats', 200)['total'], stats['total'])
    call('DELETE', f'/tasks/{task}', 200)
    call('GET', f'/tasks/{task}', 404)
    # Keep another task linked to verify category detach and user cascade effects.
    remaining = call('POST', '/tasks', 201, {'title': 'Task vinculada', 'user_id': user, 'category_id': category})['id']
    call('DELETE', f'/categories/{category}', 200)
    check('category deletion detaches tasks', call('GET', f'/tasks/{remaining}', 200)['category_id'], None)
    call('DELETE', f'/users/{user}', 200)
    call('GET', f'/users/{user}', 404)
    call('GET', f'/tasks/{remaining}', 404)
    check('user deletion leaves no owned tasks', [row['id'] for row in call('GET', '/tasks', 200) if row['user_id'] == user], [])


try:
    {1: project_one, 2: project_two, 3: project_three}[args.project]()
finally:
    result = {'project': args.project, 'refactored': args.refactored,
              'transport': 'flask-test-client' if client else 'http', 'requests': results, 'checks': checks,
              'passed': sum(x['passed'] for x in results), 'failed': sum(not x['passed'] for x in results),
              'checks_passed': sum(x['passed'] for x in checks), 'checks_failed': sum(not x['passed'] for x in checks)}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('requests', 'checks')}))
