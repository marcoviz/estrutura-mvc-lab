import os
from flask import Flask
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from config import settings
from database import get_db, close_db, init_db
from domain.errors import DomainError
from models.products import Products
from models.users import Users
from models.orders import Orders
from models.admin import AdminRepository
from services.users import UserService
from services.orders import OrderService
from controllers.store import StoreController
from controllers.admin import AdminController
from views.routes import build_routes
from views.admin import build_admin


def create_app(overrides=None):
    application = Flask(__name__)
    application.config.update(settings())
    application.config.update(overrides or {})
    CORS(application)
    application.teardown_appcontext(close_db)
    def controller():
        connection = get_db()
        users, orders = Users(connection), Orders(connection)
        return StoreController(Products(connection), users, orders, UserService(users), OrderService(orders))
    application.register_blueprint(build_routes(controller))
    application.register_blueprint(build_admin(lambda: AdminController(AdminRepository(get_db()))))
    @application.errorhandler(DomainError)
    def domain_error(error): return {"erro":str(error), "sucesso":False}, error.status
    @application.errorhandler(HTTPException)
    def http_error(error): return {"erro":error.description, "sucesso":False}, error.code
    @application.errorhandler(Exception)
    def unexpected(error):
        application.logger.error("Unhandled request error: %s", type(error).__name__)
        return {"erro":"Erro interno", "sucesso":False}, 500
    with application.app_context(): init_db()
    return application


app = create_app()
if __name__ == "__main__":
    app.run(host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")), debug=app.config["DEBUG"])
