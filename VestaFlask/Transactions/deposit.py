import cloudinary.exceptions
from flask import Blueprint, request, jsonify
from VestaFlask.Data.db import db_session
from VestaFlask.utils import Queries
from flask_jwt_extended import get_jwt_identity, jwt_required
from VestaFlask.Data.models import Deposit, deposit_schema, Client, deposits_schema, Admin, Notifications

deposit = Blueprint('deposit', __name__, url_prefix='/deposit/')


@deposit.post('create')
@jwt_required()
def create_deposit():
    cur_client = get_jwt_identity()
    get_client = Queries.filter_one(Client, Client.id, cur_client)

    amount = request.json['amount']
    bitcoin = request.json['bitcoin']

    if not get_client:
        return jsonify({"message": "Invalid client!"}), 400
    if int(amount) <= 0:
        return jsonify({"message": "Amount cannot be less than or equal to 0!"}), 400
    if int(bitcoin) <= 0:
        return jsonify({"message": "Bitcoin cannot be less than or equal to 0!"}), 400
    if get_client.investment_plan == "Bronze":
        if get_client.tot_in + int(amount) < 500:
            return jsonify({"message": "Amount too low for your plan!"}), 400
        elif get_client.tot_in + int(amount) >= 1500:
            return jsonify({"message": "Amount too high for your plan, try migrating to another plan!"}), 400
    if get_client.investment_plan == "Silver":
        if get_client.tot_in + int(amount) < 1500:
            return jsonify({"message": "Amount too low for your plan, try migrating to another plan!"}), 400
        elif get_client.tot_in + int(amount) >= 2500:
            return jsonify({"message": "Amount too high for your plan, try migrating to another plan!"}), 400
    if get_client.investment_plan == "Gold":
        if get_client.tot_in + int(amount) < 2500:
            return jsonify({"message": "Amount too low for your plan, try migrating to another plan!"}), 400

    username = f"{get_client.first_name} {get_client.last_name}"

    new_deposit = Deposit(amount=amount, bitcoin=bitcoin, client_id=get_client.id, username=username)
    new_notif = Notifications(
        message=f"Client, {get_client.first_name} {get_client.last_name} made a deposit request of ${amount}.00.")

    message_header = "Deposit Request"
    message = f"Your just made a deposit request of ${amount}.00({bitcoin} btc in your Vesta Trading account)"

    Queries.send_email(get_client.email, message, message_header)

    db_session.add(new_notif)
    db_session.add(new_deposit)
    db_session.commit()

    return jsonify({"message": "Deposit created!"}), 201


@deposit.get('get/<page_size>/<page>')
@jwt_required()
def get(page, page_size):
    cur_client = get_jwt_identity()
    get_client = Queries.filter_one(Client, Client.id, cur_client)

    deposits = deposits_schema.dump(get_client.deposits)

    items = Queries.paginate(int(page), int(page_size), deposits)

    return jsonify(items), 200


@deposit.get('get/<index>')
@jwt_required()
def search(index):
    cur_client = get_jwt_identity()
    get_deposit = Queries.filter_one(Deposit, Deposit.id, index)

    if not get_deposit:
        return jsonify([]), 400
    if get_deposit.client_id != cur_client:
        return jsonify([]), 400

    get_deposit = deposit_schema.dump(get_deposit)

    return jsonify(get_deposit), 200


@deposit.put('proof/<index>')
@jwt_required()
def deposit_proof(index):
    cur_client = get_jwt_identity()
    get_client = Queries.filter_one(Client, Client.id, cur_client)

    proof = request.json['proof']

    proof_deposit = Queries.filter_one(Deposit, Deposit.id, int(index))

    if not get_client:
        return jsonify({"message": "Invalid client!"}), 400
    if not proof_deposit:
        return jsonify({"message": "Invalid transaction id!"}), 400
    if get_client.id != proof_deposit.client_id:
        return jsonify({"message": "Invalid transaction id!"}), 400

    new_notif = Notifications(
        message=f"Client, {get_client.first_name} {get_client.last_name} uploaded proof for deposit {index}.")

    try:
        if proof_deposit.proof == proof:
            proof = proof_deposit.proof
        else:
            proof = Queries.cloud_upload(proof)
    except cloudinary.exceptions.Error:
        return jsonify({"message": "Uploading image failed!"}), 400

    message_header = "Deposit Proof uploaded"
    message = f"You just uploaded proof of deposit - {proof_deposit.id})"

    Queries.send_email(get_client.email, message, message_header)

    db_session.add(new_notif)
    proof_deposit.proof = proof

    db_session.commit()

    return jsonify({"message": "Proof added!"}), 200


@deposit.get('get/all/<page_size>/<page>')
@jwt_required()
def get_all(page, page_size):
    deposits = Queries.get_all(Deposit)

    deposits = deposits_schema.dump(deposits)

    items = Queries.paginate(int(page), int(page_size), deposits)

    return jsonify(items), 200


@deposit.get('get/all/<index>')
@jwt_required()
def search_all(index):
    get_deposit = Queries.filter_one(Deposit, Deposit.id, index)

    if not get_deposit:
        return jsonify([]), 400

    get_deposit = deposit_schema.dump(get_deposit)

    return jsonify(get_deposit), 200


@deposit.get('search/all/<user_id>/<index>')
@jwt_required()
def search_user_post(user_id, index):
    get_deposit = Queries.filter_one(Deposit, Deposit.id, index)

    if not get_deposit:
        return jsonify([]), 400
    if get_deposit.client_id != int(user_id):
        return jsonify([]), 400

    get_deposit = deposit_schema.dump(get_deposit)

    return jsonify(get_deposit), 200


@deposit.get('get/<user_id>/<page_size>/<page>')
@jwt_required()
def get_user_all(user_id, page, page_size):
    get_client = Queries.filter_one(Client, Client.id, user_id)

    if not get_client:
        return jsonify({"message": "Invalid client!"}), 400

    deposits = deposits_schema.dump(get_client.deposits)

    items = Queries.paginate(int(page), int(page_size), deposits)

    return jsonify(items), 200


@deposit.put('approve/<index>')
@jwt_required()
def approve(index):
    cur_admin = get_jwt_identity()

    get_admin = Queries.filter_one(Admin, Admin.id, cur_admin)
    get_deposit = Queries.filter_one(Deposit, Deposit.id, index)

    if not get_deposit:
        return jsonify({"message": "Invalid deposit!"}), 400

    get_client = Queries.filter_one(Client, Client.id, get_deposit.client_id)

    if not get_client:
        return jsonify({"message": "Invalid client!"}), 400

    admins = Queries.get_all(Admin)

    if get_deposit.status:
        get_deposit.status = False
        get_client.acct_bal -= int(get_deposit.amount)
        get_client.bit_bal -= int(get_deposit.bitcoin)
        get_client.tot_in -= int(get_deposit.amount)

        for admin in admins:
            admin.acct_bal -= int(get_deposit.amount)
            admin.bit_bal -= int(get_deposit.bitcoin)
            admin.tot_in -= int(get_deposit.amount)

    else:
        get_deposit.status = True
        get_client.acct_bal += int(get_deposit.amount)
        get_client.bit_bal += int(get_deposit.bitcoin)
        get_client.tot_in += int(get_deposit.amount)

        for admin in admins:
            admin.acct_bal += int(get_deposit.amount)
            admin.bit_bal += int(get_deposit.bitcoin)
            admin.tot_in += int(get_deposit.amount)

    new_notif = Notifications(
        message=f"Admin, {get_admin.first_name} {get_admin.last_name} approved deposit - {index}.")

    message_header = "Deposit Approved"
    message = f"Your deposit - {get_deposit.id}, has been approved!"

    Queries.send_email(get_client.email, message, message_header)

    db_session.add(new_notif)
    db_session.commit()

    return jsonify({"message": "Deposit approved!"}), 201
