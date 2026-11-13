import io
from pathlib import Path
from typing import Union
import pypdf
import docx

class DocumentParser:

    @staticmethod
    def extract_text_from_pdf(file_source: Union[str, Path, bytes, io.BytesIO]) -> str:
        if isinstance(file_source, (str, Path)):
            reader = pypdf.PdfReader(str(file_source))
        elif isinstance(file_source, (bytes, bytearray)):
            reader = pypdf.PdfReader(io.BytesIO(file_source))
        else:
            reader = pypdf.PdfReader(file_source)

        text_parts = []
        for idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_parts.append(page_text.strip())

        extracted = "\n\n--- Page Break ---\n\n".join(text_parts)
        return DocumentParser._clean_text(extracted)

    @staticmethod
    def extract_text_from_docx(file_source: Union[str, Path, bytes, io.BytesIO]) -> str:
        if isinstance(file_source, (str, Path)):
            doc = docx.Document(str(file_source))
        elif isinstance(file_source, (bytes, bytearray)):
            doc = docx.Document(io.BytesIO(file_source))
        else:
            doc = docx.Document(file_source)

        text_parts = []
        for paragraph in doc.paragraphs:
            p_text = paragraph.text.strip()
            if p_text:
                text_parts.append(p_text)

        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    text_parts.append(" | ".join(row_text))

        extracted = "\n".join(text_parts)
        return DocumentParser._clean_text(extracted)

    @staticmethod
    def extract_text(file_source: Union[str, Path, bytes, io.BytesIO], filename: str) -> str:
        ext = filename.lower().split(".")[-1]
        if ext == "pdf":
            return DocumentParser.extract_text_from_pdf(file_source)
        elif ext in ["docx", "doc"]:
            return DocumentParser.extract_text_from_docx(file_source)
        elif ext == "txt":
            if isinstance(file_source, (bytes, bytearray)):
                return file_source.decode("utf-8", errors="ignore")
            elif hasattr(file_source, "read"):
                content = file_source.read()
                return content.decode("utf-8", errors="ignore") if isinstance(content, bytes) else str(content)
            elif isinstance(file_source, (str, Path)):
                return Path(file_source).read_text(encoding="utf-8", errors="ignore")
            return str(file_source)
        else:
            raise ValueError(f"Unsupported file format: .{ext}. Please upload PDF or DOCX.")

    @staticmethod
    def _clean_text(text: str) -> str:
        lines = [line.strip() for line in text.splitlines()]
        cleaned = "\n".join([line for line in lines if line])
        return cleaned
