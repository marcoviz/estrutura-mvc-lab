const { randomBytes, scrypt, timingSafeEqual } = require('node:crypto');
const { promisify } = require('node:util');
const derive = promisify(scrypt);
async function hashPassword(password) {
  const salt = randomBytes(16).toString('hex');
  const key = await derive(password, salt, 64);
  return `scrypt:${salt}:${key.toString('hex')}`;
}
async function verifyPassword(password, encoded) {
  const [scheme, salt, digest] = String(encoded).split(':');
  if (scheme !== 'scrypt' || !salt || !digest) return false;
  const stored = Buffer.from(digest, 'hex');
  const actual = await derive(password, salt, 64);
  return stored.length === actual.length && timingSafeEqual(stored, actual);
}
module.exports = { hashPassword, verifyPassword };
