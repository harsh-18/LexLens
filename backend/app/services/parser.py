import os
import re
from typing import List, Dict, Any
from pathlib import Path
import pypdf
import docx

class ParsedPage:
    def __init__(self, page_number: int, text: str):
        self.page_number = page_number
        self.text = text

class ParsedDocument:
    def __init__(self, filename: str, file_type: str, file_size: int, pages: List[ParsedPage], full_text: str):
        self.filename = filename
        self.file_type = file_type
        self.file_size = file_size
        self.pages = pages
        self.page_count = len(pages)
        self.full_text = full_text

class DocumentParser:
    @staticmethod
    def validate_file_safety(file_path: str, ext: str) -> None:
        """Verify binary file headers to protect against malicious disguised executables."""
        if not os.path.exists(file_path):
            raise FileNotFoundError("Uploaded file path does not exist")
        
        with open(file_path, "rb") as f:
            header = f.read(16)
        
        # Block Windows PE/EXE and Linux ELF binaries
        if header.startswith(b"MZ") or header.startswith(b"\x7fELF"):
            raise ValueError("Executable binaries or malicious payload files are strictly prohibited.")

        # Validate PDF signature
        if ext == ".pdf":
            if not header.startswith(b"%PDF"):
                raise ValueError("Corrupted or invalid PDF file header signature.")
        # Validate DOCX (ZIP format) signature
        elif ext in [".docx", ".doc"]:
            if not header.startswith(b"PK\x03\x04"):
                raise ValueError("Invalid DOCX archive signature.")

    @staticmethod
    def parse_file(file_path: str, original_filename: str) -> ParsedDocument:
        ext = Path(original_filename).suffix.lower()
        file_size = os.path.getsize(file_path)
        
        # Enforce security header validation
        DocumentParser.validate_file_safety(file_path, ext)
        
        if ext == ".pdf":
            return DocumentParser._parse_pdf(file_path, original_filename, file_size)
        elif ext in [".docx", ".doc"]:
            return DocumentParser._parse_docx(file_path, original_filename, file_size)
        elif ext in [".txt", ".md"]:
            return DocumentParser._parse_txt(file_path, original_filename, file_size)
        else:
            return DocumentParser._parse_txt(file_path, original_filename, file_size)

    @staticmethod
    def _parse_pdf(file_path: str, filename: str, file_size: int) -> ParsedDocument:
        pages: List[ParsedPage] = []
        try:
            reader = pypdf.PdfReader(file_path)
            for idx, page in enumerate(reader.pages):
                raw_text = page.extract_text() or ""
                cleaned = DocumentParser._clean_text(raw_text)
                pages.append(ParsedPage(page_number=idx + 1, text=cleaned))
        except Exception as e:
            # Fallback if PDF fails or is protected
            pages.append(ParsedPage(page_number=1, text=f"[PDF Extraction Error: {str(e)}]"))
            
        if not pages or all(len(p.text.strip()) == 0 for p in pages):
            pages = [ParsedPage(page_number=1, text="[Document contained no extractable digital text]")]
            
        full_text = "\n\n".join([f"--- Page {p.page_number} ---\n{p.text}" for p in pages])
        return ParsedDocument(filename=filename, file_type="pdf", file_size=file_size, pages=pages, full_text=full_text)

    @staticmethod
    def _parse_docx(file_path: str, filename: str, file_size: int) -> ParsedDocument:
        pages: List[ParsedPage] = []
        try:
            doc = docx.Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            
            # Estimate pages ~ 400 words per page
            current_page_text: List[str] = []
            word_count = 0
            page_num = 1
            
            for p in paragraphs:
                words = len(p.split())
                if word_count + words > 450 and current_page_text:
                    pages.append(ParsedPage(page_number=page_num, text="\n".join(current_page_text)))
                    page_num += 1
                    current_page_text = [p]
                    word_count = words
                else:
                    current_page_text.append(p)
                    word_count += words
                    
            if current_page_text:
                pages.append(ParsedPage(page_number=page_num, text="\n".join(current_page_text)))
        except Exception as e:
            pages.append(ParsedPage(page_number=1, text=f"[DOCX Extraction Error: {str(e)}]"))
            
        if not pages:
            pages = [ParsedPage(page_number=1, text="[Empty Document]")]
            
        full_text = "\n\n".join([f"--- Page {p.page_number} ---\n{p.text}" for p in pages])
        return ParsedDocument(filename=filename, file_type="docx", file_size=file_size, pages=pages, full_text=full_text)

    @staticmethod
    def _parse_txt(file_path: str, filename: str, file_size: int) -> ParsedDocument:
        pages: List[ParsedPage] = []
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            
            # Check for page markers like '--- Page X ---' or '[Page X]'
            page_splits = re.split(r"(?:---|===|\[)\s*Page\s+(\d+)\s*(?:---|===|\])", content, flags=re.IGNORECASE)
            
            if len(page_splits) > 2:
                # We have explicit page markers
                for i in range(1, len(page_splits), 2):
                    p_num = int(page_splits[i])
                    p_text = DocumentParser._clean_text(page_splits[i+1])
                    pages.append(ParsedPage(page_number=p_num, text=p_text))
            else:
                # Segment by word count (~400 words per page)
                paragraphs = content.split("\n\n")
                current_page: List[str] = []
                words_accum = 0
                page_counter = 1
                for para in paragraphs:
                    w_count = len(para.split())
                    if words_accum + w_count > 450 and current_page:
                        pages.append(ParsedPage(page_number=page_counter, text="\n\n".join(current_page)))
                        page_counter += 1
                        current_page = [para]
                        words_accum = w_count
                    else:
                        current_page.append(para)
                        words_accum += w_count
                if current_page:
                    pages.append(ParsedPage(page_number=page_counter, text="\n\n".join(current_page)))
        except Exception as e:
            pages.append(ParsedPage(page_number=1, text=f"[TXT Read Error: {str(e)}]"))
            
        if not pages:
            pages = [ParsedPage(page_number=1, text="[Empty Document]")]
            
        full_text = "\n\n".join([f"--- Page {p.page_number} ---\n{p.text}" for p in pages])
        return ParsedDocument(filename=filename, file_type="txt", file_size=file_size, pages=pages, full_text=full_text)

    @staticmethod
    def _clean_text(text: str) -> str:
        # Standardize whitespace and remove non-printable characters
        text = re.sub(r"\r\n", "\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()
