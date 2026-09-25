import hashlib
import hmac
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from fastapi import HTTPException, Security, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from backend.app.config import settings
from backend.app.database import get_db

security_scheme = HTTPBearer(auto_error=False)

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)",
    r"(reveal|print|show|dump)\s+(the\s+)?(system\s+prompt|developer\s+instructions|system\s+message)",
    r"you\s+are\s+now\s+(in\s+developer\s+mode|an\s+unfiltered|dan|jailbreak)",
    r"disregard\s+(the\s+)?(safety\s+guidelines|system\s+prompt|above)",
    r"system\s*:\s*you\s+must",
    r"<\|im_start\|>",
    r"<\|im_end\|>",
]

class SecurityService:
    @staticmethod
    def hash_password(password: str) -> str:
        # PBKDF2 with SHA-256 for secure zero-dependency password hashing
        salt = os.urandom(16).hex()
        pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
        return f"{salt}${pwd_hash}"

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            salt, stored_hash = hashed_password.split("$")
            computed = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
            return hmac.compare_digest(stored_hash, computed)
        except Exception:
            return False

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None

    @staticmethod
    def sanitize_untrusted_input(text: str) -> tuple[str, bool]:
        """
        Sanitizes text and checks for prompt injection heuristics.
        Returns: (sanitized_text, contains_injection_flag)
        """
        flagged = False
        sanitized = text
        for pattern in PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, sanitized, re.IGNORECASE):
                flagged = True
                sanitized = re.sub(pattern, "[UNTRUSTED_INSTRUCTION_REDACTED]", sanitized, flags=re.IGNORECASE)
                
        # Neutralize XML/tag delimiters to prevent escaping out of untrusted wrappers
        if "<untrusted_document_data>" in sanitized or "</untrusted_document_data>" in sanitized:
            flagged = True
            sanitized = sanitized.replace("<untrusted_document_data>", "&lt;untrusted_document_data&gt;")
            sanitized = sanitized.replace("</untrusted_document_data>", "&lt;/untrusted_document_data&gt;")
        return sanitized, flagged

    @staticmethod
    def wrap_untrusted_context(doc_text: str) -> str:
        """
        Encloses retrieved legal text inside rigid untrusted context tags.
        """
        sanitized, _ = SecurityService.sanitize_untrusted_input(doc_text)
        return f"\n<untrusted_document_data>\n{sanitized}\n</untrusted_document_data>\n"

def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db)
):
    from backend.app.models.user import User
    
    # If no token provided, return or create a default demo user for frictionless testing
    if not auth:
        demo_user = db.query(User).filter(User.is_demo == True).first()
        if not demo_user:
            demo_user = User(
                id="demo-user-lexlens",
                email="demo@lexlens.ai",
                hashed_password=SecurityService.hash_password("DemoLexLens2026!"),
                full_name="Demo User",
                is_demo=True,
                is_active=True
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
        return demo_user

    payload = SecurityService.decode_access_token(auth.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication credentials."
        )

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive."
        )
    return user

def verify_document_ownership(document_id: str, user, db: Session):
    from backend.app.models.document import Document
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    # Allow demo user to access demo-seeded documents or documents they created
    if doc.user_id != user.id and not (user.is_demo and doc.user_id == "demo-user-lexlens"):
        raise HTTPException(status_code=403, detail="Unauthorized access to document.")
    return doc
