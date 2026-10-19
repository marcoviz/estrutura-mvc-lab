from flask import Blueprint, request, jsonify
from controllers.tasks import TaskController

task_bp = Blueprint("task_routes", __name__)


@task_bp.route("/tasks", methods=["GET"])
def route_0():
    return jsonify(TaskController().list()), 200


@task_bp.route("/tasks/<int:task_id>", methods=["GET"])
def route_1(task_id):
    return jsonify(TaskController().get(task_id)), 200


@task_bp.route("/tasks", methods=["POST"])
def route_2():
    return jsonify(TaskController().save(request.get_json())), 201


@task_bp.route("/tasks/<int:task_id>", methods=["PUT"])
def route_3(task_id):
    return jsonify(TaskController().save(request.get_json(), task_id)), 200


@task_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
def route_4(task_id):
    return jsonify(TaskController().delete(task_id)), 200


@task_bp.route("/tasks/search", methods=["GET"])
def route_5():
    return jsonify(TaskController().search(request.args)), 200


@task_bp.route("/tasks/stats", methods=["GET"])
def route_6():
    return jsonify(TaskController().statistics()), 200
