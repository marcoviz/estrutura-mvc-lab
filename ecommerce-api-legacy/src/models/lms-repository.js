class LmsRepository {
  constructor(database) { this.database = database; }
  course(id) { return this.database.get('SELECT * FROM courses WHERE id=? AND active=1', [id]); }
  userByEmail(email) { return this.database.get('SELECT id FROM users WHERE email=?', [email]); }
  createUser(name, email, hash) { return this.database.run('INSERT INTO users (name,email,pass) VALUES (?,?,?)', [name, email, hash]); }
  createEnrollment(userId, courseId) { return this.database.run('INSERT INTO enrollments (user_id,course_id) VALUES (?,?)', [userId, courseId]); }
  createPayment(enrollmentId, amount, status) { return this.database.run('INSERT INTO payments (enrollment_id,amount,status) VALUES (?,?,?)', [enrollmentId, amount, status]); }
  audit(action) { return this.database.run("INSERT INTO audit_logs (action,created_at) VALUES (?,datetime('now'))", [action]); }
  async report() {
    const rows = await this.database.all(`SELECT c.id AS course_id,c.title,e.id AS enrollment_id,u.name,p.amount,p.status
      FROM courses c LEFT JOIN enrollments e ON e.course_id=c.id LEFT JOIN users u ON u.id=e.user_id
      LEFT JOIN payments p ON p.enrollment_id=e.id ORDER BY c.id,e.id`);
    const grouped = new Map();
    for (const row of rows) {
      if (!grouped.has(row.course_id)) grouped.set(row.course_id, { course: row.title, revenue: 0, students: [] });
      const course = grouped.get(row.course_id);
      if (row.enrollment_id !== null) {
        if (row.status === 'PAID') course.revenue += row.amount;
        course.students.push({ student: row.name || 'Unknown', paid: row.amount || 0 });
      }
    }
    return [...grouped.values()];
  }
  async deleteUser(userId) {
    await this.database.run('DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id=?)', [userId]);
    await this.database.run('DELETE FROM enrollments WHERE user_id=?', [userId]);
    await this.database.run('DELETE FROM users WHERE id=?', [userId]);
  }
}
module.exports = { LmsRepository };
