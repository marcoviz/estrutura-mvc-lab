const sqlite3 = require('sqlite3');
const { randomBytes } = require('node:crypto');
const { hashPassword } = require('../domain/password');
class Database {
  constructor(path) { this.connection = new sqlite3.Database(path); this.queue = Promise.resolve(); }
  run(sql, params = []) {
    return new Promise((resolve, reject) => this.connection.run(sql, params, function(error) {
      if (error) reject(error); else resolve({ id: this.lastID, changes: this.changes });
    }));
  }
  get(sql, params = []) { return new Promise((resolve, reject) => this.connection.get(sql, params, (error, row) => error ? reject(error) : resolve(row))); }
  all(sql, params = []) { return new Promise((resolve, reject) => this.connection.all(sql, params, (error, rows) => error ? reject(error) : resolve(rows))); }
  exec(sql) { return new Promise((resolve, reject) => this.connection.exec(sql, error => error ? reject(error) : resolve())); }
  serialized(action) {
    const pending = this.queue.then(action);
    this.queue = pending.catch(() => {});
    return pending;
  }
  transaction(action) {
    return this.serialized(async () => {
      await this.run('BEGIN IMMEDIATE');
      try { const result = await action(); await this.run('COMMIT'); return result; }
      catch (error) { await this.run('ROLLBACK'); throw error; }
    });
  }
  async initialize() {
    await this.exec(`PRAGMA foreign_keys=ON;
      CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, pass TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT NOT NULL, price REAL NOT NULL, active INTEGER NOT NULL);
      CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, course_id INTEGER REFERENCES courses(id));
      CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER REFERENCES enrollments(id) ON DELETE CASCADE, amount REAL, status TEXT);
      CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME);`);
    if ((await this.get('SELECT COUNT(*) AS count FROM courses')).count === 0) {
      const hash = await hashPassword(randomBytes(24).toString('hex'));
      await this.transaction(async () => {
        const user = await this.run('INSERT INTO users (name,email,pass) VALUES (?,?,?)', ['Pessoa Demo', 'demo@example.test', hash]);
        await this.run('INSERT INTO courses (title,price,active) VALUES (?,?,1),(?,?,1)', ['Arquitetura de Software', 997, 'Containers', 497]);
        const enrollment = await this.run('INSERT INTO enrollments (user_id,course_id) VALUES (?,1)', [user.id]);
        await this.run('INSERT INTO payments (enrollment_id,amount,status) VALUES (?,?,?)', [enrollment.id, 997, 'PAID']);
      });
    }
  }
  async close() { await this.queue; return new Promise((resolve, reject) => this.connection.close(error => error ? reject(error) : resolve())); }
}
module.exports = { Database };
