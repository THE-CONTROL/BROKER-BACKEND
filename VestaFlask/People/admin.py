from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from email_validator import validate_email, EmailNotValidError
from VestaFlask.Data.db import db_session
from VestaFlask.utils import Queries
from flask_jwt_extended import get_jwt_identity, jwt_required
from VestaFlask.Data.models import Admin, admin_schema, Notifications, notifications_schema
import cloudinary.exceptions

admin = Blueprint('admin', __name__, url_prefix='/admin/')


@admin.get('get')
@jwt_required()
def get():
    cur_admin = get_jwt_identity()
    get_admin = Queries.filter_one(Admin, Admin.id, cur_admin)

    get_admin = admin_schema.dump(get_admin)

    return jsonify(get_admin), 200


@admin.put('update')
@jwt_required()
def update_admin():
    cur_admin = get_jwt_identity()
    get_admin = Queries.filter_one(Admin, Admin.id, cur_admin)

    first_name = request.json['first_name']
    last_name = request.json['last_name']
    email = request.json['email']
    picture = request.json['picture']

    another_email = Queries.filter_one(Admin, Admin.email, email)

    if len(first_name) < 1:
        return jsonify({"message": "First name cannot be empty!"}), 400
    if len(last_name) < 1:
        return jsonify({"message": "Last name cannot be empty!"}), 400
    try:
        validate_email(email).email
    except EmailNotValidError:
        return jsonify({"message": "Email is not valid!"}), 400
    if another_email and another_email != get_admin:
        return jsonify({"message": "Email already exists!"}), 400

    try:
        if picture == get_admin.picture:
            picture = get_admin.picture
        else:
            picture = Queries.cloud_upload(picture)
    except cloudinary.exceptions.Error:
        return jsonify({"message": "Uploading image failed!"}), 400

    get_admin.first_name = first_name
    get_admin.last_name = last_name
    get_admin.email = email
    get_admin.picture = picture

    new_notif = Notifications(message=f"Admin, {get_admin.first_name} {get_admin.last_name} updated account details.")

    message_header = "Account Updated"
    message = f"Hello {get_admin.first_name}, you have successfully updated your account!"

    Queries.send_email(get_admin.email, message, message_header)

    db_session.add(new_notif)
    db_session.commit()

    return jsonify({"message": "Admin updated!"}), 200


@admin.put('change/password')
@jwt_required()
def change_password():
    cur_admin = get_jwt_identity()
    get_admin = Queries.filter_one(Admin, Admin.id, cur_admin)

    cur_password = request.json['cur_password']
    new_password = request.json['new_password']
    con_password = request.json['con_password']

    if not check_password_hash(get_admin.password, cur_password):
        return jsonify({"message": "Invalid password!"}), 400
    if len(new_password) < 7:
        return jsonify({"message": "Password must be at least 7 characters!"}), 400
    if new_password != con_password:
        return jsonify({"message": "Passwords don't match!"}), 400
    if not new_password.isalnum():
        return jsonify({"message": "Password must be alphanumeric!"}), 400

    new_password = generate_password_hash(new_password)

    get_admin.password = new_password

    new_notif = Notifications(message=f"Admin, {get_admin.first_name} {get_admin.last_name} changed password.")

    message_header = "Password Changed"
    message = f"Hello {get_admin.first_name}, you have successfully changed your password!"

    Queries.send_email(get_admin.email, message, message_header)

    db_session.add(new_notif)
    db_session.commit()

    return jsonify({"message": "Password updated!"}), 200


@admin.delete('delete')
@jwt_required()
def delete_admin():
    cur_admin = get_jwt_identity()
    get_admin = Queries.filter_one(Admin, Admin.id, cur_admin)

    new_notif = Notifications(message=f"Admin, {get_admin.first_name} {get_admin.last_name} deleted account.")

    message_header = "Account Deleted"
    message = f"Hello {get_admin.first_name}, you have successfully deleted your account!"

    Queries.send_email(get_admin.email, message, message_header)

    db_session.add(new_notif)
    db_session.delete(get_admin)
    db_session.commit()

    return jsonify({"message": "Admin deleted!"}), 200


@admin.put('logout')
@jwt_required()
def logout():
    cur_admin = get_jwt_identity()
    get_admin = Queries.filter_one(Admin, Admin.id, cur_admin)

    get_admin.logged_in = False

    new_notif = Notifications(message=f"Admin, {get_admin.first_name} {get_admin.last_name} logged out.")

    db_session.add(new_notif)
    db_session.commit()

    return jsonify({"message": "Password updated!"}), 200


@admin.get('notifications/<page_size>/<page>')
@jwt_required()
def get_notifications(page, page_size):
    notifications = Queries.get_all(Notifications)

    for notification in notifications:
        notification.new = False

    db_session.commit()

    notifications = notifications_schema.dump(notifications)

    items = Queries.paginate(int(page), int(page_size), notifications)

    return jsonify(items), 200


@admin.get('notifications')
@jwt_required()
def new_notifications():
    notifications = Queries.get_all(Notifications)

    num = 0

    for notification in notifications:
        if notification.new:
            num += 1

    return jsonify({"num": num}), 200


@admin.get('/username')
@jwt_required()
def get_username():
    cur_admin = get_jwt_identity()
    get_admin = Queries.filter_one(Admin, Admin.id, cur_admin)

    return jsonify(get_admin.first_name), 200
