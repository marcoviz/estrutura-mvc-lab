from sqlalchemy import select, or_, func, delete, update
from sqlalchemy.orm import selectinload
from database import db
from domain.errors import DomainError
from models.task import Task
from models.user import User
from models.category import Category


class Store:
    def required(self, model, identifier, label):
        entity = db.session.get(model, identifier)
        if entity is None: raise DomainError(f'{label} não encontrado', 404)
        return entity

    def tasks(self, filters=None, eager=False):
        statement = select(Task).order_by(Task.id)
        if eager: statement = statement.options(selectinload(Task.user), selectinload(Task.category))
        for key, value in (filters or {}).items():
            if key == 'q' and value:
                statement = statement.where(or_(Task.title.like(f'%{value}%'), Task.description.like(f'%{value}%')))
            elif key in ('status', 'priority', 'user_id'): statement = statement.where(getattr(Task, key) == value)
        return list(db.session.scalars(statement))

    def users(self, eager=False):
        statement = select(User).order_by(User.id)
        if eager: statement = statement.options(selectinload(User.tasks))
        return list(db.session.scalars(statement))

    def categories(self):
        statement = select(Category, func.count(Task.id)).outerjoin(Task).group_by(Category.id).order_by(Category.id)
        return list(db.session.execute(statement))

    def user_by_email(self, email):
        return db.session.scalar(select(User).where(User.email == email))

    def add(self, entity):
        db.session.add(entity)

    def delete(self, entity):
        db.session.delete(entity)

    def delete_user(self, user):
        db.session.execute(delete(Task).where(Task.user_id == user.id))
        db.session.delete(user)

    def delete_category(self, category):
        db.session.execute(update(Task).where(Task.category_id == category.id).values(category_id=None))
        db.session.delete(category)

    def commit(self):
        db.session.commit()

    def counts(self):
        return {name: db.session.scalar(select(func.count()).select_from(model))
                for name, model in [('users', User), ('categories', Category)]}
