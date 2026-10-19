const { parseCheckout, parseUserId } = require('../domain/validation');
class LmsController {
  constructor(database, repository, checkout) { this.database = database; this.repository = repository; this.checkoutService = checkout; }
  checkout = async (req, res) => { res.status(200).json(await this.checkoutService.checkout(parseCheckout(req.body))); };
  report = async (_req, res) => { res.json(await this.database.serialized(() => this.repository.report())); };
  deleteUser = async (req, res) => {
    const userId = parseUserId(req.params.id);
    await this.database.transaction(() => this.repository.deleteUser(userId));
    res.send('Usuário e relações vinculadas deletados.');
  };
}
module.exports = { LmsController };
