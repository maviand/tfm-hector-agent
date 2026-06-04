from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import date

class ClaimCategory(str, Enum):
    DP = "DP"
    DPA = "DPA"
    RC = "RC"

class InvolvedParty(BaseModel):
    name: Optional[str] = Field(None, description="Name of the involved party (insured or third-party)")
    role: str = Field(description="Role of the party (e.g., 'Insured', 'Third-Party Driver', 'Pedestrian', 'Lawyer')")
    vehicle_info: Optional[str] = Field(None, description="Make, model, or license plate if applicable")

class InsuranceClaim(BaseModel):
    category: ClaimCategory = Field(
        description="Classification of the claim: DP (Daños Propios / own vehicle damage), DPA (Daños a la Propiedad Ajena / third-party property damage), or RC (Responsabilidad Civil / civil liability with judicial claim)"
    )
    incident_date: Optional[date] = Field(None, description="Date when the incident occurred")
    description: str = Field(description="Detailed description of the incident, damages, or judicial claim")
    judicial_claim_present: bool = Field(description="True if there is a judicial claim or lawsuit involved (expected True for RC)")
    probability_of_judicialization: Optional[float] = Field(
        None, description="Estimated probability (0.0 to 1.0) that this claim will result in a lawsuit, based on the documents"
    )
    involved_parties: List[InvolvedParty] = Field(
        default_factory=list, description="List of parties involved in the incident"
    )
    total_estimated_amount: Optional[float] = Field(
        None, description="Estimated total amount of damages or claim requested, if mentioned"
    )
