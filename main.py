import os
import argparse
from pathlib import Path
from dotenv import load_dotenv

from parser import DocumentParser
from screener import CandidateScreener
from exporter import ResultExporter

load_dotenv()

def run_screening_pipeline(
    cv_dir: str = "sample_data",
    jd_file: str = "sample_data/job_description.txt",
    output_dir: str = "output",
    webhook_url: str = None,
    language: str = "AZ"
):
    jd_path = Path(jd_file)
    if not jd_path.exists():
        raise FileNotFoundError(f"Job Description not found: {jd_file}")
    job_description = jd_path.read_text(encoding="utf-8")

    cv_folder = Path(cv_dir)
    cv_files = sorted([f for f in cv_folder.glob("cv_*.*") if f.suffix.lower() in [".pdf", ".docx", ".txt"]])
    if not cv_files:
        raise FileNotFoundError(f"No CV files found in {cv_dir}")

    screener = CandidateScreener()
    evaluations = []

    for idx, cv_path in enumerate(cv_files, 1):
        raw_text = DocumentParser.extract_text(cv_path, cv_path.name)
        evaluation = screener.screen_candidate(raw_text, job_description, cv_path.name, language=language)
        evaluations.append(evaluation)

    out_path = Path(output_dir)
    out_path.mkdir(exist_ok=True)

    df = ResultExporter.to_dataframe(evaluations)
    
    csv_file = out_path / "screening_results.csv"
    csv_file.write_bytes(ResultExporter.to_csv_bytes(df))

    xlsx_file = out_path / "screening_results.xlsx"
    xlsx_file.write_bytes(ResultExporter.to_excel_bytes(df))

    target_webhook = webhook_url or os.getenv("GOOGLE_SHEETS_WEBHOOK_URL")
    if target_webhook:
        try:
            ResultExporter.sync_to_google_sheets_webhook(evaluations, target_webhook)
        except Exception:
            pass

    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI CV Screening CLI")
    parser.add_argument("--cv-dir", default="sample_data")
    parser.add_argument("--jd", default="sample_data/job_description.txt")
    parser.add_argument("--output", default="output")
    parser.add_argument("--webhook", default=None)
    parser.add_argument("--lang", default="AZ")
    args = parser.parse_args()

    run_screening_pipeline(args.cv_dir, args.jd, args.output, args.webhook, args.lang)
