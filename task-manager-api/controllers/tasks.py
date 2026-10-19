from domain.validation import task_data, search_data
from domain.rules import task_statistics
from models.task import Task
from models.user import User
from models.category import Category
from repositories.store import Store
from views.presenters import task_view


class TaskController:
    def __init__(self, store=None): self.store = store or Store()

    def list(self):
        return [task_view(task, extended=True) for task in self.store.tasks(eager=True)]

    def get(self, task_id):
        return task_view(self.store.required(Task, task_id, 'Task'), overdue=True)

    def save(self, payload, task_id=None):
        task = self.store.required(Task, task_id, 'Task') if task_id else Task()
        values = task_data(payload, partial=task_id is not None)
        for key, model, label in [('user_id', User, 'Usuário'), ('category_id', Category, 'Categoria')]:
            if values.get(key) is not None: self.store.required(model, values[key], label)
        for key, value in values.items(): setattr(task, key, value)
        self.store.add(task); self.store.commit()
        return task_view(task)

    def delete(self, task_id):
        self.store.delete(self.store.required(Task, task_id, 'Task')); self.store.commit()
        return {'message': 'Task deletada com sucesso'}

    def search(self, args):
        return [task_view(task) for task in self.store.tasks(search_data(args))]

    def statistics(self):
        return task_statistics(self.store.tasks())
