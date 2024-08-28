import smtplib
import os

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders

def send_email(send_from, send_to, subject, message, files=None, server="smtp.zoho.com", port=465, username='', password='', isTls=True):
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Date'] = formatdate(localtime = True)
    msg['Subject'] = subject

    msg.attach(MIMEText(message))

    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(fil.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
            msg.attach(part)

    smtp = smtplib.SMTP_SSL(server, port)
    # if isTls:
    #     smtp.starttls()
    smtp.login(username,password)
    smtp.sendmail(send_from, [send_to], msg.as_string())
    smtp.quit()
