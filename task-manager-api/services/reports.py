from collections import defaultdict
from datetime import timedelta
from domain.rules import utc_now, task_statistics, is_overdue, STATUSES
from models.user import User


class ReportService:
    def __init__(self, store): self.store = store

    def summary(self):
        tasks, users, counts = self.store.tasks(), self.store.users(), self.store.counts()
        now = utc_now(); statistics = task_statistics(tasks, now)
        by_user = defaultdict(list)
        for task in tasks: by_user[task.user_id].append(task)
        productivity = []
        for user in users:
            stats = task_statistics(by_user[user.id], now)
            productivity.append({'user_id': user.id, 'user_name': user.name, 'total_tasks': stats['total'],
                                 'completed_tasks': stats['done'], 'completion_rate': stats['completion_rate']})
        return {'generated_at': str(now),
                'overview': {'total_tasks': len(tasks), 'total_users': counts['users'], 'total_categories': counts['categories']},
                'tasks_by_status': {status: statistics[status] for status in STATUSES},
                'tasks_by_priority': {name: sum(t.priority == priority for t in tasks)
                                     for priority, name in enumerate(('critical', 'high', 'medium', 'low', 'minimal'), 1)},
                'overdue': {'count': statistics['overdue'], 'tasks': [
                    {'id': t.id, 'title': t.title, 'due_date': str(t.due_date), 'days_overdue': (now-t.due_date).days}
                    for t in tasks if is_overdue(t, now)]},
                'recent_activity': {'tasks_created_last_7_days': sum(t.created_at >= now-timedelta(days=7) for t in tasks),
                                    'tasks_completed_last_7_days': sum(t.status == 'done' and t.updated_at >= now-timedelta(days=7) for t in tasks)},
                'user_productivity': productivity}

    def user(self, user_id):
        user = self.store.required(User, user_id, 'Usuário')
        tasks = self.store.tasks({'user_id': user_id}); stats = task_statistics(tasks)
        total = stats.pop('total')
        return {'user': {'id': user.id, 'name': user.name, 'email': user.email},
                'statistics': {'total_tasks': total, **stats, 'high_priority': sum(t.priority <= 2 for t in tasks)}}
