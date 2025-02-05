import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(sender_email, sender_password, recipient_email, subject, body):

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)

        server.sendmail(sender_email, recipient_email, msg.as_string())
        print(f"Email sent to {recipient_email} successfully")

    except Exception as e:
        print(f"Failed to send email. Error: {e}")
    finally:
        server.quit()


"""
SENDER_EMAIL = "irescueresale@gmail.com"
SENDER_PASSWORD = "dsbo ncmg tgkm cigk"
RECIPIENT_EMAIL = "gilbertenos770@yahoo.com"
SUBJECT = "🤝 TEST MESSAGE"
BODY = "test message"

"""

#koda = dsbo ncmg tgkm cigk
#gil = xnub igvz sgfo ibem

#send_email(SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, SUBJECT, BODY)


                    