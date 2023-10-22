from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from email_validator import validate_email, EmailNotValidError
from VestaFlask.Data.db import db_session
from VestaFlask.utils import Queries
from flask_jwt_extended import get_jwt_identity, jwt_required
from VestaFlask.Data.models import Client, client_schema, clients_schema, Notifications, Admin
import cloudinary.exceptions

client = Blueprint('client', __name__, url_prefix='/client/')


@client.get('get')
@jwt_required()
def get():
    cur_client = get_jwt_identity()
    get_client = Queries.filter_one(Client, Client.id, cur_client)

    if get_client.deleted:
        return jsonify({"message": "Account deactivated!"}), 400

    get_client = client_schema.dump(get_client)

    return jsonify(get_client), 200


@client.put('update')
@jwt_required()
def update_client():
    cur_client = get_jwt_identity()
    get_client = Queries.filter_one(Client, Client.id, cur_client)

    first_name = request.json['first_name']
    last_name = request.json['last_name']
    email = request.json['email']
    picture = request.json['picture']
    investment_plan = request.json['investment_plan']

    another_email = Queries.filter_one(Client, Client.email, email)

    if len(first_name) < 1:
        return jsonify({"message": "First name cannot be empty!"}), 400
    if len(last_name) < 1:
        return jsonify({"message": "Last name cannot be empty!"}), 400
    try:
        validate_email(email).email
    except EmailNotValidError:
        return jsonify({"message": "Email is not valid!"}), 400
    if another_email and another_email != get_client:
        return jsonify({"message": "Email already exists!"}), 400
    if get_client.deleted:
        return jsonify({"message": "Account deleted!"}), 400

    try:
        if picture == get_client.picture:
            picture = get_client.picture
        else:
            picture = Queries.cloud_upload(picture)
    except cloudinary.exceptions.Error:
        return jsonify({"message": "Uploading image failed!"}), 400

    get_client.first_name = first_name
    get_client.last_name = last_name
    get_client.email = email
    get_client.picture = picture
    get_client.investment_plan = investment_plan

    new_notif = Notifications(message=f"Client, {get_client.first_name} {get_client.last_name} updated account \
    details.")

    message_header = "Account Updated"
    message = f"Hello {get_client.first_name}, you have successfully updated your account!"

    Queries.send_email(get_client.email, message, message_header)

    db_session.add(new_notif)
    db_session.commit()

    return jsonify({"message": "Client updated!"}), 200


@client.put('change/password')
@jwt_required()
def change_password():
    cur_client = get_jwt_identity()
    get_client = Queries.filter_one(Client, Client.id, cur_client)

    cur_password = request.json['cur_password']
    new_password = request.json['new_password']
    con_password = request.json['con_password']

    if not check_password_hash(get_client.password, cur_password):
        return jsonify({"message": "Invalid password!"}), 400
    if len(new_password) < 7:
        return jsonify({"message": "Password must be at least 7 characters!"}), 400
    if new_password != con_password:
        return jsonify({"message": "Passwords don't match!"}), 400
    if not new_password.isalnum():
        return jsonify({"message": "Password must be alphanumeric!"}), 400
    if get_client.deleted:
        return jsonify({"message": "Account deactivated!"}), 400

    new_password = generate_password_hash(new_password)

    get_client.password = new_password

    new_notif = Notifications(message=f"Client, {get_client.first_name} {get_client.last_name} changed password.")

    message_header = "Password Changed"
    message = f"Hello {get_client.first_name}, you have successfully changed your password!"

    Queries.send_email(get_client.email, message, message_header)

    db_session.add(new_notif)
    db_session.commit()

    return jsonify({"message": "Password updated!"}), 200


@client.delete('delete')
@jwt_required()
def delete_client():
    cur_client = get_jwt_identity()
    get_client = Queries.filter_one(Client, Client.id, cur_client)

    if get_client.deleted:
        return jsonify({"message": "Account deactivated!"}), 400
    if get_client.acct_bal > 100:
        return jsonify({"message": f"You still have ${get_client.acct_bal}.00 in your account, withdraw before \
        deleting your account!"}), 400

    new_notif = Notifications(message=f"Client, {get_client.first_name} {get_client.last_name} deactivated account.")

    message_header = "Account Deactivated"
    message = f"Hello {get_client.first_name}, you have successfully deactivated your account!"

    Queries.send_email(get_client.email, message, message_header)

    db_session.add(new_notif)
    get_client.deleted = True
    get_client.logged_in = False
    db_session.commit()

    return jsonify({"message": "Client deleted!"}), 200


@client.put('logout')
@jwt_required()
def logout():
    cur_client = get_jwt_identity()
    get_client = Queries.filter_one(Client, Client.id, cur_client)

    get_client.logged_in = False

    new_notif = Notifications(message=f"Client, {get_client.first_name} {get_client.last_name} logged out.")

    db_session.add(new_notif)
    db_session.commit()

    return jsonify({"message": "Password updated!"}), 200


@client.get('/username')
@jwt_required()
def get_username():
    cur_client = get_jwt_identity()
    get_client = Queries.filter_one(Client, Client.id, cur_client)

    if get_client.deleted:
        return jsonify({"message": "Account deactivated!"}), 400

    return jsonify(get_client.first_name), 200


@client.get('get/<page_size>/<page>')
@jwt_required()
def get_all_clients(page, page_size):
    clients = Queries.get_all(Client)

    clients = clients_schema.dump(clients)

    items = Queries.paginate(int(page), int(page_size), clients)

    return jsonify(items), 200


@client.put('activate/<index>')
@jwt_required()
def activate_client(index):
    cur_admin = get_jwt_identity()

    get_admin = Queries.filter_one(Admin, Admin.id, cur_admin)
    get_client = Queries.filter_one(Client, Client.id, index)

    if get_client.deleted:
        get_client.deleted = False
        new_notif = Notifications(message=f"Admin, {get_admin.first_name} {get_admin.last_name} activated client, \
        {get_client.first_name} {get_client.last_name}'s account.")

        message_header = "Account Activated"
        message = f"Hello {get_client.first_name}, your account has been reactivated!"
    else:
        get_client.deleted = True
        get_client.logged_in = False
        new_notif = Notifications(message=f"Admin, {get_admin.first_name} {get_admin.last_name} deactivated client, \
        {get_client.first_name} {get_client.last_name}'s account.")

        message_header = "Account Deactivated"
        message = f"Hello {get_client.first_name}, your account has been deactivated!"

    Queries.send_email(get_client.email, message, message_header)

    db_session.add(new_notif)
    db_session.commit()

    return jsonify({"message": "Client deleted!"}), 200


@client.get('get/<index>')
@jwt_required()
def search_all(index):

    first_client = Queries.filter_one(Client, Client.id, index)
    sec_client = Queries.filter_one(Client, Client.first_name, index)
    third_client = Queries.filter_one(Client, Client.last_name, index)
    fourth_client = Queries.filter_one(Client, Client.email, index)

    get_client = first_client or sec_client or third_client or fourth_client

    if not get_client:
        return jsonify([]), 400

    get_client = client_schema.dump(get_client)

    return jsonify(get_client), 200


@client.get('get/logged_in')
@jwt_required()
def get_logged_in():
    cur_client = get_jwt_identity()
    get_client = Queries.filter_one(Client, Client.id, cur_client)

    if not get_client:
        return jsonify({"message": "Invalid client!"}), 400
    if get_client.deleted:
        return jsonify({"message": "Account deleted!"}), 400

    return jsonify(get_client.logged_in), 200
