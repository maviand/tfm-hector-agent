import pytest
from src.agent.schema import InsuranceClaim, ClaimCategory

def test_insurance_claim_schema():
    # Simple test to verify the schema is correctly imported and can be validated
    sample_data = {
        "category": "DP",
        "description": "El coche se rayó en el parking.",
        "judicial_claim_present": False,
        "probability_of_judicialization": 0.05,
        "involved_parties": [
            {
                "name": "Juan Perez",
                "role": "Insured",
                "vehicle_info": "Toyota Corolla 1234ABC"
            }
        ],
        "total_estimated_amount": 150.0
    }
    
    claim = InsuranceClaim(**sample_data)
    assert claim.category == ClaimCategory.DP
    assert claim.judicial_claim_present is False
    assert claim.total_estimated_amount == 150.0
    assert len(claim.involved_parties) == 1
