function loadConfig(env = process.env) {
  const port = Number(env.PORT || 3000);
  if (!Number.isInteger(port) || port < 0 || port > 65535) throw new Error('Invalid PORT');
  return { port, host: env.HOST || '127.0.0.1', databasePath: env.DATABASE_PATH || ':memory:' };
}
module.exports = { loadConfig };
