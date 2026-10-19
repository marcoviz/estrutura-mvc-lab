from database import db
from domain.rules import utc_now, is_overdue, STATUSES, PRIORITY_MIN, PRIORITY_MAX


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='pending')
    priority = db.Column(db.Integer, default=3)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)
    user = db.relationship('User', backref='tasks')
    category = db.relationship('Category', backref='tasks')

    def validate_status(self, status):
        return status in STATUSES

    def validate_priority(self, priority):
        return isinstance(priority, int) and not isinstance(priority, bool) and PRIORITY_MIN <= priority <= PRIORITY_MAX

    def is_overdue(self):
        return is_overdue(self)
