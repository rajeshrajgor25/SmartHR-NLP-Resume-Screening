import os
import re
from imapclient import IMAPClient
from email import policy
from email.parser import BytesParser
from config import IMAP_HOST, IMAP_USER, IMAP_PASSWORD, MAIL_FOLDER, RESUMES_DIR

os.makedirs(RESUMES_DIR, exist_ok=True)


def save_attachment(payload_bytes, filename):
    """Save the attachment to the resumes directory."""
    filename = filename.replace(' ', '_')
    path = os.path.join(RESUMES_DIR, filename)
    with open(path, 'wb') as f:
        f.write(payload_bytes)
    return path


def parse_email_address(from_header):
    """Extract clean email address from From header."""
    m = re.search(r'([\w\.-]+@[\w\.-]+)', from_header)
    return m.group(1) if m else from_header


def is_valid_resume_file(filename):
    """Allow only PDF or DOCX files (resume attachments)."""
    if not filename:
        return False
    return filename.lower().endswith(('.pdf', '.docx'))


def is_spam_sender(sender):
    """Filter out common spam or marketing senders."""
    spam_keywords = ["no-reply", "newsletter", "marketing", "promo", "update", "notification"]
    return any(k in sender.lower() for k in spam_keywords)


def fetch_emails():
    """Fetch only unread candidate-related emails with resume attachments."""
    results = []
    print("📨 Connecting to IMAP (fetching unread mails)...")

    with IMAPClient(IMAP_HOST) as client:
        client.login(IMAP_USER, IMAP_PASSWORD)
        client.select_folder(MAIL_FOLDER)

        messages = client.search(['UNSEEN'])
        print(f"Found {len(messages)} unread messages")

        if not messages:
            return results

        fetch_data = client.fetch(messages, ['RFC822'])
        for uid, md in fetch_data.items():
            raw = md[b'RFC822']
            msg = BytesParser(policy=policy.default).parsebytes(raw)

            subject = msg.get('subject', '')
            from_hdr = msg.get('from', '')
            date = msg.get('date', '')
            sender_email = parse_email_address(str(from_hdr))

            if is_spam_sender(sender_email):
                print(f"⚠️ Skipping spam or newsletter email from: {sender_email}")
                continue

            body = ''
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == 'text/plain' and part.get_content_disposition() is None:
                        try:
                            body += part.get_content()
                        except Exception:
                            pass
            else:
                if msg.get_content_type() == 'text/plain':
                    try:
                        body = msg.get_content()
                    except Exception:
                        body = ''

            attachments = []
            for part in msg.iter_attachments():
                filename = part.get_filename()
                if not filename or not is_valid_resume_file(filename):
                    continue  

                payload = part.get_payload(decode=True)
                path = save_attachment(payload, filename)
                attachments.append(path)
                print(f"📎 Saved resume: {filename} from {sender_email}")

            if not attachments:
                print(f"⚠️ Skipping email (no valid resume): {sender_email}")
                continue

            results.append({
                'uid': uid,
                'subject': subject,
                'from': sender_email,
                'raw_from': str(from_hdr),
                'date': date,
                'body': body,
                'attachments': attachments
            })

            client.add_flags(uid, [b'\\Seen'])

    return results
