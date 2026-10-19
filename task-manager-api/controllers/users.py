from domain.errors import DomainError
from domain.validation import user_data, object_data, text
from models.user import User
from repositories.store import Store
from views.presenters import user_view, task_view, user_task_view


class UserController:
    def __init__(self, store=None): self.store = store or Store()

    def list(self):
        return [{**user_view(user), 'task_count': len(user.tasks)} for user in self.store.users(eager=True)]

    def get(self, user_id):
        user = self.store.required(User, user_id, 'Usuário')
        return {**user_view(user), 'tasks': [task_view(task) for task in self.store.tasks({'user_id': user_id})]}

    def save(self, payload, user_id=None):
        user = self.store.required(User, user_id, 'Usuário') if user_id else User()
        values = user_data(payload, partial=user_id is not None)
        if 'email' in values:
            existing = self.store.user_by_email(values['email'])
            if existing and existing.id != user_id: raise DomainError('Email já cadastrado', 409)
        for key, value in values.items():
            if key == 'password': user.set_password(value)
            else: setattr(user, key, value)
        self.store.add(user); self.store.commit()
        return user_view(user)

    def delete(self, user_id):
        self.store.delete_user(self.store.required(User, user_id, 'Usuário')); self.store.commit()
        return {'message': 'Usuário deletado com sucesso'}

    def tasks(self, user_id):
        self.store.required(User, user_id, 'Usuário')
        return [user_task_view(task) for task in self.store.tasks({'user_id': user_id})]

    def login(self, payload):
        payload = object_data(payload)
        email = text(payload.get('email'), 'Email', 1, 150)
        password = text(payload.get('password'), 'Senha', 1, 1024)
        user = self.store.user_by_email(email)
        if not user or not user.check_password(password): raise DomainError('Credenciais inválidas', 401)
        if not user.active: raise DomainError('Usuário inativo', 403)
        self.store.commit()  # Persists an upgrade when the legacy MD5 branch was used.
        return {'message': 'Login realizado com sucesso', 'user': user_view(user),
                'token': 'fake-jwt-token-' + str(user.id)}  # Exercise contract, not an authentication token.
