# Playbook de transformação

Exemplos são padrões mínimos para adaptar à stack e à unidade de trabalho real; não são código pronto de um projeto específico. Cada transformação inclui um teste que prova efeito observável.

## T01 — Parâmetros SQL (AP-01)

Antes (Python):
```python
row = conn.execute("SELECT * FROM users WHERE email = '" + email + "'").fetchone()
```
Depois:
```python
row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
```
Verificar: apóstrofo permanece dado, entrada não altera predicado. Identificadores/ordenação exigem allowlist, não placeholder de valor.

## T02 — Secret e DTO público (AP-02)

Antes:
```python
SECRET_KEY = "fixed-key"
def present(user):
    return dict(user)
```
Depois:
```python
SECRET_KEY = os.environ["APP_SECRET"]
def present(user):
    return {"id": user["id"], "name": user["name"]}
```
Verificar: respostas e logs não contêm senha/hash/secret; ausência de config produz erro de inicialização legível, sem imprimir valor.

## T03 — Controller e caso de uso (AP-03/AP-05)

Antes (JavaScript):
```javascript
app.post('/orders', async (req, res) => {
  const total = await calculateFromDatabase(req.body);
  await writeSeveralTables(req.body, total);
  res.status(201).json({ total });
});
```
Depois:
```javascript
const createOrder = service => async (req, res, next) => {
  try { res.status(201).json(await service.create(req.body)); }
  catch (error) { next(error); }
};
router.post('/orders', validateOrder, createOrder(orderService));
```
Verificar: serviço testa regras sem servidor; router não conhece SQL. Não manter cálculo/SQL escondidos numa nova God Class de service.

## T04 — Unidade transacional (AP-04)

Antes:
```python
save_order(conn, order)
conn.commit()
save_items(conn, items)
conn.commit()
```
Depois:
```python
with conn:
    save_order(conn, order)
    save_items(conn, items)
```
Verificar: falha no segundo passo reverte primeiro. Adaptar semântica autocommit/BEGIN e fechamento da conexão ao driver; não assumir que `with` fecha o sqlite3.

## T05 — Batch em vez de N+1 (AP-06)

Antes:
```python
for order in orders:
    order["items"] = find_items(order["id"])
```
Depois:
```python
items = find_items_for_orders([order["id"] for order in orders])
for order in orders:
    order["items"] = items.get(order["id"], [])
```
Verificar: consultas permanecem limitadas ao aumentar fixtures, sem perder pedidos sem itens. ORM pode usar eager loading equivalente.

## T06 — Validação compartilhada (AP-07)

Antes:
```javascript
const amount = Number(req.body.amount);
await service.create(amount);
```
Depois:
```javascript
function parseAmount(value) {
  if (typeof value !== 'number' || !Number.isFinite(value) || value < 0)
    throw new ValidationError('amount inválido');
  return value;
}
await service.create(parseAmount(req.body.amount));
```
Verificar: null/string/NaN/negativo não chegam à escrita. Reutilizar validação em create/update sem alterar campos externos.

## T07 — Erros em fronteira única (AP-08)

Antes:
```javascript
try { return await action(); }
catch (err) { res.status(500).json({ error: err.stack }); }
```
Depois:
```javascript
app.use((err, req, res, next) => {
  const known = err instanceof DomainError;
  if (!known) logger.error({ requestId: req.id }, 'request failed');
  res.status(known ? err.status : 500)
    .json({ error: known ? err.message : 'Internal error' });
});
```
Verificar: erros esperados mantêm status; erro inesperado não vaza stack/SQL e não derruba processo. Adapte assinatura ao framework.

## T08 — Substituição de API legada (AP-09)

Antes (SQLAlchemy):
```python
user = User.query.get(user_id)
```
Depois:
```python
user = db.session.get(User, user_id)
```
Verificar: entidade existente/ausente e escopo de sessão preservados, sem LegacyAPIWarning. Para utcnow, migrar conscientemente aware/naive; não substituir texto sem testar comparação e serialização.

## T09 — Política nomeada (AP-10)

Antes:
```python
if revenue > 10000:
    discount = revenue * .1
```
Depois:
```python
DISCOUNT_THRESHOLD = 10000
DISCOUNT_RATE = .1
if revenue > DISCOUNT_THRESHOLD:
    discount = revenue * DISCOUNT_RATE
```
Verificar: fronteira exata mantém `>` e não vira `>=`; política pode ser tabela quando há várias faixas.

## T10 — Nomes locais expressivos (AP-11)

Antes:
```javascript
const cid = req.body.c_id;
const cc = req.body.card;
```
Depois:
```javascript
const courseId = req.body.c_id;
const card = req.body.card;
```
Verificar: integração continua enviando c_id/card; renomear variável interna não obriga migrar contrato público.

## T11 — Eliminar estado morto (AP-12)

Antes:
```javascript
let totalRevenue = 0;
module.exports = { report, totalRevenue };
```
Depois:
```javascript
module.exports = { report };
```
Verificar: nenhum consumidor usa export removido; relatório calcula do banco e não de cache divergente. Não remover imports com efeito colateral sem investigar.

## T12 — Password KDF (AP-02)

Antes (Python):
```python
stored = hashlib.md5(password.encode()).hexdigest()
```
Depois:
```python
from werkzeug.security import generate_password_hash, check_password_hash
stored = generate_password_hash(password)
assert check_password_hash(stored, password)
```
Verificar: salts distintos e senha incorreta recusada; planejar upgrade de dados legados sem publicar hashes. Node pode usar crypto.scrypt com salt, parâmetros e comparação constante.

## T13 — Fronteira administrativa (AP-13)

Antes:
```python
@routes.post('/admin/reset')
def reset():
    repository.reset()
    return {}, 200
```
Depois:
```python
@routes.post('/admin/reset')
@require_admin
def reset():
    repository.reset()
    return {}, 200
```
Verificar: anônimo negado, ator autorizado consegue operar no DB de teste; rota mantém URL e ação aprovada, e SQL arbitrário não é liberado por validação superficial.

## T14 — Integridade de exclusão (AP-14)

Antes:
```python
conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
```
Depois:
```python
with conn:
    conn.execute('DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)', (user_id,))
    conn.execute('DELETE FROM enrollments WHERE user_id = ?', (user_id,))
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
```
Verificar: nenhuma referência órfã, rollback se parte falhar. Cascade versus restrict é política do domínio a confirmar; não escolher destruição adicional sem a aprovação do plano.
