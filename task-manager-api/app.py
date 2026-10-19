import os
from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException
from config import settings
from database import db
from domain.errors import DomainError
from domain.rules import utc_now
from routes.task_routes import task_bp
from routes.user_routes import user_bp
from routes.report_routes import report_bp


def create_app(overrides=None):
    application = Flask(__name__)
    application.config.update(settings())
    application.config.update(overrides or {})
    CORS(application); db.init_app(application)
    for blueprint in (task_bp, user_bp, report_bp): application.register_blueprint(blueprint)

    @application.get('/health')
    def health(): return {'status': 'ok', 'timestamp': str(utc_now())}

    @application.get('/')
    def index(): return {'message': 'Task Manager API', 'version': '1.0'}

    @application.errorhandler(Exception)
    def error(exception):
        db.session.rollback()
        if isinstance(exception, DomainError): return jsonify(error=str(exception)), exception.status
        if isinstance(exception, IntegrityError): return jsonify(error='Conflito de integridade'), 409
        if isinstance(exception, HTTPException): return jsonify(error=exception.description), exception.code
        application.logger.error('Request failed: %s', type(exception).__name__)
        return jsonify(error='Erro interno'), 500

    with application.app_context(): db.create_all()
    return application


app = create_app()
if __name__ == '__main__':
    app.run(host=os.getenv('HOST', '127.0.0.1'), port=int(os.getenv('PORT', '5000')), debug=app.config['DEBUG'])
