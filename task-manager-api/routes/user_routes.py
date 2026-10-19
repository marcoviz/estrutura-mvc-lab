from flask import Blueprint, request, jsonify
from controllers.users import UserController

user_bp = Blueprint("user_routes", __name__)


@user_bp.route("/users", methods=["GET"])
def route_0():
    return jsonify(UserController().list()), 200


@user_bp.route("/users/<int:user_id>", methods=["GET"])
def route_1(user_id):
    return jsonify(UserController().get(user_id)), 200


@user_bp.route("/users", methods=["POST"])
def route_2():
    return jsonify(UserController().save(request.get_json())), 201


@user_bp.route("/users/<int:user_id>", methods=["PUT"])
def route_3(user_id):
    return jsonify(UserController().save(request.get_json(), user_id)), 200


@user_bp.route("/users/<int:user_id>", methods=["DELETE"])
def route_4(user_id):
    return jsonify(UserController().delete(user_id)), 200


@user_bp.route("/users/<int:user_id>/tasks", methods=["GET"])
def route_5(user_id):
    return jsonify(UserController().tasks(user_id)), 200


@user_bp.route("/login", methods=["POST"])
def route_6():
    return jsonify(UserController().login(request.get_json())), 200
