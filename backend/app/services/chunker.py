import re
from typing import List, Dict, Any, Optional

CLAUSE_HEADER_PATTERN = re.compile(
    r"^(?:(?:Section|Clause|Article|Schedule|Exhibit|Paragraph)\s+([0-9A-Z\.]+)|([0-9]+\.[0-9]+(?:\.[0-9]+)?|[0-9]+\.)\s+([A-Z][^\n\.\:]{2,50}))",
    re.MULTILINE
)

class LegalChunk:
    def __init__(
        self,
        document_id: str,
        page_number: int,
        section: str,
        clause_id: Optional[str],
        text: str,
        document_type: str = "general_contract"
    ):
        self.document_id = document_id
        self.page_number = page_number
        self.section = section
        self.clause_id = clause_id
        self.text = text
        self.document_type = document_type

class LegalChunker:
    @staticmethod
    def chunk_document(
        document_id: str,
        pages: List[Any],
        document_type: str = "general_contract",
        max_chunk_words: int = 350,
        overlap_words: int = 50
    ) -> List[LegalChunk]:
        chunks: List[LegalChunk] = []
        current_section = "General / Preamble"
        current_clause = None

        for page in pages:
            page_text = page.text
            page_num = page.page_number
            
            # Split by paragraphs
            paragraphs = [p.strip() for p in page_text.split("\n\n") if p.strip()]
            
            current_buffer: List[str] = []
            current_word_count = 0

            for para in paragraphs:
                # Check if paragraph begins with a clause or section header
                lines = para.split("\n")
                first_line = lines[0].strip()
                match = CLAUSE_HEADER_PATTERN.match(first_line)
                
                if match:
                    # Flush previous buffer before starting new section
                    if current_buffer:
                        chunk_text = "\n\n".join(current_buffer)
                        chunks.append(LegalChunk(
                            document_id=document_id,
                            page_number=page_num,
                            section=current_section,
                            clause_id=current_clause,
                            text=chunk_text,
                            document_type=document_type
                        ))
                        current_buffer = []
                        current_word_count = 0
                    
                    clause_num = match.group(1) or match.group(2)
                    header_title = match.group(3) or first_line
                    current_clause = clause_num.strip() if clause_num else None
                    current_section = header_title.strip()[:60]
                
                words = len(para.split())
                if current_word_count + words > max_chunk_words and current_buffer:
                    chunk_text = "\n\n".join(current_buffer)
                    chunks.append(LegalChunk(
                        document_id=document_id,
                        page_number=page_num,
                        section=current_section,
                        clause_id=current_clause,
                        text=chunk_text,
                        document_type=document_type
                    ))
                    # Overlap with last paragraph
                    if overlap_words > 0 and len(current_buffer) > 1:
                        current_buffer = [current_buffer[-1], para]
                        current_word_count = len(current_buffer[0].split()) + words
                    else:
                        current_buffer = [para]
                        current_word_count = words
                else:
                    current_buffer.append(para)
                    current_word_count += words
            
            # Flush end of page buffer
            if current_buffer:
                chunk_text = "\n\n".join(current_buffer)
                chunks.append(LegalChunk(
                    document_id=document_id,
                    page_number=page_num,
                    section=current_section,
                    clause_id=current_clause,
                    text=chunk_text,
                    document_type=document_type
                ))

        # Fallback if document had no split paragraphs
        if not chunks:
            for page in pages:
                chunks.append(LegalChunk(
                    document_id=document_id,
                    page_number=page.page_number,
                    section="Full Document",
                    clause_id=None,
                    text=page.text,
                    document_type=document_type
                ))

        return chunks
