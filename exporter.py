import io
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
import requests
from screener import CandidateEvaluation

class ResultExporter:

    @staticmethod
    def to_dataframe(evaluations: List[CandidateEvaluation]) -> pd.DataFrame:
        rows = []
        for ev in evaluations:
            rows.append({
                "Candidate Name": ev.candidate_name,
                "Email": ev.candidate_email or "N/A",
                "Phone": ev.candidate_phone or "N/A",
                "Overall Score": ev.overall_score,
                "Overall Score (0-100)": ev.overall_score,
                "Recommendation": ev.recommendation,
                "Technical Skills Score": ev.scores.technical_skills,
                "Tech Skills Score (40%)": ev.scores.technical_skills,
                "Experience Score": ev.scores.experience_relevance,
                "Experience Score (30%)": ev.scores.experience_relevance,
                "Education Score": ev.scores.education_certifications,
                "Education Score (15%)": ev.scores.education_certifications,
                "Presentation Score": ev.scores.presentation_structure,
                "Presentation Score (15%)": ev.scores.presentation_structure,
                "Matched Skills": ", ".join(ev.matched_skills),
                "Missing Skills": ", ".join(ev.missing_skills_or_gaps),
                "Missing Skills / Gaps": ", ".join(ev.missing_skills_or_gaps),
                "Key Strengths": " | ".join(ev.key_strengths),
                "Concerns": " | ".join(ev.concerns_or_red_flags),
                "Suggested Questions": " \n ".join([f"{i+1}. {q}" for i, q in enumerate(ev.suggested_interview_questions)]),
                "Executive Summary": ev.summary,
                "Screened At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
        df = pd.DataFrame(rows)
        if not df.empty and "Overall Score" in df.columns:
            df = df.sort_values(by="Overall Score", ascending=False)
        return df

    @staticmethod
    def to_csv_bytes(df: pd.DataFrame) -> bytes:
        return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

    @staticmethod
    def to_excel_bytes(df: pd.DataFrame) -> bytes:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Evaluations", index=False)
        output.seek(0)
        return output.getvalue()

    @staticmethod
    def sync_to_google_sheets_webhook(
        evaluations: List[CandidateEvaluation],
        webhook_url: str
    ) -> Dict[str, Any]:
        if not webhook_url or not webhook_url.startswith("http"):
            raise ValueError("Invalid Google Sheets Webhook URL.")

        payload = {
            "timestamp": datetime.now().isoformat(),
            "total_candidates": len(evaluations),
            "candidates": [
                {
                    "name": ev.candidate_name,
                    "email": ev.candidate_email or "",
                    "phone": ev.candidate_phone or "",
                    "overall_score": ev.overall_score,
                    "recommendation": ev.recommendation,
                    "tech_score": ev.scores.technical_skills,
                    "exp_score": ev.scores.experience_relevance,
                    "edu_score": ev.scores.education_certifications,
                    "pres_score": ev.scores.presentation_structure,
                    "matched_skills": ", ".join(ev.matched_skills),
                    "missing_skills": ", ".join(ev.missing_skills_or_gaps),
                    "summary": ev.summary,
                    "questions": " | ".join(ev.suggested_interview_questions)
                }
                for ev in evaluations
            ]
        }

        response = requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            allow_redirects=True,
            timeout=20
        )

        return {
            "status_code": response.status_code,
            "success": response.status_code in [200, 201, 302],
            "response_text": response.text[:200]
        }
