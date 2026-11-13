import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import docx

SAMPLE_DIR = Path("sample_data")
SAMPLE_DIR.mkdir(exist_ok=True)

# 1. Job Description
JD_TEXT = """Job Title: AI Automation Engineer / Python Specialist
Department: Technology & Innovation
Location: Remote / Hybrid

Role Summary:
We are looking for an AI Automation Engineer to design, build, and deploy intelligent workflows that automate business processes. You will leverage modern LLMs (Gemini, OpenAI), automation tools (n8n, Make), and Python to build automated agents, document intelligence pipelines, and system integrations.

Key Responsibilities:
- Develop automated workflows using Python, n8n, Make, and webhook integrations.
- Implement LLM-based solutions utilizing prompt engineering, structured JSON outputs, and function calling.
- Extract, parse, and analyze unstructured documents (PDFs, DOCX, CSVs) using Python libraries (pypdf, docx).
- Connect AI models with third-party platforms (Google Sheets API, Notion, CRMs, internal databases).
- Monitor, debug, and optimize workflow execution, latency, and API costs.

Required Qualifications & Skills:
- 2+ years of hands-on experience in Python programming (APIs, Requests, Pandas, Pydantic).
- Strong practical experience with LLM APIs (OpenAI API, Google Gemini, Anthropic).
- Proven experience building automated workflows in n8n or Make.com.
- Familiarity with document parsing, data extraction, and regex.
- Solid understanding of REST APIs, Webhooks, and JSON data structures.
- Bachelor's degree in Computer Science, Information Technology, or equivalent practical experience.

Nice-to-Have:
- Experience building web prototypes using Streamlit or FastAPI.
- Knowledge of Docker and cloud deployments.
- Experience with Google Sheets API / Google Apps Script.
"""

(SAMPLE_DIR / "job_description.txt").write_text(JD_TEXT, encoding="utf-8")

# Helper for PDF generation
def create_pdf(filename: Path, title: str, content_blocks: list):
    doc = SimpleDocTemplate(str(filename), pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor='#1a365d',
        spaceAfter=10
    )
    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor='#2b6cb0',
        spaceBefore=10,
        spaceAfter=5
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor='#2d3748',
        spaceAfter=6
    )

    story = [Paragraph(title, title_style), Spacer(1, 10)]
    for heading, text in content_blocks:
        story.append(Paragraph(heading, h2_style))
        for line in text.strip().split("\n"):
            if line.strip():
                story.append(Paragraph(line.strip(), body_style))
        story.append(Spacer(1, 8))

    doc.build(story)

# 2. Candidate 1: Murad Aliyev (Strong Match) - PDF
cv1_blocks = [
    ("Contact Info", "Email: murad.aliyev.ai@gmail.com | Phone: +994 50 123 45 67 | Baku, Azerbaijan | GitHub: github.com/murad-ai"),
    ("Professional Summary", "Results-oriented AI Automation Engineer with 3+ years of experience designing scalable automation pipelines, LLM-powered systems, and intelligent document processing workflows. Proven track record in orchestrating n8n and Python to cut manual operational time by 70%."),
    ("Core Skills & Competencies", "• Programming: Python (FastAPI, Streamlit, Pandas, Pydantic, Requests, PyPDF, python-docx)<br/>• AI & LLMs: Google Gemini API, OpenAI GPT-4o, Prompt Engineering, Structured JSON Outputs, LangChain<br/>• Automation & Integration: n8n (advanced workflows), Make.com, Webhooks, REST APIs, Google Sheets API<br/>• DevOps & Tools: Docker, Git, Linux, Postman"),
    ("Work Experience", 
     "<b>Senior AI Automation Developer | NexaTech Solutions (2022 - Present)</b><br/>"
     "- Architected end-to-end CV and invoice processing pipelines using Python, pypdf, and LLM structured outputs.<br/>"
     "- Built multi-step n8n automation scenarios integrating Webhooks, Google Sheets, and Slack alerts.<br/>"
     "- Deployed internal HR evaluation dashboards in Streamlit, saving 15 hours weekly for recruiting teams.<br/>"
     "<br/>"
     "<b>Python Developer | Innovate Data Lab (2021 - 2022)</b><br/>"
     "- Built web scraping scripts and REST API connectors for automated data collection.<br/>"
     "- Integrated third-party APIs (Google Drive, Sheets, CRM) using Python scripts and OAuth2."),
    ("Education & Certifications", 
     "• BSc in Computer Science | Baku State University (2017 - 2021)<br/>"
     "• Certified n8n Workflow Automation Specialist (2023)<br/>"
     "• DeepLearning.AI: Building Systems with the ChatGPT API (2023)")
]
create_pdf(SAMPLE_DIR / "cv_1_strong_match_Murad_Aliyev.pdf", "Murad Aliyev - AI Automation Engineer", cv1_blocks)

# 3. Candidate 2: Aysel Mammadova (Potential Match / Junior) - DOCX
doc = docx.Document()
doc.add_heading("Aysel Mammadova", 0)
doc.add_paragraph("Email: aysel.mammadova.dev@outlook.com | Phone: +994 55 987 65 43 | Sumqayit, Azerbaijan")

doc.add_heading("Professional Summary", level=1)
doc.add_paragraph(
    "Motivated Junior Python Developer and recent graduate with strong foundational programming knowledge "
    "and passion for artificial intelligence. Seeking an opportunity to grow in AI workflow automation and Python development."
)

doc.add_heading("Technical Skills", level=1)
doc.add_paragraph("• Languages: Python (Intermediate), SQL, HTML/CSS")
doc.add_paragraph("• Libraries: Pandas, NumPy, Requests, BeautifulSoup, basic Matplotlib")
doc.add_paragraph("• AI Tools: Experience experimenting with OpenAI ChatGPT API via simple Python scripts")
doc.add_paragraph("• Tools: Git, VS Code, Jupyter Notebook, Google Sheets")

doc.add_heading("Experience & Projects", level=1)
p = doc.add_paragraph()
p.add_run("Junior Data & Python Assistant | TechStart Hub (2023 - 2024)\n").bold = True
p.add_run("- Wrote Python scripts to scrape product listings from e-commerce sites using BeautifulSoup and Requests.\n")
p.add_run("- Cleaned and formatted datasets with Pandas before exporting to Excel and Google Sheets.\n")
p.add_run("- Built a small pet project using OpenAI API to summarize student lecture notes.\n")
p.add_run("Note: Eager to learn workflow automation tools like n8n and Make; currently studying their official documentation.")

doc.add_heading("Education", level=1)
doc.add_paragraph("BSc in Information Technology | Azerbaijan State Oil and Industry University (ASOIU) (2020 - 2024, GPA: 88/100)")
doc.save(str(SAMPLE_DIR / "cv_2_potential_match_Aysel_Mammadova.docx"))

# 4. Candidate 3: Kamran Gasimov (Mismatch) - PDF
cv3_blocks = [
    ("Contact Info", "Email: kamran.creative.design@gmail.com | Phone: +994 70 333 22 11 | Baku, Azerbaijan | Portfolio: behance.net/kamran_design"),
    ("Professional Summary", "Creative Graphic Designer and Brand Identity Specialist with 4+ years of agency experience crafting modern visual assets, social media branding, and print materials. Passionate about typography and minimalist design."),
    ("Design Skills & Software", "• Adobe Creative Cloud: Photoshop, Illustrator, InDesign, Premiere Pro<br/>• UI/UX Tools: Figma, Canva Pro, Sketch<br/>• Specialties: Logo Design, Social Media Posters, Packaging, Vector Illustration, Brand Guidelines<br/>• Soft Skills: Creative thinking, visual storytelling, client presentations"),
    ("Work Experience", 
     "<b>Senior Graphic Designer | ArtStudio Creative Agency (2022 - Present)</b><br/>"
     "- Led visual branding projects for 20+ commercial brands across retail and hospitality sectors.<br/>"
     "- Designed high-converting social media creatives and promotional banners.<br/>"
     "- Managed design team of 3 junior graphic designers.<br/>"
     "<br/>"
     "<b>Graphic & UI Designer | BrandUp Marketing (2020 - 2022)</b><br/>"
     "- Created flyers, brochures, and digital banners for digital marketing campaigns.<br/>"
     "- Designed wireframes and mobile UI concepts using Figma."),
    ("Education", 
     "• BA in Fine Arts & Graphic Design | Azerbaijan State Academy of Fine Arts (2016 - 2020)")
]
create_pdf(SAMPLE_DIR / "cv_3_mismatch_Kamran_Gasimov.pdf", "Kamran Gasimov - Graphic Designer", cv3_blocks)

print("Sample files created successfully in:", SAMPLE_DIR.resolve())
