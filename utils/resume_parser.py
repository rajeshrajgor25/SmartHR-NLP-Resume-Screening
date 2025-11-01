import os
import re
import pdfplumber
import docx2txt

def extract_text_from_pdf(path):
    text_chunks = []
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text_chunks.append(t)
    except Exception as e:
        print('PDF read error:', e)
    return ' '.join(text_chunks)

def extract_text_from_docx(path):
    try:
        return docx2txt.process(path)
    except Exception as e:
        print('DOCX read error:', e)
        return ''

def extract_text_from_file(path):
    if not path or not os.path.exists(path):
        return ''
    if path.lower().endswith('.pdf'):
        return extract_text_from_pdf(path)
    elif path.lower().endswith(('.docx', '.doc')):
        return extract_text_from_docx(path)
    else:
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception:
            return ''

def extract_contact_email(text):
    m = re.search(r'([\w\.-]+@[\w\.-]+)', text)
    return m.group(1) if m else ''

def extract_experience_years(text):
    m = re.search(r'(\d+\+?)\s+years?', text.lower())
    if m:
        try:
            return int(re.sub('\D', '', m.group(1)))
        except Exception:
            return 0
    return 0
