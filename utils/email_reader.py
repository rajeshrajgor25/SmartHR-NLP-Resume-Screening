import os
import re
from imapclient import IMAPClient
from email import policy
from email.parser import BytesParser
from config import IMAP_HOST, IMAP_USER, IMAP_PASSWORD, MAIL_FOLDER, SEARCH_CRITERIA, RESUMES_DIR

os.makedirs(RESUMES_DIR, exist_ok=True)

def save_attachment(payload_bytes, filename):
    filename = filename.replace(' ', '_')
    path = os.path.join(RESUMES_DIR, filename)
    with open(path, 'wb') as f:
        f.write(payload_bytes)
    return path

def parse_email_address(from_header):
    m = re.search(r'([\w\.-]+@[\w\.-]+)', from_header)
    return m.group(1) if m else from_header

def fetch_emails():
    results = []
    print('Connecting to IMAP...')
    with IMAPClient(IMAP_HOST) as client:
        client.login(IMAP_USER, IMAP_PASSWORD)
        client.select_folder(MAIL_FOLDER)
        messages = client.search(SEARCH_CRITERIA)
        print(f'Found {len(messages)} messages')
        if not messages:
            return results

        fetch_data = client.fetch(messages, ['RFC822'])
        for uid, md in fetch_data.items():
            raw = md[b'RFC822']
            msg = BytesParser(policy=policy.default).parsebytes(raw)
            subject = msg.get('subject', '')
            from_hdr = msg.get('from', '')
            date = msg.get('date', '')

            # Extract plain text body
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
                if not filename:
                    continue
                payload = part.get_payload(decode=True)
                path = save_attachment(payload, filename)
                attachments.append(path)

            results.append({
                'uid': uid,
                'subject': subject,
                'from': parse_email_address(str(from_hdr)),
                'raw_from': str(from_hdr),
                'date': date,
                'body': body,
                'attachments': attachments
            })
    return results
