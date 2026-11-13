# Technical Workflow & Design Decisions Document

## 1. Executive Summary
This document outlines the architectural decisions, workflow design, and tooling rationale behind the **AI-Powered CV Screening System**, built for the AI Automation Internship Technical Task.

The objective was to create a functional, robust prototype capable of parsing multi-format candidate CVs, conducting an objective evaluation against a target Job Description (JD), and storing results systematically.

---

## 2. Tools & Technologies Used

| Tool / Library | Role in Architecture | Justification |
| :--- | :--- | :--- |
| **Python 3.12** | Core Programming Language | Industry standard for AI, automation, and data pipelines with unparalleled library ecosystem. |
| **Google Gemini (`gemini-3.1-flash-lite`)** | LLM Engine | High token processing speed, ultra-low latency, generous free tier via Google AI Studio, and native Structured JSON Schema support. |
| **Pydantic v2** | Data Validation & Schema | Enforces deterministic schema for model outputs, eliminating JSON decoding errors and ensuring type safety. |
| **Streamlit** | Frontend UI & Interactive Dashboard | Rapid, clean UI development enabling HR teams to upload CVs, configure JDs, inspect candidate radar cards, and trigger exports without CLI friction. |
| **pypdf & python-docx** | Document Parsing | Lightweight, robust local parsing of PDF and DOCX files without external paid SaaS dependencies. |
| **Pandas & openpyxl** | Data Wrangling & Export | Formats evaluation records into tabular views and exports to CSV and styled Excel. |
| **Google Sheets (Webhook / Apps Script)** | Cloud Storage Integration | Enables automated real-time synchronization of candidate evaluations into HR spreadsheets. |
| **n8n (Exported JSON)** | Low-Code Automation Workflow | Demonstrates low-code orchestration capability alongside code-based engineering. |

---

## 3. Key Technical Decisions & Rationale

### A. Rubric-Based Scoring vs. Naive Prompting
* **The Problem:** In typical implementations, asking an LLM to "Rate this candidate from 1 to 100" results in arbitrary, drifting scores that vary significantly between runs and heavily favor verbose CVs.
* **Our Solution:** We decoupled evaluation into four weighted pillars:
  1. **Technical Skills Match (40%)**: Explicit overlap between JD technical requirements and candidate skills.
  2. **Experience Relevance (30%)**: Seniority, role impact, and domain experience.
  3. **Education & Certifications (15%)**: Formal qualifications and verified learning credentials.
  4. **Structure & Presentation (15%)**: Readability, professional formatting, and clarity.
* **Result:** Consistent, explainable scores that HR stakeholders can trust and audit.

### B. Structured Outputs (Constrained Generation)
* Rather than asking the LLM for freeform markdown and using regex to parse scores, we utilized Google Gemini's `response_schema` bound to a Pydantic `CandidateEvaluation` model.
* This guarantees that the output strictly contains required fields (`scores`, `matched_skills`, `missing_skills_or_gaps`, `suggested_interview_questions`) every single time.

### C. Multi-Model Automatic Failover
* Public LLM endpoints occasionally experience transient 503 high-demand spikes.
* The `CandidateScreener` class implements a fallback sequence (`gemini-3.1-flash-lite` -> `gemini-3.5-flash-lite` -> `gemini-3.7-flash` -> `gemini-3.8-flash`), ensuring uninterrupted processing even under heavy API load.

### D. HR-Centric Interview Assistance
* Beyond simple scoring, the system generates **3 tailored interview questions** specifically designed to probe candidate claims or clarify missing skills identified during screening.

---

## 4. Evaluation Benchmark (3 Distinct Sample Candidates)

To prove system discrimination and fairness, 3 distinct candidate CVs were tested against an **AI Automation Engineer** JD:

1. **Murad Aliyev (PDF) — 94/100 (Strong Match)**
   * Possesses 3+ years in Python, n8n, Make, and LLM APIs.
   * System correctly assigned 95% in Tech & Experience, identifying Docker and Streamlit as key strengths.
2. **Aysel Mammadova (DOCX) — 59/100 (Potential Match)**
   * Junior IT graduate with foundational Python and scraping skills, but lacking production n8n/Make automation experience.
   * System accurately categorized her as a trainable junior candidate and drafted targeted interview questions regarding JSON handling.
3. **Kamran Gasimov (PDF) — 15/100 (Not a Match)**
   * Experienced Graphic Designer with no software or automation background.
   * System identified a complete technical mismatch (0% Tech & Exp), preventing HR from wasting interview bandwidth.

---

## 5. Scalability & Production Roadmap

For transition from prototype to enterprise-scale:
1. **Asynchronous Ingestion**: Introduce Celery / Redis queue to process batches of 1,000+ CVs concurrently.
2. **Multi-Modal / OCR Support**: Integrate Google Cloud Vision or Docling for scanned image-based CVs.
3. **Privacy & Anonymization (GDPR)**: Add a PII scrubber to mask candidate names and photos before LLM ingestion to eliminate subconscious bias.
4. **Vector Search (RAG)**: Embed past candidate pools in a vector database (e.g. Pinecone/Chroma) to match existing candidates to newly opened job requisitions automatically.
