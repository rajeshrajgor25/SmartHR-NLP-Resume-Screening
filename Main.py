import os
import re
import pandas as pd
from utils.email_reader import fetch_emails
from utils.resume_parser import extract_text_from_file, extract_contact_email, extract_experience_years
from utils.nlp_similarity import compute_similarity, extract_skills
from utils.excel_writer import save_to_excel
from utils.auto_mailer import send_rejection_email, send_shortlist_email
from config import SIMILARITY_THRESHOLD, OUTPUT_EXCEL

HR_EMAIL = "rajeshrajgor00@gmail.com"

def load_job_descriptions(path='job_descriptions.txt'):
    """Load job descriptions separated by ---"""
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    return [p.strip() for p in raw.split('---') if p.strip()]

def extract_required_skills(jd_text):
    """Extract required skills from JD text (based on COMMON_SKILLS list)"""
    from utils.nlp_similarity import COMMON_SKILLS
    jd_lower = jd_text.lower()
    return [s for s in COMMON_SKILLS if s in jd_lower]


def extract_required_experience(jd_text):
    """
    Extract required years of experience from JD text.
    Example matched: "1-3 years", "2 yrs", "3 years", "1 to 4 years"
    """
    exp_pattern = re.search(r'(\d+)\s*[-toand]*\s*(\d*)\s*(?:year|yrs)', jd_text.lower())
    if exp_pattern:
        min_exp = int(exp_pattern.group(1))
        max_exp = int(exp_pattern.group(2)) if exp_pattern.group(2) else min_exp
        return min_exp, max_exp
    return None, None

def pick_best_jd_match(jds, candidate_text):
    """Find the best matching JD for a candidate resume"""
    best_score = 0.0
    best_jd = ''
    for jd in jds:
        score = compute_similarity(jd, candidate_text)
        if score > best_score:
            best_score = score
            best_jd = jd
    return best_jd, best_score

def is_candidate_email(mail):
    """Check if the mail is from a real candidate"""
    sender = mail.get('from', '').lower()
    subj = mail.get('subject', '').lower()
    body = mail.get('body', '').lower()
    attachments = mail.get('attachments', [])

    if sender == HR_EMAIL.lower() or "no-reply" in sender or "notification" in sender:
        return False

    if not attachments:
        return False

    if not any(a.lower().endswith(('.pdf', '.docx')) for a in attachments):
        return False

    if not re.search(r"(resume|cv|application|candidate|job|profile)", subj + " " + body, re.I):
        return False

    return True

if __name__ == '__main__':
    print('Loading job descriptions...')
    jds = load_job_descriptions()
    if not jds:
        print(' No job descriptions found.')
        exit(1)

    print(' Fetching unread candidate emails...')
    emails = fetch_emails(only_unread=True)
    print(f' Processing {len(emails)} unread emails...')

    shortlisted = []
    rejected = []

    for mail in emails:

        if not is_candidate_email(mail):
            print(f" Skipping non-candidate email from {mail.get('from')}")
            continue

        subj = mail.get('subject', '')
        body = mail.get('body', '')
        attachments = mail.get('attachments', [])

        resume_path = attachments[0] if attachments else ''
        resume_text = extract_text_from_file(resume_path)
        candidate_text = (body + '\n' + resume_text).strip()

        best_jd, best_score = pick_best_jd_match(jds, candidate_text)

        required_skills = extract_required_skills(best_jd)
        candidate_skills = extract_skills(candidate_text)

        contact_email = extract_contact_email(candidate_text) or mail.get('from')
        exp_years = extract_experience_years(candidate_text)
        min_exp, max_exp = extract_required_experience(best_jd)

        match_count = len([s for s in required_skills if s in candidate_skills])
        total_required = len(required_skills)

        exp_okay = False
        if min_exp is None and max_exp is None:
            exp_okay = True  
        elif exp_years >= min_exp and (max_exp == 0 or exp_years <= max_exp):
            exp_okay = True
        elif exp_years > 3 and (min_exp <= 3):
            exp_okay = True

        shortlisted_flag = (
            exp_okay and
            ((total_required > 0 and match_count >= total_required - 1) or (best_score >= 0.60))
        )

        candidate = {
            'email': contact_email,
            'subject': subj,
            'skills': ', '.join(candidate_skills),
            'experience_years': exp_years,
            'resume': resume_path,
            'best_jd': (best_jd[:100] + '...'),
            'similarity': round(best_score * 100, 2),
            'matched_skills': match_count,
            'required_skills': total_required,
            'shortlisted': shortlisted_flag
        }

        if shortlisted_flag:
            shortlisted.append(candidate)
            send_shortlist_email(contact_email, 'Candidate', 'the applied position')
        else:
            rejected.append(candidate)
            send_rejection_email(contact_email, 'Candidate', 'the applied position')

        print(
            f"{contact_email} | JD Match: {candidate['similarity']}% | "
            f"Skills: {match_count}/{total_required} | Exp: {exp_years} yrs | "
            f"Shortlisted: {shortlisted_flag}"
        )

    # Save results
    if shortlisted:
        save_to_excel(pd.DataFrame(shortlisted), OUTPUT_EXCEL)
        print(f' Shortlisted candidates saved to {OUTPUT_EXCEL}')
    else:
        print(' No candidates shortlisted.')

    if rejected:
        save_to_excel(pd.DataFrame(rejected), "rejected_candidates.xlsx")
        print(' Rejected candidates saved to rejected_candidates.xlsx')

    print('\n Screening complete!')
