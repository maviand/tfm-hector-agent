import re

class PIIRedactor:
    """
    A utility to redact Personally Identifiable Information (PII) from text.
    Handles Spanish specific formats like DNI, NIE, as well as general formats.
    """
    
    # Common Spanish DNI format: 8 digits followed by a letter
    DNI_PATTERN = r'\b\d{8}[A-HJ-NP-TV-Z]\b'
    
    # Common Spanish NIE format: X, Y or Z followed by 7 digits and a letter
    NIE_PATTERN = r'\b[XYZ]\d{7}[A-HJ-NP-TV-Z]\b'
    
    # Credit Card pattern (basic 16 digits with or without dashes/spaces)
    CREDIT_CARD_PATTERN = r'\b(?:\d[ -]*?){13,16}\b'
    
    # Email pattern
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    # Spanish Phone Numbers (e.g. 6XX XXX XXX or 9XX XXX XXX, with optional +34)
    PHONE_PATTERN = r'\b(?:\+34\s*)?[6789]\d{2}[\s\-]?\d{3}[\s\-]?\d{3}\b'

    @classmethod
    def redact(cls, text: str) -> str:
        if not text:
            return text
            
        redacted_text = text
        
        # Redact Credit Cards (do this before numbers to avoid clashing)
        redacted_text = re.sub(cls.CREDIT_CARD_PATTERN, '[CREDIT_CARD_REDACTED]', redacted_text)
        
        # Redact DNI
        redacted_text = re.sub(cls.DNI_PATTERN, '[DNI_REDACTED]', redacted_text, flags=re.IGNORECASE)
        
        # Redact NIE
        redacted_text = re.sub(cls.NIE_PATTERN, '[NIE_REDACTED]', redacted_text, flags=re.IGNORECASE)
        
        # Redact Emails
        redacted_text = re.sub(cls.EMAIL_PATTERN, '[EMAIL_REDACTED]', redacted_text, flags=re.IGNORECASE)
        
        # Redact Phone Numbers
        redacted_text = re.sub(cls.PHONE_PATTERN, '[PHONE_REDACTED]', redacted_text)
        
        return redacted_text
