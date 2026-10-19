import os


def settings():
    return {'SQLALCHEMY_DATABASE_URI': os.getenv('DATABASE_URL', 'sqlite:///tasks.db'),
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SECRET_KEY': os.getenv('APP_SECRET'),
            'DEBUG': os.getenv('APP_DEBUG', '').lower() == 'true',
            'MAX_CONTENT_LENGTH': 65536}
