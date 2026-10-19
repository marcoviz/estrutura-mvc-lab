import hashlib
import hmac
import re
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from domain.rules import utc_now


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        if re.fullmatch(r'[0-9a-f]{32}', self.password):
            # Migration-only compatibility with existing MD5 rows. Successful login upgrades it.
            valid = hmac.compare_digest(self.password, hashlib.md5(password.encode()).hexdigest())
            if valid: self.set_password(password)
            return valid
        return check_password_hash(self.password, password)

    def is_admin(self):
        return self.role == 'admin'
