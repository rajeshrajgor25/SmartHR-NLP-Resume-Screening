import smtplib
from email.message import EmailMessage
from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SENDER_REJECTION

def send_rejection_email(to_email, candidate_name, job_title='the position'):
    """Send polite rejection email to non-selected candidates"""
    if not to_email:
        print('⚠️ No recipient email found, skipping rejection mail')
        return

    msg = EmailMessage()
    msg['Subject'] = f'Application Update - {job_title}'
    msg['From'] = SENDER_REJECTION
    msg['To'] = to_email
    body = (f"Dear {candidate_name or 'Candidate'},\n\n"
            "Thank you for your interest in joining our team.\n"
            f"After reviewing your application for {job_title}, we found that your profile does not fully match our current requirements.\n\n"
            "We truly appreciate your time and encourage you to apply for future openings.\n\n"
            "Best wishes,\nHR Team")
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.send_message(msg)
        print(f'📩 Sent rejection email to {to_email}')
    except Exception as e:
        print(f'❌ Failed to send mail to {to_email}: {e}')


def send_shortlist_email(to_email, candidate_name, job_title='the position'):
    """Send congratulatory email to shortlisted candidates"""
    if not to_email:
        print('⚠️ No recipient email found, skipping shortlist mail')
        return

    msg = EmailMessage()
    msg['Subject'] = f'🎉 Congratulations - Shortlisted for {job_title}'
    msg['From'] = SENDER_REJECTION
    msg['To'] = to_email
    body = (f"Dear {candidate_name or 'Candidate'},\n\n"
            "Congratulations! 🎊\n\n"
            f"You have been shortlisted for {job_title}. Our HR team will reach out soon with further details about the next interview round.\n\n"
            "We’re excited to learn more about you!\n\n"
            "Best regards,\nHR Team")
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.send_message(msg)
        print(f'📩 Sent shortlist email to {to_email}')
    except Exception as e:
        print(f'❌ Failed to send mail to {to_email}: {e}')
