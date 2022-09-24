from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from VestaFlask.Data.db import Base
from datetime import datetime, timedelta
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import relationship

ma = Marshmallow()


class Admin(Base):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(120), unique=True)
    phone_no = Column(String(120))
    picture = Column(Text,
                     default="https://res.cloudinary.com/de49puo0s/image/upload/v1663949544/wjmrngpjhbgrwdhdihok.png")
    password = Column(Text)
    date_created = Column(String, default=datetime.now().strftime("%d/%m/%Y"))
    logged_in = Column(Boolean, default=False)
    acct_bal = Column(Integer, default=0)
    bit_bal = Column(Integer, default=0)
    profit = Column(Integer, default=0)
    loss = Column(Integer, default=0)
    tot_in = Column(Integer, default=0)
    tot_out = Column(Integer, default=0)

    def __init__(self, first_name, last_name, email, phone_no, password, acct_bal, bit_bal, tot_in, tot_out, profit,
                 loss):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_no = phone_no
        self.password = password
        self.acct_bal = acct_bal
        self.bit_bal = bit_bal
        self.tot_in = tot_in
        self.tot_out = tot_out
        self.profit = profit
        self.loss = loss

    def __repr__(self):
        return f'<Admin {self.first_name!r} {self.last_name!r}>'


class AdminSchema(ma.Schema):
    class Meta:
        fields = ("id", "first_name", "last_name", "email", "phone_no", "picture", "password", "logged_in",
                  "date_created", "acct_bal", "bit_bal", "tot_in", "tot_out", "profit", "loss")


admin_schema = AdminSchema()
admins_schema = AdminSchema(many=True)


class Client(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(120), unique=True)
    phone_no = Column(String(120))
    picture = Column(Text,
                     default="https://res.cloudinary.com/de49puo0s/image/upload/v1663949544/wjmrngpjhbgrwdhdihok.png")
    country = Column(String(50))
    state = Column(String(50))
    city = Column(String(50))
    zip_code = Column(String(50))
    address = Column(String(1000))
    annual_income = Column(String(50))
    investment_plan = Column(String(50))
    profession = Column(String(50))
    password = Column(Text)
    date_created = Column(String, default=datetime.now().strftime("%d/%m/%Y"))
    logged_in = Column(Boolean, default=False)
    deleted = Column(Boolean, default=False)
    deposits = relationship("Deposit", back_populates="client")
    withdrawals = relationship("Withdrawal", back_populates="client")
    earnings = relationship("Earning", back_populates="client")
    deficits = relationship("Deficit", back_populates="client")
    is_coin = Column(Boolean, default=False)
    coinbase_pass = Column(String(50))
    coinbase_key = Column(String(50))
    acct_bal = Column(Integer, default=0)
    bit_bal = Column(Integer, default=0)
    profit = Column(Integer, default=0)
    loss = Column(Integer, default=0)
    tot_in = Column(Integer, default=0)
    tot_re = Column(Integer, default=0)

    def __init__(self, first_name, last_name, email, phone_no, country, state, city, zip_code, address, annual_income,
                 investment_plan, profession, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_no = phone_no
        self.country = country
        self.state = state
        self.city = city
        self.zip_code = zip_code
        self.address = address
        self.annual_income = annual_income
        self.investment_plan = investment_plan
        self.profession = profession
        self.password = password

    def __repr__(self):
        return f'<Client {self.first_name!r} {self.last_name!r}>'


class ClientSchema(ma.Schema):
    class Meta:
        fields = ("id", "first_name", "last_name", "email", "phone_no", "picture", "country", "state", "city",
                  "zip_code", "address", "annual_income", "investment_plan", "profession", "password", "logged_in",
                  "deleted", "date_created", "coinbase_pass", "coinbase_key", "acct_bal", "bit_bal", "tot_in", "tot_re",
                  "profit", "loss")


client_schema = ClientSchema()
clients_schema = ClientSchema(many=True)


class Deposit(Base):
    __tablename__ = 'deposits'
    id = Column(Integer, primary_key=True)
    username = Column(String(100))
    amount = Column(String(100))
    bitcoin = Column(String(100))
    proof = Column(String(100),
                   default="https://res.cloudinary.com/de49puo0s/image/upload/v1663951059/cq7ajzupx0u1z01i9afd.jpg")
    status = Column(Boolean, default=False)
    date_created = Column(String, default=datetime.now().strftime("%d/%m/%Y"))
    client_id = Column(Integer, ForeignKey("clients.id"))
    client = relationship("Client", back_populates="deposits")

    def __init__(self, username, amount, bitcoin, client_id):
        self.username = username
        self.amount = amount
        self.bitcoin = bitcoin
        self.client_id = client_id

    def __repr__(self):
        return f'<Deposit {self.username!r} - {self.amount!r}>'


class DepositSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "amount", "bitcoin", "proof", "status", "date_created", "client_id")


deposit_schema = DepositSchema()
deposits_schema = DepositSchema(many=True)


class Withdrawal(Base):
    __tablename__ = 'withdrawals'
    id = Column(Integer, primary_key=True)
    username = Column(String(100))
    amount = Column(String(100))
    bitcoin = Column(String(100))
    wallet = Column(String(100))
    status = Column(Boolean, default=False)
    date_created = Column(String, default=datetime.now().strftime("%d/%m/%Y"))
    client_id = Column(Integer, ForeignKey("clients.id"))
    client = relationship("Client", back_populates="withdrawals")

    def __init__(self, username, amount, bitcoin, wallet, client_id):
        self.username = username
        self.amount = amount
        self.bitcoin = bitcoin
        self.client_id = client_id
        self.wallet = wallet

    def __repr__(self):
        return f'<Withdrawal {self.username!r} - {self.amount!r}>'


class WithdrawalSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "amount", "bitcoin", "wallet", "status", "date_created", "client_id")


withdrawal_schema = WithdrawalSchema()
withdrawals_schema = WithdrawalSchema(many=True)


class Earning(Base):
    __tablename__ = 'earnings'
    id = Column(Integer, primary_key=True)
    username = Column(String(100))
    amount = Column(String(100))
    bitcoin = Column(String(100))
    date_created = Column(String, default=datetime.now().strftime("%d/%m/%Y"))
    client_id = Column(Integer, ForeignKey("clients.id"))
    client = relationship("Client", back_populates="earnings")

    def __init__(self, username, amount, bitcoin, client_id):
        self.username = username
        self.amount = amount
        self.bitcoin = bitcoin
        self.client_id = client_id

    def __repr__(self):
        return f'<Earning {self.username!r} - {self.amount!r}>'


class EarningSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "amount", "bitcoin", "date_created", "client_id")


earning_schema = EarningSchema()
earnings_schema = EarningSchema(many=True)


class Deficit(Base):
    __tablename__ = 'deficits'
    id = Column(Integer, primary_key=True)
    username = Column(String(100))
    amount = Column(String(100))
    bitcoin = Column(String(100))
    date_created = Column(String, default=datetime.now().strftime("%d/%m/%Y"))
    client_id = Column(Integer, ForeignKey("clients.id"))
    client = relationship("Client", back_populates="deficits")

    def __init__(self, username, amount, bitcoin, client_id):
        self.username = username
        self.amount = amount
        self.bitcoin = bitcoin
        self.client_id = client_id

    def __repr__(self):
        return f'<Deficit {self.username!r} - {self.amount!r}>'


class DeficitSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "amount", "bitcoin", "date_created", "client_id")


deficit_schema = DeficitSchema()
deficits_schema = DeficitSchema(many=True)


class ResetPassword(Base):
    __tablename__ = "reset_password"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120))
    reset_code = Column(String(120), unique=True)
    status = Column(Boolean, default=False)
    expires_in = Column(DateTime, default=datetime.utcnow() + timedelta(minutes=5))
    date_created = Column(String, default=datetime.now().strftime("%d/%m/%Y"))

    def __init__(self, email, reset_code):
        self.email = email
        self.reset_code = reset_code

    def __repr__(self):
        return f'<Reset Password: {self.email!r} - {self.reset_code!r} - {self.status!r}>'


class ResetPasswordSchema(ma.Schema):
    class Meta:
        fields = ("id", "email", "reset_code", "status", "expires_in", "date_created")


reset_password_schema = ResetPasswordSchema()
reset_passwords_schema = ResetPasswordSchema(many=True)


class Notifications(Base):
    __tablename__ = "notification"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String(120))
    date_created = Column(String, default=datetime.now().strftime("%d/%m/%Y"))
    new = Column(Boolean, default=True)

    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return f'<Reset Password: {self.message!r} - {self.date_created!r}>'


class NotificationsSchema(ma.Schema):
    class Meta:
        fields = ("id", "message", "new", "date_created")


notification_schema = NotificationsSchema()
notifications_schema = NotificationsSchema(many=True)
