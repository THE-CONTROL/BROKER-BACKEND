from flask import Blueprint, request, jsonify
from VestaFlask.Data.db import db_session
from VestaFlask.utils import Queries
from flask_jwt_extended import get_jwt_identity, jwt_required
from VestaFlask.Data.models import Deficit, deficit_schema, Client, deficits_schema, Admin, Notifications

deficit = Blueprint('deficit', __name__, url_prefix='/deficit/')


@deficit.post('create/<index>')
@jwt_required()
def create_deficit(index):
    cur_admin = get_jwt_identity()
    get_client = Queries.filter_one(Client, Client.id, index)
    get_admin = Queries.filter_one(Admin, Admin.id, cur_admin)

    amount = request.json['amount']
    bitcoin = request.json['bitcoin']

    if not get_client:
        return jsonify({"message": "Invalid client!"}), 400
    if get_client.deleted:
        return jsonify({"message": "This users account is deactivated!"}), 400
    if amount == "":
        return jsonify({"message": "Invalid input!"}), 400
    if float(amount) <= 0.0:
        return jsonify({"message": "Amount cannot be less than or equal to 0!"}), 400

    bitcoin = Queries.sf(bitcoin)

    username = f"{get_client.first_name} {get_client.last_name}"

    new_deficit = Deficit(amount=amount, bitcoin=bitcoin, client_id=get_client.id, username=username)
    new_notif = Notifications(
        message=f"Admin, {get_admin.first_name} {get_admin.last_name} credited client, {get_client.first_name} \
                {get_client.last_name} with deficit of ${amount}.00.")

    get_client.acct_bal -= float(amount)
    get_client.bit_bal -= float(bitcoin)
    get_client.loss += float(amount)

    admins = Queries.get_all(Admin)

    for admin in admins:
        admin.loss += float(amount)

    message_header = "You just had a loss"
    message = f"Your VestaTrading account was debited with an deficit of ${amount}.00({bitcoin} btc)"

    Queries.send_email(get_client.email, message, message_header)

    db_session.add(new_notif)
    db_session.add(new_deficit)
    db_session.commit()

    return jsonify({"heading": "Deficit was successfully created!", "content": f"You just debited \
                        {get_client.first_name} {get_client.last_name} with ${amount}({bitcoin}btc)"}), 201


@deficit.get('get/<page_size>/<page>')
@jwt_required()
def get(page, page_size):
    cur_client = get_jwt_identity()
    get_client = Queries.filter_one(Client, Client.id, cur_client)

    deficits = deficits_schema.dump(get_client.deficits)

    items = Queries.paginate(int(page), int(page_size), deficits)

    return jsonify(items), 200


@deficit.get('get/<index>')
@jwt_required()
def search(index):
    cur_client = get_jwt_identity()
    get_deficit = Queries.filter_one(Deficit, Deficit.id, index)

    if not get_deficit:
        return jsonify([]), 400
    if get_deficit.client_id != cur_client:
        return jsonify([]), 400

    get_deficit = deficit_schema.dump(get_deficit)

    return jsonify(get_deficit), 200


@deficit.get('get/all/<page_size>/<page>')
@jwt_required()
def get_all(page, page_size):
    deficits = Queries.get_all(Deficit)

    deficits = deficits_schema.dump(deficits)

    items = Queries.paginate(int(page), int(page_size), deficits)

    return jsonify(items), 200


@deficit.get('get/all/<index>')
@jwt_required()
def search_all(index):
    get_deficit = Queries.filter_one(Deficit, Deficit.id, index)

    if not get_deficit:
        return jsonify([]), 400

    get_deficit = deficit_schema.dump(get_deficit)

    return jsonify(get_deficit), 200


@deficit.get('search/all/<user_id>/<index>')
@jwt_required()
def search_user_post(user_id, index):
    get_deficit = Queries.filter_one(Deficit, Deficit.id, index)

    if not get_deficit:
        return jsonify([]), 400
    if get_deficit.client_id != int(user_id):
        return jsonify([]), 400

    get_deficit = deficit_schema.dump(get_deficit)

    return jsonify(get_deficit), 200


@deficit.get('get/<user_id>/<page_size>/<page>')
@jwt_required()
def get_user_all(user_id, page, page_size):
    get_client = Queries.filter_one(Client, Client.id, user_id)

    if not get_client:
        return jsonify({"message": "Invalid client!"}), 400

    deficits = deficits_schema.dump(get_client.deficits)

    items = Queries.paginate(int(page), int(page_size), deficits)

    return jsonify(items), 200
