import pytest
from datetime import date, timedelta
from pydantic import ValidationError
import json

from src.agent.schema import InsuranceClaim, ClaimCategory, InvolvedParty
from src.agent.security import PIIRedactor

def test_incident_date_validation():
    # Test valid date
    valid_data = {
        "category": "DP",
        "description": "Car crash",
        "judicial_claim_present": False,
        "incident_date": str(date.today() - timedelta(days=5))
    }
    claim = InsuranceClaim(**valid_data)
    assert claim.incident_date < date.today()

    # Test future date failure
    invalid_data = {
        "category": "DP",
        "description": "Future crash",
        "judicial_claim_present": False,
        "incident_date": str(date.today() + timedelta(days=5))
    }
    with pytest.raises(ValidationError) as exc_info:
        InsuranceClaim(**invalid_data)
    assert "incident_date cannot be in the future" in str(exc_info.value)

def test_pii_redaction():
    text = "Contact me at 612 345 678 or my email is test@example.com. My DNI is 12345678Z and card 4532 1111 2222 3333."
    redacted = PIIRedactor.redact(text)
    
    assert "612 345 678" not in redacted
    assert "[PHONE_REDACTED]" in redacted
    assert "test@example.com" not in redacted
    assert "[EMAIL_REDACTED]" in redacted
    assert "12345678Z" not in redacted
    assert "[DNI_REDACTED]" in redacted
    assert "4532 1111 2222 3333" not in redacted
    assert "[CREDIT_CARD_REDACTED]" in redacted

def test_schema_optional_fields():
    data = {
        "category": "RC",
        "description": "Lawsuit",
        "judicial_claim_present": True,
        "extraction_confidence": 0.95,
        "is_probable_total_loss": True,
        "potential_fraud_flags": ["Claimed whiplash but was not in car"],
        "reasoning_trace": "Found in page 2"
    }
    claim = InsuranceClaim(**data)
    assert claim.extraction_confidence == 0.95
    assert claim.is_probable_total_loss is True
    assert len(claim.potential_fraud_flags) == 1
