from secrets import token_urlsafe
from math import ceil
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from cloudinary.uploader import upload
import cloudinary.api

cloudinary.config(
  cloud_name="de49puo0s",
  api_key="282637876839251",
  api_secret="J8d0CPLJ4b6f_4uAtjgMVe4hEI0",
  api_proxy="http://proxy.server:3128",
  secure=True
)


class Queries:

    @staticmethod
    def get_all(model):
        return model.query.all()

    @staticmethod
    def filter_one(model, value, checker):
        return model.query.filter(value == checker).first()

    @staticmethod
    def generate():
        return token_urlsafe(10)

    @staticmethod
    def paginate(page, page_size, items):
        items.reverse()
        page = int(page)
        page_size = page_size
        start = (page - 1) * page_size
        if len(items) > start + page_size:
            end = start + page_size
        else:
            end = len(items)
        pages = ceil((len(items) / page_size))
        if page - 1 > 0:
            prev_page = page - 1
        else:
            prev_page = None
        if page + 1 > pages:
            next_page = None
        else:
            next_page = page + 1

        meta = {"page": page, "next_page": next_page, "prev_page": prev_page, "pages": list((range(1, pages+1))),
                "num_items": len(items), "first_item": start+1, "last_item": end}

        new_items = items[start:end]

        info = {"meta": meta, "items": new_items}

        return info

    @staticmethod
    def send_email(receiver_email, send_message, message_header):
        port = 465
        password = "grcvnnwmcpdftfto"
        sender_email = "Vestaatrading@gmail.com"

        message = MIMEMultipart("alternative")
        message["Subject"] = message_header
        message["From"] = sender_email
        message["To"] = receiver_email

        plain_message = f"""\
Subject: {message_header}

{send_message}."""

        part1 = MIMEText(plain_message, "plain")
        part2 = MIMEText(send_message, "html")

        message.attach(part1)
        message.attach(part2)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )

    @staticmethod
    def cloud_upload(picture):
        upload_result = cloudinary.uploader.upload(picture)
        upload_result = upload_result["secure_url"]
        return upload_result

    @staticmethod
    def sf(val):
        formatted_string = "{:.5f}".format(val)
        float_value = float(formatted_string)
        return float_value
