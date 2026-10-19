import os
import sys
import hashlib
import unittest
from pathlib import Path
from datetime import timedelta
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
from app import create_app
from database import db
from models.user import User
from models.task import Task
from models.category import Category
from domain.rules import utc_now
from sqlalchemy import event, select


class ArchitectureTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
        self.client = self.app.test_client()
        self.context = self.app.app_context(); self.context.push()

    def tearDown(self):
        db.session.remove(); db.drop_all(); self.context.pop()

    def user(self, email='test@example.test'):
        response = self.client.post('/users', json={'name': 'Pessoa', 'email': email, 'password': 'test-only-password'})
        self.assertEqual(response.status_code, 201)
        self.assertNotIn('password', response.json)
        return response.json['id']

    def test_password_dto_and_legacy_login_upgrade(self):
        identifier = self.user()
        user = db.session.get(User, identifier)
        self.assertTrue(user.password.startswith('scrypt:'))
        user.password = hashlib.md5(b'legacy').hexdigest(); db.session.commit()
        result = self.client.post('/login', json={'email': user.email, 'password': 'legacy'})
        self.assertEqual(result.status_code, 200); self.assertNotIn('password', result.json['user'])
        db.session.expire_all(); self.assertTrue(db.session.get(User, identifier).password.startswith('scrypt:'))
        self.assertEqual(self.client.post('/login', json={'email': user.email, 'password': 'wrong'}).status_code, 401)

    def test_validation_and_failed_write_leave_no_partial_state(self):
        self.user()
        self.assertEqual(self.client.get('/tasks/search?priority=abc').status_code, 400)
        self.assertEqual(self.client.post('/tasks', json={'title': 'Task', 'priority': True}).status_code, 400)
        self.assertEqual(self.client.post('/tasks', json={'title': 'Task', 'user_id': 999}).status_code, 404)
        self.assertEqual(self.client.post('/users', json={'name': 'Another', 'email': 'test@example.test', 'password': 'abcd'}).status_code, 409)
        self.assertEqual(db.session.scalar(select(db.func.count()).select_from(Task)), 0)
        self.assertEqual(db.session.scalar(select(db.func.count()).select_from(User)), 1)

    def test_bound_queries_and_shared_overdue_rule(self):
        category = Category(name='Study'); db.session.add(category)
        for index in range(6):
            user = User(name=f'User {index}', email=f'{index}@example.test'); user.set_password('test')
            db.session.add(user); db.session.flush()
            db.session.add(Task(title='Task', user_id=user.id, category=category, due_date=utc_now()-timedelta(days=1)))
        db.session.commit(); db.session.remove()
        queries = []
        def capture(_conn, _cursor, statement, _parameters, _context, _executemany):
            if statement.lstrip().upper().startswith('SELECT'): queries.append(statement)
        event.listen(db.engine, 'before_cursor_execute', capture)
        try:
            result = self.client.get('/tasks'); self.assertEqual(result.status_code, 200)
            self.assertEqual(len(queries), 3); self.assertTrue(all(task['overdue'] for task in result.json))
            queries.clear(); self.client.get('/users'); self.assertEqual(len(queries), 2)
            queries.clear(); self.client.get('/categories'); self.assertEqual(len(queries), 1)
        finally: event.remove(db.engine, 'before_cursor_execute', capture)
        self.assertEqual(self.client.get('/tasks/stats').json['overdue'], 6)
        self.assertEqual(self.client.get('/reports/summary').json['overdue']['count'], 6)
        self.client.put('/tasks/1', json={'status': 'done'})
        self.assertFalse(self.client.get('/tasks/1').json['overdue'])
        self.assertEqual(self.client.get('/tasks/stats').json['overdue'], 5)

    def test_category_delete_detaches_and_user_delete_removes_tasks(self):
        user = self.user()
        category = self.client.post('/categories', json={'name': 'Study'}).json['id']
        task = self.client.post('/tasks', json={'title': 'Task', 'user_id': user, 'category_id': category}).json['id']
        self.assertEqual(self.client.delete(f'/categories/{category}').status_code, 200)
        self.assertIsNone(self.client.get(f'/tasks/{task}').json['category_id'])
        self.assertEqual(self.client.delete(f'/users/{user}').status_code, 200)
        self.assertEqual(self.client.get(f'/tasks/{task}').status_code, 404)

    def test_category_create_defaults_description_and_partial_update_preserves_it(self):
        created = self.client.post('/categories', json={'name': 'Study'})
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.json['description'], '')
        category_id = created.json['id']
        updated = self.client.put(f'/categories/{category_id}', json={'color': '#123456'})
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json['description'], '')
        self.assertEqual(updated.json['color'], '#123456')


if __name__ == '__main__': unittest.main()
