from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from enum import Enum
from datetime import date

class ClaimCategory(str, Enum):
    DP = "DP"
    DPA = "DPA"
    RC = "RC"

class Sentiment(str, Enum):
    COOPERATIVE = "Cooperative"
    NEUTRAL = "Neutral"
    HOSTILE = "Hostile"
    DISTRESSED = "Distressed"

class InjurySeverity(str, Enum):
    NONE = "None"
    MINOR = "Minor"
    MAJOR = "Major"
    FATAL = "Fatal"

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
    
    # Phase 1 Improvements
    extraction_confidence: Optional[float] = Field(
        None, description="Confidence score from 0.0 to 1.0 representing how certain the AI is about the extracted data."
    )
    reasoning_trace: Optional[str] = Field(
        None, description="Explainable AI trace: explain exactly where in the document the data was found and why it was extracted this way."
    )
    missing_information_questions: List[str] = Field(
        default_factory=list, description="A list of follow-up questions to ask the claimant if mandatory data (like amount, date, or vehicle info) is missing."
    )
    is_probable_total_loss: Optional[bool] = Field(
        None, description="True if the damages described (e.g., structural frame, airbags deployed) likely result in a total loss."
    )
    potential_fraud_flags: List[str] = Field(
        default_factory=list, description="Any contradictions or suspicious elements found in the description that might indicate fraud."
    )
    
    # Phase 2 Improvements
    normalized_amount_usd: Optional[float] = Field(
        None, description="The total_estimated_amount normalized into a standard US Dollar float format, stripping symbols and converting if necessary."
    )
    subrogation_opportunity: Optional[bool] = Field(
        None, description="True if a third-party is explicitly at fault and there is an opportunity for the insurer to recover costs."
    )
    chronological_timeline: List[str] = Field(
        default_factory=list, description="A chronological sequence of events leading up to and following the incident, based on the description."
    )
    
    # Phase 4 Final Upgrades
    claimant_sentiment: Sentiment = Field(
        default=Sentiment.NEUTRAL, description="The detected emotional tone or sentiment of the claimant based on the language used in their description."
    )
    injury_severity_score: InjurySeverity = Field(
        default=InjurySeverity.NONE, description="Classification of the severity of injuries reported, if any."
    )

    @field_validator('incident_date')
    @classmethod
    def incident_date_must_not_be_in_future(cls, v):
        if v and v > date.today():
            raise ValueError(f"incident_date cannot be in the future. Got {v}.")
        return v
