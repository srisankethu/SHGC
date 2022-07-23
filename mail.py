from threading import Thread
from flask import current_app
from flask_mail import Message

def send_async_mail(app, mail, msg):

    with app.app_context():
        mail.send(msg)

def send_mail(app, mail, to, subject, message):

    msg = Message(subject+":",
                  sender = "iamjustice443@gmail.com",
                  recipients = [to])
    msg.body = message
    thread = Thread(target=send_async_mail, args=[app, mail, msg])
    thread.start()
    return thread

def send_bug_report(app, mail, error_area, error_message):

    send_mail(app, mail, "iamjustice443@gmail.com", "SHGC Bug Report",
              "Bug found at:" + error_area + "\n" + error_message)
