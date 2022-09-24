from flask import Blueprint, request, jsonify
from VestaFlask.Data.db import db_session
from VestaFlask.utils import Queries
from flask_jwt_extended import get_jwt_identity, jwt_required
from VestaFlask.Data.models import Earning, earning_schema, Client, earnings_schema, Admin, Notifications

earning = Blueprint('earning', __name__, url_prefix='/earning/')


@earning.post('create/<index>')
@jwt_required()
def create_earning(index):
    cur_admin = get_jwt_identity()
    get_client = Queries.filter_one(Client, Client.id, index)
    get_admin = Queries.filter_one(Admin, Admin.id, cur_admin)

    amount = request.json['amount']
    bitcoin = request.json['bitcoin']

    if not get_client:
        return jsonify({"message": "Invalid client!"}), 400
    if int(amount) <= 0:
        return jsonify({"message": "Amount cannot be less than or equal to 0!"}), 400
    if int(bitcoin) <= 0:
        return jsonify({"message": "Bitcoin cannot be less than or equal to 0!"}), 400

    username = f"{get_client.first_name} {get_client.last_name}"

    new_earning = Earning(amount=amount, bitcoin=bitcoin, client_id=get_client.id, username=username)
    new_notif = Notifications(
        message=f"Admin, {get_admin.first_name} {get_admin.last_name} credited client, {get_client.first_name} \
                {get_client.last_name} with earning of ${amount}.00.")

    get_client.acct_bal += int(amount)
    get_client.bit_bal += int(bitcoin)
    get_client.profit += int(amount)

    admins = Queries.get_all(Admin)

    for admin in admins:
        admin.profit += int(amount)

    message_header = "You just made an earning"
    message = f"Your VestaTrading account was credited with an earning of ${amount}.00({bitcoin} btc)"

    Queries.send_email(get_client.email, message, message_header)

    db_session.add(new_notif)
    db_session.add(new_earning)
    db_session.commit()

    return jsonify({"message": "Earning created!"}), 201


@earning.get('get/<page_size>/<page>')
@jwt_required()
def get(page, page_size):
    cur_client = get_jwt_identity()
    get_client = Queries.filter_one(Client, Client.id, cur_client)

    earnings = earnings_schema.dump(get_client.earnings)

    items = Queries.paginate(int(page), int(page_size), earnings)

    return jsonify(items), 200


@earning.get('get/<index>')
@jwt_required()
def search(index):
    cur_client = get_jwt_identity()
    get_earning = Queries.filter_one(Earning, Earning.id, index)

    if not get_earning:
        return jsonify([]), 400
    if get_earning.client_id != cur_client:
        return jsonify([]), 400

    get_earning = earning_schema.dump(get_earning)

    return jsonify(get_earning), 200


@earning.get('get/all/<page_size>/<page>')
@jwt_required()
def get_all(page, page_size):
    earnings = Queries.get_all(Earning)

    earnings = earnings_schema.dump(earnings)

    items = Queries.paginate(int(page), int(page_size), earnings)

    return jsonify(items), 200


@earning.get('get/all/<index>')
@jwt_required()
def search_all(index):
    get_earning = Queries.filter_one(Earning, Earning.id, index)

    if not get_earning:
        return jsonify([]), 400

    get_earning = earning_schema.dump(get_earning)

    return jsonify(get_earning), 200


@earning.get('search/all/<user_id>/<index>')
@jwt_required()
def search_user_post(user_id, index):
    get_earning = Queries.filter_one(Earning, Earning.id, index)

    if not get_earning:
        return jsonify([]), 400
    if get_earning.client_id != int(user_id):
        return jsonify([]), 400

    get_earning = earning_schema.dump(get_earning)

    return jsonify(get_earning), 200


@earning.get('get/<user_id>/<page_size>/<page>')
@jwt_required()
def get_user_all(user_id, page, page_size):
    get_client = Queries.filter_one(Client, Client.id, user_id)

    if not get_client:
        return jsonify({"message": "Invalid client!"}), 400

    earnings = earnings_schema.dump(get_client.earnings)

    items = Queries.paginate(int(page), int(page_size), earnings)

    return jsonify(items), 200
