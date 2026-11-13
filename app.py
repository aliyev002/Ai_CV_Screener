import os
import io
import time
from pathlib import Path
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from parser import DocumentParser
from screener import CandidateScreener, CandidateEvaluation
from exporter import ResultExporter

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI CV Screener",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Multi-language dictionary
TRANSLATIONS = {
    "AZ": {
        "title": "AI CV Screening & Evaluation System",
        "subtitle": "Namizədlərin CV-lərini təhlil edin, tələblərə uyğunluq balını çıxarın və nəticələri ixrac edin.",
        "config_header": "Konfiqurasiya",
        "gemini_api_key": "Gemini API Açar:",
        "api_key_help": ".env faylından avtomatik oxunur.",
        "jd_header": "Vakansiya Tələbləri (JD)",
        "use_default_jd": "Hazır Şablon JD",
        "job_desc_label": "İş Təsviri:",
        "job_desc_placeholder": "Vakansiya tələblərini daxil edin...",
        "sheets_header": "Google Sheets Webhook",
        "webhook_url": "Webhook URL:",
        "upload_label": "Namizəd CV fayllarını seçin (PDF və ya DOCX formatında bir və ya bir neçə fayl yükləyə bilərsiniz):",
        "uploaded_notice": "Yüklənmiş fayllar ({count} ədəd):",
        "start_screening": "Təhlili Başlat",
        "screening_progress": "Təhlil edilir [{curr}/{total}]: {name}...",
        "screening_done": "Təhlil tamamlandı.",
        "screening_success": "{count} namizədin təhlili uğurla başa çatdı.",
        "api_key_missing": "Google Gemini API açarı daxil edilməyib.",
        "jd_missing": "Vakansiya mətni boş ola bilməz.",
        "error_prefix": "Xəta baş verdi:",
        "results_header": "Təhlil Nəticələri",
        "total_candidates": "Ümumi Namizəd",
        "strong_candidates": "Uyğun Namizədlər",
        "average_score": "Orta Bal",
        "top_score": "Ən Yüksək Bal",
        "ranking_table": "Reytinq Cədvəli",
        "detailed_profiles": "Ətraflı Namizəd Profilləri",
        "email": "Email:",
        "phone": "Telefon:",
        "not_specified": "Qeyd olunmayıb",
        "score_breakdown": "Bal Bölgüsü:",
        "tech_skills": "Texniki Bacarıq:",
        "experience": "İş Təcrübəsi:",
        "education": "Təhsil:",
        "cv_presentation": "CV Tərtibatı:",
        "summary": "Xülasə:",
        "matched_skills": "Uyğunlaşan Bacarıqlar:",
        "no_matched_skills": "Uyğun bacarıq tapılmadı",
        "missing_gaps": "Çatışmayan Tələblər:",
        "all_requirements_met": "Bütün tələblər mövcuddur",
        "key_strengths": "Əsas Üstünlüklər:",
        "interview_questions": "HR Müsahibə Sualları:",
        "export_header": "Nəticələri İxrac Et",
        "download_csv": "CSV Yüklə",
        "download_excel": "Excel Yüklə (.xlsx)",
        "send_to_sheets": "Google Sheets-ə Göndər",
        "sheets_success": "Məlumatlar Google Sheets-ə göndərildi.",
        "sheets_no_webhook": "Sol paneldə Google Sheets Webhook URL daxil edilməyib.",
        "sheets_401_error": "Google Sheets 401 Xətası: Apps Script-də 'Şu kullanıcı olarak çalıştır' hissəsi 'Ben' olmalı, 'Erişimi olanlar' isə mütləq 'Herkes' seçilməlidir."
    },
    "EN": {
        "title": "AI CV Screening & Evaluation System",
        "subtitle": "Analyze candidate CVs, calculate match scores against job requirements, and export results.",
        "config_header": "Configuration",
        "gemini_api_key": "Gemini API Key:",
        "api_key_help": "Automatically loaded from .env file.",
        "jd_header": "Job Description (JD)",
        "use_default_jd": "Use Default Template JD",
        "job_desc_label": "Job Description:",
        "job_desc_placeholder": "Enter target job requirements here...",
        "sheets_header": "Google Sheets Webhook",
        "webhook_url": "Webhook URL:",
        "upload_label": "Select candidate CV files (You can upload one or multiple PDF / DOCX files):",
        "uploaded_notice": "Uploaded files ({count} files):",
        "start_screening": "Start Screening",
        "screening_progress": "Screening [{curr}/{total}]: {name}...",
        "screening_done": "Screening completed.",
        "screening_success": "Successfully screened {count} candidate(s).",
        "api_key_missing": "Google Gemini API key is missing.",
        "jd_missing": "Job description cannot be empty.",
        "error_prefix": "An error occurred:",
        "results_header": "Screening Results",
        "total_candidates": "Total Candidates",
        "strong_candidates": "Strong Matches",
        "average_score": "Average Score",
        "top_score": "Top Score",
        "ranking_table": "Leaderboard Table",
        "detailed_profiles": "Detailed Candidate Profiles",
        "email": "Email:",
        "phone": "Phone:",
        "not_specified": "Not specified",
        "score_breakdown": "Score Breakdown:",
        "tech_skills": "Technical Skills:",
        "experience": "Work Experience:",
        "education": "Education:",
        "cv_presentation": "CV Presentation:",
        "summary": "Summary:",
        "matched_skills": "Matched Skills:",
        "no_matched_skills": "No matching skills found",
        "missing_gaps": "Missing Requirements:",
        "all_requirements_met": "All requirements met",
        "key_strengths": "Key Strengths:",
        "interview_questions": "HR Interview Questions:",
        "export_header": "Export Results",
        "download_csv": "Download CSV",
        "download_excel": "Download Excel (.xlsx)",
        "send_to_sheets": "Sync to Google Sheets",
        "sheets_success": "Data successfully synced to Google Sheets.",
        "sheets_no_webhook": "Google Sheets Webhook URL is missing in the sidebar.",
        "sheets_401_error": "Google Sheets 401 Error: In Apps Script, set 'Execute as' to 'Me' and 'Who has access' to 'Anyone'."
    }
}

# State management
if "evaluations" not in st.session_state:
    st.session_state.evaluations = []
if "lang" not in st.session_state:
    st.session_state.lang = "AZ"

T = TRANSLATIONS[st.session_state.lang]

# Ultra-safe Clean CSS (Native Theme Compliance)
st.markdown("""
<style>
    .stDeployButton, footer, [data-testid="stStatusWidget"], [data-testid="manage-app-button"] {
        display: none !important;
    }
    
    .app-header {
        border-bottom: 1px solid rgba(128, 128, 128, 0.2);
        padding-bottom: 0.8rem;
        margin-bottom: 1.25rem;
    }
    .app-title {
        font-size: 1.85rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin: 0;
    }
    .app-subtitle {
        font-size: 0.95rem;
        opacity: 0.75;
        margin-top: 0.3rem;
    }
    
    .metric-card {
        background: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 10px;
        padding: 1.15rem 1rem;
        text-align: center;
    }
    .metric-num {
        font-size: 1.85rem;
        font-weight: 700;
        margin-top: 0.2rem;
    }
    .metric-txt {
        font-size: 0.76rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        opacity: 0.7;
        font-weight: 600;
    }
    
    .status-badge {
        display: inline-block;
        padding: 4px 10px;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 6px;
        text-transform: uppercase;
    }
    .badge-strong {
        background-color: rgba(16, 185, 129, 0.18);
        color: #10b981 !important;
        border: 1px solid rgba(16, 185, 129, 0.35);
    }
    .badge-potential {
        background-color: rgba(245, 158, 11, 0.18);
        color: #f59e0b !important;
        border: 1px solid rgba(245, 158, 11, 0.35);
    }
    .badge-mismatch {
        background-color: rgba(239, 68, 68, 0.18);
        color: #ef4444 !important;
        border: 1px solid rgba(239, 68, 68, 0.35);
    }
    
    .pill {
        display: inline-block;
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 0.82rem;
        margin: 2px 4px 2px 0;
        font-weight: 500;
    }
    .pill-blue {
        background-color: rgba(37, 99, 235, 0.15) !important;
        color: #3b82f6 !important;
        border: 1px solid rgba(37, 99, 235, 0.3) !important;
    }
    .pill-red {
        background-color: rgba(239, 68, 68, 0.15) !important;
        color: #ef4444 !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

# Default Job Description
DEFAULT_JD_PATH = Path("sample_data/job_description.txt")
DEFAULT_JD = DEFAULT_JD_PATH.read_text(encoding="utf-8") if DEFAULT_JD_PATH.exists() else ""

# Sidebar Controls
with st.sidebar:
    chosen_lang = st.selectbox(
        "Dil / Language",
        options=["AZ", "EN"],
        index=0 if st.session_state.lang == "AZ" else 1,
    )
    if chosen_lang != st.session_state.lang:
        st.session_state.lang = chosen_lang
        st.rerun()

    st.markdown("---")
    st.markdown(f"### {T['config_header']}")
    
    env_key = os.getenv("GEMINI_API_KEY", "")
    api_key_input = st.text_input(
        T["gemini_api_key"],
        value=env_key,
        type="password",
        help=T["api_key_help"]
    )
    
    st.markdown("---")
    st.markdown(f"### {T['jd_header']}")
    use_default_jd = st.checkbox(T["use_default_jd"], value=True)
    if use_default_jd:
        job_desc = st.text_area(T["job_desc_label"], value=DEFAULT_JD, height=220)
    else:
        job_desc = st.text_area(T["job_desc_label"], height=220, placeholder=T["job_desc_placeholder"])
        
    st.markdown("---")
    st.markdown(f"### {T['sheets_header']}")
    webhook_url = st.text_input(
        T["webhook_url"],
        value=os.getenv("GOOGLE_SHEETS_WEBHOOK_URL", ""),
        placeholder="https://script.google.com/macros/s/.../exec"
    )

# Header
st.markdown(f"""
<div class="app-header">
    <h1 class="app-title">{T['title']}</h1>
    <div class="app-subtitle">{T['subtitle']}</div>
</div>
""", unsafe_allow_html=True)

# Upload Zone
uploaded_files = st.file_uploader(
    T["upload_label"],
    type=["pdf", "docx"],
    accept_multiple_files=True
)

if uploaded_files:
    notice_text = T["uploaded_notice"].format(count=len(uploaded_files))
    st.info(f"{notice_text} {', '.join([f.name for f in uploaded_files])}")
    
    col_run, _ = st.columns([1, 4])
    with col_run:
        start_button = st.button(T["start_screening"], type="primary", use_container_width=True)
        
    if start_button:
        active_key = api_key_input.strip() or os.getenv("GEMINI_API_KEY", "").strip()
        if not active_key:
            st.error(T["api_key_missing"])
        elif not job_desc.strip():
            st.error(T["jd_missing"])
        else:
            try:
                screener = CandidateScreener(api_key=active_key)
                evaluations = []
                pbar = st.progress(0)
                status_box = st.empty()
                
                total = len(uploaded_files)
                for idx, uf in enumerate(uploaded_files):
                    status_box.text(T["screening_progress"].format(curr=idx+1, total=total, name=uf.name))
                    file_bytes = uf.read()
                    text = DocumentParser.extract_text(file_bytes, uf.name)
                    # Pass selected language to the AI engine!
                    eval_res = screener.screen_candidate(text, job_desc, uf.name, language=st.session_state.lang)
                    evaluations.append(eval_res)
                    pbar.progress((idx + 1) / total)
                    time.sleep(0.3)
                    
                status_box.text(T["screening_done"])
                st.session_state.evaluations = evaluations
                st.rerun()
            except Exception as e:
                st.error(f"{T['error_prefix']} {e}")

# Display Results if evaluations exist
if st.session_state.evaluations:
    evals = st.session_state.evaluations
    df = ResultExporter.to_dataframe(evals)
    
    st.markdown("---")
    st.markdown(f"### {T['results_header']}")
    
    # KPI Metrics
    k1, k2, k3, k4 = st.columns(4)
    total_cand = len(evals)
    strong_cand = sum(1 for e in evals if e.recommendation == "Strong Match")
    avg_score = round(sum(e.overall_score for e in evals) / total_cand, 1) if total_cand else 0
    top_cand = max(evals, key=lambda x: x.overall_score).candidate_name if evals else "-"
    
    with k1:
        st.markdown(f"""<div class="metric-card"><div class="metric-txt">{T['total_candidates']}</div><div class="metric-num">{total_cand}</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="metric-card"><div class="metric-txt">{T['strong_candidates']}</div><div class="metric-num">{strong_cand}</div></div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="metric-card"><div class="metric-txt">{T['average_score']}</div><div class="metric-num">{avg_score} / 100</div></div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="metric-card"><div class="metric-txt">{T['top_score']}</div><div class="metric-num">{top_cand}</div></div>""", unsafe_allow_html=True)
        
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    # Summary Table
    st.markdown(f"#### {T['ranking_table']}")
    display_df = df[[
        "Candidate Name",
        "Overall Score",
        "Recommendation",
        "Technical Skills Score",
        "Experience Score",
        "Education Score",
        "Matched Skills"
    ]].copy()
    st.dataframe(display_df, use_container_width=True)
    
    # Detailed Cards
    st.markdown(f"#### {T['detailed_profiles']}")
    for ev in sorted(evals, key=lambda x: x.overall_score, reverse=True):
        b_class = "badge-strong" if ev.recommendation == "Strong Match" else ("badge-potential" if ev.recommendation == "Potential Match" else "badge-mismatch")
        
        with st.expander(f"{ev.candidate_name} — {ev.overall_score}/100 ({ev.recommendation})", expanded=(ev.overall_score >= 70)):
            col_l, col_r = st.columns([1, 2])
            with col_l:
                st.markdown(f"<span class='status-badge {b_class}'>{ev.recommendation} • {ev.overall_score} / 100</span>", unsafe_allow_html=True)
                st.markdown(f"**{T['email']}** {ev.candidate_email or T['not_specified']}")
                st.markdown(f"**{T['phone']}** {ev.candidate_phone or T['not_specified']}")
                st.markdown("<br/>", unsafe_allow_html=True)
                
                st.markdown(f"**{T['score_breakdown']}**")
                st.progress(ev.scores.technical_skills / 100, text=f"{T['tech_skills']} {ev.scores.technical_skills}%")
                st.progress(ev.scores.experience_relevance / 100, text=f"{T['experience']} {ev.scores.experience_relevance}%")
                st.progress(ev.scores.education_certifications / 100, text=f"{T['education']} {ev.scores.education_certifications}%")
                st.progress(ev.scores.presentation_structure / 100, text=f"{T['cv_presentation']} {ev.scores.presentation_structure}%")
                
            with col_r:
                st.markdown(f"**{T['summary']}** {ev.summary}")
                
                st.markdown(f"**{T['matched_skills']}**")
                matched_html = "".join([f"<span class='pill pill-blue'>{s}</span>" for s in ev.matched_skills]) or f"<span style='opacity:0.7; font-size:0.85rem;'>{T['no_matched_skills']}</span>"
                st.markdown(matched_html, unsafe_allow_html=True)
                
                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                st.markdown(f"**{T['missing_gaps']}**")
                missing_html = "".join([f"<span class='pill pill-red'>{s}</span>" for s in ev.missing_skills_or_gaps]) or f"<span style='opacity:0.7; font-size:0.85rem;'>{T['all_requirements_met']}</span>"
                st.markdown(missing_html, unsafe_allow_html=True)
                
                if ev.key_strengths:
                    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                    st.markdown(f"**{T['key_strengths']}**")
                    for s in ev.key_strengths:
                        st.markdown(f"• {s}")
                        
                if ev.suggested_interview_questions:
                    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                    st.markdown(f"**{T['interview_questions']}**")
                    for idx_q, q in enumerate(ev.suggested_interview_questions, 1):
                        st.markdown(f"**{idx_q}.** {q}")
                        
    # Export Area
    st.markdown("---")
    st.markdown(f"### {T['export_header']}")
    
    col_c, col_e, col_s = st.columns(3)
    with col_c:
        csv_bytes = ResultExporter.to_csv_bytes(df)
        st.download_button(T["download_csv"], data=csv_bytes, file_name="screening_results.csv", mime="text/csv", use_container_width=True)
    with col_e:
        excel_bytes = ResultExporter.to_excel_bytes(df)
        st.download_button(T["download_excel"], data=excel_bytes, file_name="screening_results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    with col_s:
        if st.button(T["send_to_sheets"], use_container_width=True):
            if not webhook_url:
                st.warning(T["sheets_no_webhook"])
            else:
                try:
                    res = ResultExporter.sync_to_google_sheets_webhook(evals, webhook_url)
                    if res["success"]:
                        st.success(T["sheets_success"])
                    elif res["status_code"] == 401:
                        st.error(T["sheets_401_error"])
                    else:
                        st.error(f"{T['error_prefix']} Status {res['status_code']}. {res['response_text']}")
                except Exception as ex:
                    st.error(f"{T['error_prefix']} {ex}")
