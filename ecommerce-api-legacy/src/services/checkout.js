const { DomainError } = require('../domain/errors');
const { hashPassword } = require('../domain/password');
class SimulatedPaymentGateway {
  async authorize(card) { return card.startsWith('4') ? 'PAID' : 'DENIED'; }
}
class CheckoutService {
  constructor(database, repository, gateway) { this.database = database; this.repository = repository; this.gateway = gateway; }
  async checkout(input) {
    // Compute expensive KDF outside the transaction. This gateway is deliberately local.
    const hash = input.password ? await hashPassword(input.password) : null;
    return this.database.transaction(async () => {
      const course = await this.repository.course(input.courseId);
      if (!course) throw new DomainError('Curso não encontrado', 404);
      let user = await this.repository.userByEmail(input.email);
      if (!user && !hash) throw new DomainError('Senha é obrigatória para novo usuário');
      const status = await this.gateway.authorize(input.card);
      if (status !== 'PAID') throw new DomainError('Pagamento recusado');
      if (!user) user = await this.repository.createUser(input.userName, input.email, hash);
      const enrollment = await this.repository.createEnrollment(user.id, course.id);
      await this.repository.createPayment(enrollment.id, course.price, status);
      await this.repository.audit(`Checkout curso ${course.id} por ${user.id}`);
      return { msg: 'Sucesso', enrollment_id: enrollment.id };
    });
  }
}
module.exports = { CheckoutService, SimulatedPaymentGateway };
