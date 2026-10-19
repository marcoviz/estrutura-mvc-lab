from flask import Blueprint, request, jsonify
from controllers.reports import ReportController

report_bp = Blueprint("report_routes", __name__)


@report_bp.route("/reports/summary", methods=["GET"])
def route_0():
    return jsonify(ReportController().summary()), 200


@report_bp.route("/reports/user/<int:user_id>", methods=["GET"])
def route_1(user_id):
    return jsonify(ReportController().user(user_id)), 200


@report_bp.route("/categories", methods=["GET"])
def route_2():
    return jsonify(ReportController().categories()), 200


@report_bp.route("/categories", methods=["POST"])
def route_3():
    return jsonify(ReportController().save_category(request.get_json())), 201


@report_bp.route("/categories/<int:cat_id>", methods=["PUT"])
def route_4(cat_id):
    return jsonify(ReportController().save_category(request.get_json(), cat_id)), 200


@report_bp.route("/categories/<int:cat_id>", methods=["DELETE"])
def route_5(cat_id):
    return jsonify(ReportController().delete_category(cat_id)), 200
