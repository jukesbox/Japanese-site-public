""" Japanese Flask Application - sending_emails.py

This file is used to send emails to the users.

This script is imported by main_app.py when the main program is run.

The packages that should be installed to be able to run this file are:
smtplib, ssl
"""


import smtplib, ssl


def send_pin(pin, email_address):
    """
    Sends the OTP email to the user so that they can log in using it.

    Parameters
    ----------
    pin: str
        The single-use PIN
    email_address: str
        The email address that the email would be sent to.
    """
    # the email_address parameter would be used to send to the user's actual email address... however
    # to simulate this, there is my own hardcoded email address that will have all PINs sent to it.
    port = 465
    smtp_serv = "smtp.gmail.com"
    sender = "" # The email to be shown as the sender
    receiver = "" # The email that the emails should be sent to
    password = "" # passwd
    message = "Subject: Your Single login PIN!\n\nYour single " \
              "login PIN is: " + str(pin) + " ... you can only use this to sign in once!"

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_serv, port, context=context) as serv:
        serv.login(sender, password)
        serv.sendmail(sender, receiver, message)


def send_reminders(email_addresses):
    """
    Sends an email to users that are going to lose their streak to remind them to practice.

    Parameters
    ----------
    email_addresses: list
        The list of email addresses to send the email to

    Returns
    -------
    None
    """
    # the email_address parameter would be used to send to the user's actual email address... however
    # to simulate this, there is my own hardcoded email address that will have all PINs sent to it.
    port = 465
    smtp_serv = "smtp.gmail.com"
    sender = "" # sender
    receiver = "" # receiver
    password = input("Type your password: ")
    message = "Subject: Remember to practice!\n\nIf you don't practice by the end of the day, you'll lose" \
              " your streak!"

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_serv, port, context=context) as serv:
        serv.login(sender, password)
        # here I would loop over the list of emails to change the receiver each time - sending the email
        # to all of the relevant users.
        serv.sendmail(sender, receiver, message)
