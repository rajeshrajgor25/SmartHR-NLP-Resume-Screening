import os
from utils.email_reader import fetch_emails
from utils.resume_parser import extract_text_from_file, extract_contact_email, extract_experience_years
from utils.nlp_similarity import compute_similarity, extract_skills
from utils.excel_writer import save_to_excel
from utils.auto_mailer import send_rejection_email
from config import SIMILARITY_THRESHOLD, OUTPUT_EXCEL

def load_job_descriptions(path='job_descriptions.txt'):
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    parts = [p.strip() for p in raw.split('---') if p.strip()]
    return parts

def pick_best_jd_match(jds, candidate_text):
    best_score = 0.0
    best_jd = ''
    for jd in jds:
        score = compute_similarity(jd, candidate_text)
        if score > best_score:
            best_score = score
            best_jd = jd
    return best_jd, best_score

if __name__ == '__main__':
    print('Loading job descriptions...')
    jds = load_job_descriptions()
    if not jds:
        print('No job descriptions found.')
        exit(1)

    print('Fetching candidate emails...')
    emails = fetch_emails()
    print(f'Processing {len(emails)} emails...')

    shortlisted = []

    for mail in emails:
        subj = mail.get('subject', '')
        body = mail.get('body', '')
        attachments = mail.get('attachments', [])

        if not any(k in (subj + ' ' + body).lower() for k in ['resume','cv','application','candidate']):
            continue

        resume_path = attachments[0] if attachments else ''
        resume_text = extract_text_from_file(resume_path) if resume_path else ''
        candidate_text = (body + '\n' + resume_text).strip()
        if not candidate_text:
            continue

        best_jd, best_score = pick_best_jd_match(jds, candidate_text)
        skills = extract_skills(candidate_text)
        contact_email = extract_contact_email(candidate_text) or mail.get('from')
        exp_years = extract_experience_years(candidate_text)

        candidate = {
            'email': contact_email,
            'subject': subj,
            'skills': ', '.join(skills),
            'experience_years': exp_years,
            'resume': resume_path or '',
            'best_jd': (best_jd[:100] + '...') if best_jd else '',
            'similarity': round(best_score * 100, 2),
            'shortlisted': best_score >= SIMILARITY_THRESHOLD
        }

        if candidate['shortlisted']:
            shortlisted.append(candidate)
        else:
            # send_rejection_email(candidate['email'], 'Candidate', 'Position')  # Optional
            pass

        print(f"{candidate['email']} | Match: {candidate['similarity']}% | Shortlisted: {candidate['shortlisted']}")

    if shortlisted:
        import pandas as pd
        df = pd.DataFrame(shortlisted)
        save_to_excel(df, OUTPUT_EXCEL)
    else:
        print('No candidates shortlisted.')

    print('✅ Process complete!')
