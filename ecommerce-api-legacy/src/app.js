const express = require('express');
const { loadConfig } = require('./config');
const { Database } = require('./models/database');
const { LmsRepository } = require('./models/lms-repository');
const { CheckoutService, SimulatedPaymentGateway } = require('./services/checkout');
const { LmsController } = require('./controllers/lms-controller');
const { buildRoutes } = require('./views/routes');
const { DomainError } = require('./domain/errors');
async function createApp(options = {}) {
  const config = options.config || loadConfig();
  const database = options.database || new Database(config.databasePath);
  await database.initialize();
  const repository = new LmsRepository(database);
  const checkout = new CheckoutService(database, repository, options.gateway || new SimulatedPaymentGateway());
  const app = express();
  app.disable('x-powered-by');
  app.use(express.json({ limit: '64kb' }));
  app.use(buildRoutes(new LmsController(database, repository, checkout)));
  app.use((error, _req, res, _next) => {
    if (error instanceof DomainError) return res.status(error.status).send(error.message);
    if (error.type === 'entity.parse.failed') return res.status(400).send('Bad Request');
    if (error.type === 'entity.too.large') return res.status(413).send('Payload too large');
    console.error('request_failed', { type: error.name });
    return res.status(500).send('Erro interno');
  });
  return { app, database, config };
}
module.exports = { createApp };
