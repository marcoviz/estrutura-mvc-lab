from domain.rules import is_overdue


def task_view(task, extended=False, overdue=False):
    result = {key: getattr(task, key) for key in ('id', 'title', 'description', 'status', 'priority', 'user_id', 'category_id')}
    result.update(created_at=str(task.created_at), updated_at=str(task.updated_at),
                  due_date=str(task.due_date) if task.due_date else None,
                  tags=task.tags.split(',') if task.tags else [])
    if extended or overdue: result['overdue'] = is_overdue(task)
    if extended:
        result.update(user_name=task.user.name if task.user else None,
                      category_name=task.category.name if task.category else None)
    return result


def user_view(user):
    return {**{key: getattr(user, key) for key in ('id', 'name', 'email', 'role', 'active')},
            'created_at': str(user.created_at)}


def user_task_view(task):
    result = task_view(task, overdue=True)
    return {key: result[key] for key in ('id', 'title', 'description', 'status', 'priority', 'created_at', 'due_date', 'overdue')}


def category_view(category):
    return {**{key: getattr(category, key) for key in ('id', 'name', 'description', 'color')},
            'created_at': str(category.created_at)}
