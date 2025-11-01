import smtplib
from email.message import EmailMessage
from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SENDER_REJECTION

def send_rejection_email(to_email, candidate_name, job_title='the position'):
    if not to_email:
        print('No recipient email found, skipping rejection mail')
        return
    msg = EmailMessage()
    msg['Subject'] = f'Application Update - {job_title}'
    msg['From'] = SENDER_REJECTION
    msg['To'] = to_email
    body = (f"Dear {candidate_name or 'Candidate'},\n\n"
            "Thank you for applying. We appreciate your interest, "
            "but we will not be moving forward with your application at this time.\n\n"
            "Best wishes,\nHR Team")
    msg.set_content(body)
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.send_message(msg)
        print(f'Sent rejection to {to_email}')
    except Exception as e:
        print('Failed to send mail:', e)
