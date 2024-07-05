import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from email_data import ConnectionData


def send_email_(subject, body, to_email, from_email, smtp_server, smtp_port, smtp_user, smtp_password):
    # Create message container
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    # Create the body of the message (HTML version).
    html = body
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    msg.attach(part2)

    # Send the message via local SMTP server.
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(from_email, to_email, msg.as_string())

def send_email(subject, body, to_email, from_email, connection_data: ConnectionData):
    # Create message container
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    # Create the body of the message (HTML version).
    html = body
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    msg.attach(part2)

    # Send the message via local SMTP server.
    with smtplib.SMTP(connection_data.smtp_server, connection_data.smtp_port) as server:
        server.starttls()
        server.login(connection_data.smtp_user, connection_data.smtp_password)
        server.sendmail(from_email, to_email, msg.as_string())

if __name__ == "__main__":

    send_email(
        subject="Test Email",
        body="<html><body><h1>Hello, World!</h1></body></html>",
        to_email="recipient@example.com",
        from_email="your_email@example.com",
        smtp_server="smtp.example.com",
        smtp_port=465,
        smtp_user="your_email@example.com",
        smtp_password="your_password"
    )