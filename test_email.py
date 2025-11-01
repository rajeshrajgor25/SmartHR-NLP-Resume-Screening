import smtplib
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "yourmail@gmail.com"       
SMTP_PASSWORD = "yourapppassword"       

def send_test_email():
    msg = MIMEText("Hello Rajesh, your SmartHR email system is working perfectly ✅")
    msg["Subject"] = "SmartHR Test Email"
    msg["From"] = SMTP_USER
    msg["To"] = SMTP_USER  

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        print("✅ Test email sent successfully!")

if __name__ == "__main__":
    send_test_email()
