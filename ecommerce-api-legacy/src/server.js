const { createApp } = require('./app');
async function start() {
  const { app, database, config } = await createApp();
  const server = app.listen(config.port, config.host, () => console.log(`LMS local em http://${config.host}:${server.address().port}`));
  const stop = () => server.close(async () => { await database.close(); process.exit(0); });
  process.on('SIGINT', stop); process.on('SIGTERM', stop);
}
if (require.main === module) start().catch(error => { console.error('startup_failed', { type: error.name }); process.exitCode = 1; });
module.exports = { start };
