const test = require('node:test');
const assert = require('node:assert/strict');
const { Database } = require('../src/models/database');
const { LmsRepository } = require('../src/models/lms-repository');
const { CheckoutService, SimulatedPaymentGateway } = require('../src/services/checkout');
const { parseCheckout } = require('../src/domain/validation');
const { hashPassword, verifyPassword } = require('../src/domain/password');
async function fixture(t) {
  const database = new Database(':memory:');
  await database.initialize();
  t.after(() => database.close());
  const repository = new LmsRepository(database);
  return { database, repository, checkout: new CheckoutService(database, repository, new SimulatedPaymentGateway()) };
}
const input = (email = 'test@example.test') => parseCheckout({ usr: 'Pessoa', eml: email, pwd: 'test-only-password', c_id: 2, card: '4111222233334444' });
test('salted KDF verifies without deterministic or reversible password storage', async () => {
  const first = await hashPassword('example'), second = await hashPassword('example');
  assert.notEqual(first, second); assert.equal(await verifyPassword('example', first), true);
  assert.equal(await verifyPassword('incorrect', first), false);
});
test('input validates types before payment and SQL', () => {
  assert.throws(() => parseCheckout({ usr: 'X', eml: 'x@example.test', c_id: 2, card: 4111 }), /Bad Request/);
  assert.throws(() => parseCheckout([]), /Bad Request/);
});
test('failure after enrollment rolls back user, enrollment, payment and audit', async t => {
  const { database, repository, checkout } = await fixture(t);
  const before = await database.get('SELECT COUNT(*) AS count FROM enrollments');
  repository.createPayment = async () => { throw new Error('injected-storage-failure'); };
  await assert.rejects(checkout.checkout(input()), /injected-storage-failure/);
  assert.equal(await repository.userByEmail('test@example.test'), undefined);
  assert.deepEqual(await database.get('SELECT COUNT(*) AS count FROM enrollments'), before);
  assert.equal((await database.get('SELECT COUNT(*) AS count FROM audit_logs')).count, 0);
});
test('serialized concurrent checkout commits complete units and report executes one query', async t => {
  const { database, repository, checkout } = await fixture(t);
  const results = await Promise.all([checkout.checkout(input('one@example.test')), checkout.checkout(input('two@example.test'))]);
  assert.notEqual(results[0].enrollment_id, results[1].enrollment_id);
  assert.equal((await database.get('SELECT COUNT(*) AS count FROM payments')).count, 3);
  let queries = 0; const all = database.all.bind(database);
  database.all = (...args) => { queries++; return all(...args); };
  const report = await repository.report();
  assert.equal(queries, 1); assert.equal(report[1].revenue, 994); assert.equal(report[1].students.length, 2);
});
test('denied payment does not persist user and delete removes dependent rows', async t => {
  const { database, repository, checkout } = await fixture(t);
  await assert.rejects(checkout.checkout({ ...input(), card: '5111222233334444' }), /Pagamento recusado/);
  assert.equal(await repository.userByEmail('test@example.test'), undefined);
  await database.transaction(() => repository.deleteUser(1));
  assert.equal((await database.get('SELECT COUNT(*) AS count FROM enrollments')).count, 0);
  assert.equal((await database.get('SELECT COUNT(*) AS count FROM payments')).count, 0);
  assert.equal((await database.get('PRAGMA foreign_key_check')), undefined);
});
