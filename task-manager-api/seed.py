"""Optional non-destructive sample data. Explicit DEMO_PASSWORD is required."""
import os
from sqlalchemy import select
from app import app
from database import db
from models.user import User
from models.category import Category
from models.task import Task


def seed():
    password = os.environ.get('DEMO_PASSWORD')
    if not password or len(password) < 4: raise SystemExit('Set DEMO_PASSWORD with at least 4 characters')
    with app.app_context():
        if db.session.scalar(select(User.id).limit(1)) is not None:
            raise SystemExit('Database is not empty; no rows changed')
        user = User(name='Pessoa Demo', email='demo@example.test', role='user'); user.set_password(password)
        category = Category(name='Estudo', description='Exemplo local', color='#355C7D')
        db.session.add_all([user, category]); db.session.flush()
        db.session.add(Task(title='Explorar arquitetura', user_id=user.id, category_id=category.id))
        db.session.commit()
        print('Sample created without deleting existing data')


if __name__ == '__main__': seed()
