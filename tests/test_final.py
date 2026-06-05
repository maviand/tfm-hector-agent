import pytest
from pydantic import ValidationError

from src.agent.schema import InsuranceClaim, Sentiment, InjurySeverity

def test_final_schema_fields():
    # Test valid assignment of Phase 2 and Phase 4 fields
    data = {
        "category": "RC",
        "description": "The third party driver explicitly admitted fault after running a red light. I broke my leg. Total damage is 1,500.50 EUROS.",
        "judicial_claim_present": False,
        "normalized_amount_usd": 1500.50,
        "subrogation_opportunity": True,
        "chronological_timeline": [
            "1. Insured stopped at red light.",
            "2. Third party rear-ended insured."
        ],
        "claimant_sentiment": "Distressed",
        "injury_severity_score": "Major"
    }
    
    claim = InsuranceClaim(**data)
    
    # Assertions
    assert claim.normalized_amount_usd == 1500.50
    assert claim.subrogation_opportunity is True
    assert claim.claimant_sentiment == Sentiment.DISTRESSED
    assert claim.injury_severity_score == InjurySeverity.MAJOR
