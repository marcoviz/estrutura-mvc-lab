from datetime import datetime, timezone

STATUSES = ('pending', 'in_progress', 'done', 'cancelled')
ROLES = ('user', 'admin', 'manager')
TITLE_MIN, TITLE_MAX = 3, 200
PASSWORD_MIN = 4  # Preserve the exercise contract; deployment needs its own policy.
PRIORITY_MIN, PRIORITY_MAX = 1, 5


def utc_now():
    # Existing SQLite DateTime columns store naive UTC; convert only at this boundary.
    return datetime.now(timezone.utc).replace(tzinfo=None)


def is_overdue(task, now=None):
    return bool(task.due_date and task.due_date < (now or utc_now())
                and task.status not in ('done', 'cancelled'))


def task_statistics(tasks, now=None):
    now = now or utc_now()
    counts = {status: 0 for status in STATUSES}
    for task in tasks:
        counts[task.status] = counts.get(task.status, 0) + 1
    total = len(tasks)
    return {'total': total, **counts, 'overdue': sum(is_overdue(t, now) for t in tasks),
            'completion_rate': round(counts['done'] / total * 100, 2) if total else 0}
