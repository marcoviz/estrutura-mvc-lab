const { DomainError } = require('./errors');
function parseCheckout(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) throw new DomainError('Bad Request');
  const { usr: userName, eml: email, pwd: password, c_id: courseId, card } = input;
  if (typeof userName !== 'string' || !userName.trim() || typeof email !== 'string' || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
    || !Number.isInteger(courseId) || courseId <= 0 || typeof card !== 'string' || !/^\d{12,19}$/.test(card)) throw new DomainError('Bad Request');
  if (password !== undefined && (typeof password !== 'string' || !password)) throw new DomainError('Senha inválida');
  return { userName: userName.trim(), email, password, courseId, card };
}
function parseUserId(value) {
  if (!/^\d+$/.test(String(value)) || Number(value) < 1 || !Number.isSafeInteger(Number(value))) throw new DomainError('Usuário inválido');
  return Number(value);
}
module.exports = { parseCheckout, parseUserId };
