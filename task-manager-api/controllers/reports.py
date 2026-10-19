from domain.validation import category_data
from models.category import Category
from repositories.store import Store
from views.presenters import category_view
from services.reports import ReportService


class ReportController:
    def __init__(self, store=None): self.store = store or Store()

    def summary(self):
        return ReportService(self.store).summary()

    def user(self, user_id):
        return ReportService(self.store).user(user_id)

    def categories(self):
        return [{**category_view(category), 'task_count': count} for category, count in self.store.categories()]

    def save_category(self, payload, category_id=None):
        category = self.store.required(Category, category_id, 'Categoria') if category_id else Category()
        for key, value in category_data(payload, partial=category_id is not None).items(): setattr(category, key, value)
        self.store.add(category); self.store.commit()
        return category_view(category)

    def delete_category(self, category_id):
        self.store.delete_category(self.store.required(Category, category_id, 'Categoria')); self.store.commit()
        return {'message': 'Categoria deletada'}
