import os
from email.message import EmailMessage
import ssl
import smtplib

password = 'bnvt ztrw uhsp dfak'


def MailRep(file, doc_name, receiver):


    email_sender = 'nexsynchelpdesk@gmail.com'
    email_password = password

    email_receiver = receiver

    subject = "Prescription"

    body = f"""Dear Patient,\n\n{doc_name} has prescribed some medications and health routines for you.\nPrescription is attached below.\n\nBest wishes for a speedy recovery!,\nPrognosify Team"""

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['subject'] = subject
    em.set_content(body)
    context = ssl.create_default_context()
    with open(file, 'rb') as f:
        file_data = f.read()

    em.add_attachment(file_data, maintype='application', subtype = 'octet-stream', filename=file)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        try:
            smtp.sendmail(email_sender, email_receiver, em.as_string())
            return 1
        except Exception as e:
            return -1
