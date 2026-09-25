import os
import tempfile
import pytest
from backend.app.services.parser import DocumentParser
from backend.app.services.chunker import LegalChunker, LegalChunk

def test_txt_parser_with_page_markers():
    sample_text = """--- Page 1 ---
Clause 1. Definitions
In this Agreement, the following terms shall apply.
--- Page 2 ---
Clause 2. Payment Terms
Client shall pay $10,000 within thirty (30) days of invoice."""

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(sample_text)
        temp_path = f.name

    try:
        parsed = DocumentParser.parse_file(temp_path, "sample_contract.txt")
        assert parsed.page_count == 2
        assert parsed.file_type == "txt"
        assert "Payment Terms" in parsed.pages[1].text
        assert parsed.pages[0].page_number == 1
        assert parsed.pages[1].page_number == 2
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def test_legal_chunker_preserves_clause_metadata():
    class MockPage:
        def __init__(self, page_number, text):
            self.page_number = page_number
            self.text = text

    pages = [
        MockPage(1, "Clause 1.1 Confidentiality\nEach party shall protect confidential information.\n\nClause 1.2 Exceptions\nExceptions apply to publicly available data."),
        MockPage(2, "Section 4. Termination\nEither party may terminate upon 30 days notice.")
    ]

    chunks = LegalChunker.chunk_document("doc-test-123", pages, "employment_agreement")
    assert len(chunks) >= 2
    assert any(c.page_number == 1 for c in chunks)
    assert any(c.page_number == 2 for c in chunks)
    assert any("Confidentiality" in c.section or "1.1" in str(c.clause_id) for c in chunks)
