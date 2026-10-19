const { Router } = require('express');
const asyncRoute = handler => (req, res, next) => Promise.resolve(handler(req, res)).catch(next);
function buildRoutes(controller) {
  const router = Router();
  router.post('/api/checkout', asyncRoute(controller.checkout));
  router.get('/api/admin/financial-report', asyncRoute(controller.report));
  router.delete('/api/users/:id', asyncRoute(controller.deleteUser));
  return router;
}
module.exports = { buildRoutes };
