import os
import json
from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class ScoreBreakdown(BaseModel):
    technical_skills: int = Field(description="Score 0-100 evaluating match of required programming languages, tools, frameworks, and skills.")
    experience_relevance: int = Field(description="Score 0-100 evaluating depth and relevance of past work experience.")
    education_certifications: int = Field(description="Score 0-100 evaluating degree, certifications, or educational credentials.")
    presentation_structure: int = Field(description="Score 0-100 evaluating clarity, organization, and completeness of CV.")

class CandidateEvaluation(BaseModel):
    candidate_name: str = Field(description="Full name of candidate.")
    candidate_email: Optional[str] = Field(default=None, description="Email address.")
    candidate_phone: Optional[str] = Field(default=None, description="Phone number.")
    overall_score: int = Field(description="Calculated weighted total score 0-100.")
    recommendation: Literal["Strong Match", "Potential Match", "Not a Match"] = Field(description="Recommendation bucket.")
    summary: str = Field(description="Executive summary in target language.")
    scores: ScoreBreakdown = Field(description="Score breakdown.")
    matched_skills: List[str] = Field(description="Matched skills list in target language.")
    missing_skills_or_gaps: List[str] = Field(description="Missing requirements list in target language.")
    key_strengths: List[str] = Field(description="Key strengths list in target language.")
    concerns_or_red_flags: List[str] = Field(description="Concerns list in target language.")
    suggested_interview_questions: List[str] = Field(description="Interview questions in target language.")


class CandidateScreener:

    AVAILABLE_MODELS = [
        "gemini-3.1-flash-lite",
        "gemini-3.5-flash-lite",
        "gemini-3.7-flash",
        "gemini-3.8-flash",
    ]

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found.")
        self.client = genai.Client(api_key=self.api_key)

    def screen_candidate(
        self,
        cv_text: str,
        job_description: str,
        filename: str = "CV",
        language: str = "AZ"
    ) -> CandidateEvaluation:
        target_lang_name = "Azerbaijani" if language.upper() == "AZ" else "English"

        system_instruction = (
            "You are an expert Senior Technical Recruiter and AI Automation Lead. "
            "Objectively evaluate candidate CVs against the Job Description.\n"
            f"Generate all text fields (summary, matched_skills, missing_skills_or_gaps, key_strengths, concerns_or_red_flags, suggested_interview_questions) strictly in {target_lang_name}.\n"
            "Rules:\n"
            "1. Ground all claims in the provided CV text.\n"
            "2. Score according to the rubric: Technical (40%), Experience (30%), Education (15%), Presentation (15%).\n"
            "3. Overall score must be weighted average: round(0.40*tech + 0.30*exp + 0.15*edu + 0.15*pres).\n"
            "4. Categorize recommendation strictly: Strong Match (>= 75), Potential Match (50-74), Not a Match (< 50).\n"
            "5. Output must conform to the provided JSON schema."
        )

        prompt = f"""
TARGET OUTPUT LANGUAGE: {target_lang_name}

JOB DESCRIPTION:
{job_description}

CANDIDATE CV ({filename}):
{cv_text}
"""

        last_error = None
        for model_name in self.AVAILABLE_MODELS:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        response_mime_type="application/json",
                        response_schema=CandidateEvaluation,
                        temperature=0.2,
                    )
                )

                data = json.loads(response.text)
                evaluation = CandidateEvaluation(**data)

                calculated_score = round(
                    0.40 * evaluation.scores.technical_skills
                    + 0.30 * evaluation.scores.experience_relevance
                    + 0.15 * evaluation.scores.education_certifications
                    + 0.15 * evaluation.scores.presentation_structure
                )
                evaluation.overall_score = max(0, min(100, calculated_score))

                if evaluation.overall_score >= 75:
                    evaluation.recommendation = "Strong Match"
                elif evaluation.overall_score >= 50:
                    evaluation.recommendation = "Potential Match"
                else:
                    evaluation.recommendation = "Not a Match"

                return evaluation

            except Exception as e:
                last_error = e
                continue

        raise RuntimeError(f"Model generation error: {last_error}")
