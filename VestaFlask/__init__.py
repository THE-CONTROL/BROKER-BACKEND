import os
from flask import Flask
from VestaFlask.Data.db import db_session, init_db
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='work',
        DATABASE=os.path.join(app.instance_path, 'VestaFlask.sqlite'),
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=1),
        JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=900)
    )
    JWTManager(app)
    CORS(app)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from VestaFlask.Transactions import withdrawal, earning, deficits, deposit
    from VestaFlask.People import client, admin, auth

    app.register_blueprint(auth.auth)
    app.register_blueprint(admin.admin)
    app.register_blueprint(client.client)
    app.register_blueprint(deposit.deposit)
    app.register_blueprint(withdrawal.withdrawal)
    app.register_blueprint(earning.earning)
    app.register_blueprint(deficits.deficit)

    init_db()

    return app
