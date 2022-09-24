from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from email_validator import validate_email, EmailNotValidError
from VestaFlask.Data.db import db_session
from VestaFlask.utils import Queries
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from VestaFlask.Data.models import Client, Admin, ResetPassword, Notifications
import string
import secrets
from datetime import datetime

auth = Blueprint('auth', __name__, url_prefix='/auth/')


@auth.post('client/register')
def client_register():
    first_name = request.json['first_name']
    last_name = request.json['last_name']
    email = request.json['email']
    phone_no = request.json['phone_no']
    country = request.json['country']
    state = request.json['state']
    city = request.json['city']
    zip_code = request.json['zip_code']
    address = request.json['address']
    annual_income = request.json['annual_income']
    investment_plan = request.json['investment_plan']
    profession = request.json['profession']
    password = request.json['password']
    con_pass = request.json['con_pass']

    another_email = Queries.filter_one(Client, Client.email, email)

    if len(first_name) < 1:
        return jsonify({"message": "First name cannot be empty!"}), 400
    if len(last_name) < 1:
        return jsonify({"message": "Last name cannot be empty!"}), 400
    try:
        validate_email(email).email
    except EmailNotValidError:
        return jsonify({"message": "Email is not valid!"}), 400
    if another_email:
        return jsonify({"message": "Email already exists!"}), 400
    if len(password) < 7:
        return jsonify({"message": "Password must be at least 7 characters!"}), 400
    if password != con_pass:
        return jsonify({"message": "Passwords don't match!"}), 400
    if not password.isalnum():
        return jsonify({"message": "Password must be alphanumeric!"}), 400
    if investment_plan != str("Bronze") and investment_plan != str("Silver") and investment_plan != str("Gold"):
        return jsonify({"message": "Please select a valid investment plan!"}), 400

    password = generate_password_hash(password)

    new_client = Client(first_name=first_name, last_name=last_name, email=email, phone_no=phone_no, country=country,
                        state=state, city=city, zip_code=zip_code, address=address, annual_income=annual_income,
                        investment_plan=investment_plan, profession=profession, password=password)
    new_notif = Notifications(message=f"{first_name} {last_name} joined as a client.")

    message_header = "Welcome to Vesta Trading"
    message = f"Hello {first_name}, we are so glad to have you with us and we hope that we can serve you well!"

    Queries.send_email(email, message, message_header)

    db_session.add(new_notif)
    db_session.add(new_client)
    db_session.commit()

    return jsonify({"message": "Client created!"}), 201


@auth.post('client/login')
def client_login():
    email = request.json['email']
    password = request.json['password']

    login_client = Queries.filter_one(Client, Client.email, email)

    if not login_client:
        return jsonify({"message": "Invalid login details!"}), 400
    if not check_password_hash(login_client.password, password):
        return jsonify({"message": "Invalid login details!"}), 400
    if login_client.deleted:
        return jsonify({"message": "Invalid login details!"}), 400

    access_token = create_access_token(identity=login_client.id)
    refresh_token = create_refresh_token(identity=login_client.id)

    login_client.logged_in = True

    new_notif = Notifications(message=f"{login_client.first_name} {login_client.last_name} logged as a client.")

    db_session.add(new_notif)
    db_session.commit()

    return jsonify({"message": "Login successful!",
                    "access_token": access_token, "refresh_token": refresh_token}), 200


@auth.post('admin/register')
def admin_register():
    first_name = request.json['first_name']
    last_name = request.json['last_name']
    email = request.json['email']
    phone_no = request.json['phone_no']
    password = request.json['password']
    con_pass = request.json['con_pass']

    another_email = Queries.filter_one(Admin, Admin.email, email)

    if len(first_name) < 1:
        return jsonify({"message": "First name cannot be empty!"}), 400
    if len(last_name) < 1:
        return jsonify({"message": "Last name cannot be empty!"}), 400
    try:
        validate_email(email).email
    except EmailNotValidError:
        return jsonify({"message": "Email is not valid!"}), 400
    if another_email:
        return jsonify({"message": "Email already exists!"}), 400
    if len(password) < 7:
        return jsonify({"message": "Password must be at least 7 characters!"}), 400
    if password != con_pass:
        return jsonify({"message": "Passwords don't match!"}), 400
    if not password.isalnum():
        return jsonify({"message": "Password must be alphanumeric!"}), 400

    password = generate_password_hash(password)

    acct_bal = 0
    bit_bal = 0
    tot_in = 0
    tot_out = 0
    profit = 0
    loss = 0

    clients = Queries.get_all(Client)

    for client in clients:
        acct_bal += client.acct_bal
        bit_bal += client.bit_bal
        tot_in += client.tot_in
        tot_out += client.tot_re
        profit += client.profit
        loss += client.loss

    new_admin = Admin(first_name=first_name, last_name=last_name, email=email, phone_no=phone_no, password=password,
                      acct_bal=acct_bal, bit_bal=bit_bal, tot_out=tot_out, tot_in=tot_in, profit=profit, loss=loss)
    new_notif = Notifications(message=f"{first_name} {last_name} joined as an admin.")

    message_header = "Welcome to Vesta Trading"
    message = f"Hello {first_name}, we are so glad to have you with us, you have admin access to Vesta Trading!"

    Queries.send_email(email, message, message_header)

    db_session.add(new_notif)
    db_session.add(new_admin)
    db_session.commit()

    return jsonify({"message": "Admin created!"}), 201


@auth.post('admin/login')
def admin_login():
    email = request.json['email']
    password = request.json['password']

    login_admin = Queries.filter_one(Admin, Admin.email, email)

    if not login_admin:
        return jsonify({"message": "Invalid login details!"}), 400
    if not check_password_hash(login_admin.password, password):
        return jsonify({"message": "Invalid login details!"}), 400

    access_token = create_access_token(identity=login_admin.id)
    refresh_token = create_refresh_token(identity=login_admin.id)

    login_admin.logged_in = True

    new_notif = Notifications(message=f"{login_admin.first_name} {login_admin.last_name} logged as an admin.")

    db_session.add(new_notif)
    db_session.commit()

    return jsonify({"message": "Login successful!",
                    "access_token": access_token, "refresh_token": refresh_token}), 200


@auth.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({"access_token": access_token}), 200


@auth.post('admin/forgot')
def admin_forgot():
    email = request.json['email']

    forgot_admin = Queries.filter_one(Admin, Admin.email, email)

    if not forgot_admin:
        return jsonify({"message": "Invalid email address!"}), 400

    alphabet = string.ascii_letters + string.digits
    reset_code = ''.join(secrets.choice(alphabet) for _ in range(10))

    message_header = "Your Password Reset Code"

    reset_email = f"Your password reset code is: <b>{reset_code}</b>"

    new_reset_code = ResetPassword(email=forgot_admin.email, reset_code=reset_code)

    Queries.send_email(email, reset_email, message_header)

    db_session.add(new_reset_code)
    db_session.commit()

    return jsonify({"message": "Reset code created!"}), 200


@auth.put("/admin/reset/password")
def check_admin_reset_code():
    reset = request.json["reset"]
    password = request.json["password"]
    con_password = request.json["con_password"]

    get_reset = Queries.filter_one(ResetPassword, ResetPassword.reset_code, reset)

    if not get_reset:
        return jsonify({"message": "Invalid reset code!"}), 400
    if len(password) < 7:
        return jsonify({"message": "Password must be at least 7 characters!"}), 400
    if password != con_password:
        return jsonify({"message": "Passwords don't match!"}), 400
    if not password.isalnum():
        return jsonify({"message": "Password must be alphanumeric!"}), 400

    password = generate_password_hash(password)

    get_admin = Queries.filter_one(Admin, Admin.email, get_reset.email)

    if not get_admin:
        return jsonify({"message": "Invalid admin!"}), 400

    if datetime.utcnow() > get_reset.expires_in:
        return jsonify({"message": "Reset code expired!"}), 400

    get_admin.password = password

    new_notif = Notifications(message=f"Admin, {get_admin.first_name} {get_admin.last_name} changed password.")

    message_header = "Password Changed"
    message = f"Hello {get_admin.first_name}, you have successfully changed your password!"

    Queries.send_email(get_admin.email, message, message_header)

    db_session.add(new_notif)
    db_session.commit()

    return jsonify({"message": "Password changed!"}), 200


@auth.post('client/forgot')
def client_forgot():
    email = request.json['email']

    forgot_client = Queries.filter_one(Client, Client.email, email)

    if not forgot_client:
        return jsonify({"message": "Invalid email address!"}), 400

    alphabet = string.ascii_letters + string.digits
    reset_code = ''.join(secrets.choice(alphabet) for _ in range(10))

    message_header = "Your Password Reset Code"

    reset_email = f"Your password reset code is: <b>{reset_code}</b>"

    new_reset_code = ResetPassword(email=forgot_client.email, reset_code=reset_code)

    Queries.send_email(email, reset_email, message_header)

    db_session.add(new_reset_code)
    db_session.commit()

    return jsonify({"message": "Reset code created!"}), 200


@auth.put("/client/reset/password")
def check_client_reset_code():
    reset = request.json["reset"]
    password = request.json["password"]
    con_password = request.json["con_password"]

    get_reset = Queries.filter_one(ResetPassword, ResetPassword.reset_code, reset)

    if not get_reset:
        return jsonify({"message": "Invalid reset code!"}), 400
    if len(password) < 7:
        return jsonify({"message": "Password must be at least 7 characters!"}), 400
    if password != con_password:
        return jsonify({"message": "Passwords don't match!"}), 400
    if not password.isalnum():
        return jsonify({"message": "Password must be alphanumeric!"}), 400

    password = generate_password_hash(password)

    get_client = Queries.filter_one(Client, Client.email, get_reset.email)

    if not get_client:
        return jsonify({"message": "Invalid client!"}), 400

    if datetime.utcnow() > get_reset.expires_in:
        return jsonify({"message": "Reset code expired!"}), 400

    get_client.password = password

    new_notif = Notifications(message=f"Client, {get_client.first_name} {get_client.last_name} changed password.")

    message_header = "Password Changed"
    message = f"Hello {get_client.first_name}, you have successfully changed your password!"

    Queries.send_email(get_client.email, message, message_header)

    db_session.add(new_notif)
    db_session.commit()

    return jsonify({"message": "Password changed!"}), 200
