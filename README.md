# AI-Powered CV Screening System

Avtomatlaşdırılmış CV qiymətləndirmə və təhlil sistemi. Sistem namizədlərin PDF və DOCX formatındakı CV fayllarını qəbul edir, verilmiş vakansiya tələblərinə (Job Description) əsasən meyarlar üzrə dəyərləndirir, uyğunluq balını hesablayır və nəticələri Google Sheets, CSV və Excel formatlarında saxlayır.

---

## 1. Layihə Haqqında (Azərbaycan dili)

### Əsas İmkanlar
- PDF və DOCX formatındakı fayllardan mətn məlumatlarının çıxarılması (`pypdf`, `python-docx`).
- Dəqiq və balanslaşdırılmış qiymətləndirmə meyarları:
  - Texniki bacarıqlar (40%)
  - İş təcrübəsi və layihələr (30%)
  - Təhsil və sertifikatlar (15%)
  - CV-nin strukturu və tərtibatı (15%)
- Strukturlaşdırılmış və etibarlı JSON məlumat çıxışı (Pydantic modelləri əsasında).
- HR komandası üçün əlavə təhlillər:
  - Uyğunlaşan bacarıqlar və çatışmayan tələblər
  - Namizədin güclü tərəfləri
  - Müsahibə zamanı veriləcək 3 hədəfli sual
- Nəticələrin birbaşa Google Sheets cədvəlinə (Webhook vasitəsilə), CSV və Excel faylına köçürülməsi.
- İkidilli interfeys və süni intellekt analizi (AZ / EN).

### Layihənin Quruluşu
```text
AiCvScreener/
|-- sample_data/                          # Sınaq üçün nümunə CV-lər və vakansiya mətni
|   |-- job_description.txt
|   |-- cv_1_strong_match_Murad_Aliyev.pdf
|   |-- cv_2_potential_match_Aysel_Mammadova.docx
|   `-- cv_3_mismatch_Kamran_Gasimov.pdf
|-- parser.py                             # Sənəd oxuma modulu (PDF, DOCX)
|-- screener.py                           # Gemini və Pydantic əsaslı qiymətləndirmə modulu
|-- exporter.py                           # Məlumatların cədvələ və fayllara köçürülməsi
|-- app.py                                # Streamlit istifadəçi interfeysi
|-- main.py                               # Terminal (CLI) vasitəsilə toplu emal skripti
|-- requirements.txt                      # Asılılıqlar
|-- .env.example                          # Ətraf mühit dəyişənləri şablonu
`-- README.md
```

### Quraşdırılma və İşə Salınma
1. Virtual mühiti aktivləşdirin və asılılıqları yükləyin:
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
```

2. `.env` faylını yaradın və Google Gemini API açarınızı daxil edin:
```env
GEMINI_API_KEY=your_api_key_here
GOOGLE_SHEETS_WEBHOOK_URL=your_webhook_url_optional
```

3. Tətbiqi başladın:
```bash
streamlit run app.py
```

4. Konsol rejimində (istifadəçi interfeysi olmadan) yoxlamaq üçün:
```bash
python main.py
```

### Google Sheets İnteqrasiyası
Nəticələrin avtomatik Google Sheets cədvəlinə yazılması üçün Google Apps Script redaktoruna aşağıdakı skripti əlavə edib Web App olaraq yerləşdirmək (deploy etmək) lazımdır:
```javascript
function doPost(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var data = JSON.parse(e.postData.contents);
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(["Ad", "Ümumi Bal", "Tövsiyə", "Texniki", "Təcrübə", "Təhsil", "Xülasə"]);
    }
    data.candidates.forEach(function(c) {
      sheet.appendRow([c.name, c.overall_score, c.recommendation, c.tech_score, c.exp_score, c.edu_score, c.summary]);
    });
    return ContentService.createTextOutput("SUCCESS").setMimeType(ContentService.MimeType.TEXT);
  } catch(err) {
    return ContentService.createTextOutput("ERROR: " + err.message).setMimeType(ContentService.MimeType.TEXT);
  }
}
```
Yerləşdirmə (Deploy) parametrlərində **Execute as** = `Me` və **Who has access** = `Anyone` seçilməlidir.

---

## 2. Project Overview (English)

### Key Capabilities
- Automated text ingestion from PDF and DOCX files (`pypdf`, `python-docx`).
- Weighted multi-dimensional evaluation criteria:
  - Technical skills alignment (40%)
  - Relevant experience and projects (30%)
  - Education and credentials (15%)
  - CV clarity and structure (15%)
- Strict schema enforcement via Pydantic to ensure reliable JSON parsing.
- Actionable recruitment insights:
  - Skill match and gap analysis
  - Key strengths identification
  - 3 targeted interview questions tailored to candidate gaps
- Multi-channel export: Google Sheets (Webhook), CSV, and Excel (.xlsx).
- Full bilingual support (Azerbaijani and English).

### Installation and Usage
1. Setup virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:
```env
GEMINI_API_KEY=your_api_key_here
GOOGLE_SHEETS_WEBHOOK_URL=your_webhook_url_optional
```

3. Run the interactive dashboard:
```bash
streamlit run app.py
```

4. Or run headlessly via CLI:
```bash
python main.py
```

### Benchmark Sample Evaluation
The repository includes three realistic candidate profiles tested against an AI Automation Engineer role:
1. `cv_1_strong_match_Murad_Aliyev.pdf`: Senior candidate with 3+ years in Python, n8n, and LLM APIs. Rated as **Strong Match (94/100)**.
2. `cv_2_potential_match_Aysel_Mammadova.docx`: Junior candidate with Python basics but lacking enterprise automation pipelines. Rated as **Potential Match (59/100)**.
3. `cv_3_mismatch_Kamran_Gasimov.pdf`: Graphic designer profile with no software engineering experience. Rated as **Not a Match (15/100)**.
