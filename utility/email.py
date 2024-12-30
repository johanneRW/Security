from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import settings
from bottle import template

def send_email(to_email, subject, template_name, **template_vars):
    try:
        # Create the email message
        message = MIMEMultipart()
        message["To"] = to_email
        message["From"] = settings.DEFAULT_EMAIL
        message["Subject"] = subject

        # Render the email body from template
        email_body = template("emails/" + template_name + ".html", **template_vars)
        message_text = MIMEText(email_body, 'html')
        message.attach(message_text)

        # Email credentials
        email = settings.DEFAULT_EMAIL
        password = settings.EMAIL_PASSWORD

        # Send the email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(email, password)
        server.sendmail(email, to_email, message.as_string())
        server.quit()

        return "Email sent successfully."
    
    except Exception as e:
        return f"Error sending email: {str(e)}"
