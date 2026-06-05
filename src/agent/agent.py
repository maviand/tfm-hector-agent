import json
import pydantic
from typing import List
from PIL import Image
from google import genai
from google.genai import types
import os

from .schema import InsuranceClaim
from .security import PIIRedactor
from ..utils.pdf_utils import split_pdf

class InsuranceClaimAgent:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash" 

    def extract(self, images: List[Image.Image]) -> InsuranceClaim:
        """
        Extract structured data from a list of images representing a document.
        """
        prompt = self._get_base_prompt()
        contents = [prompt] + images
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=InsuranceClaim,
                temperature=0.1, 
            )
        )
        
        return self._validate_with_self_correction(response.text, contents)

    def extract_from_file(self, file_path: str, use_splitting: bool = True) -> InsuranceClaim:
        """
        Uploads a file (PDF, image, or scanned document) to the Gemini API and extracts structured data.
        If `use_splitting` is True and the file is a large PDF, it splits the PDF into chunks and processes the first chunk.
        (For full support, an aggregator function would combine chunks, but for now we process the primary chunk).
        """
        prompt = self._get_base_prompt()
        
        # Phase 2: PDF Splitting
        target_path = file_path
        tmp_chunks = []
        if use_splitting and file_path.lower().endswith('.pdf'):
            tmp_chunks = split_pdf(file_path, output_dir=os.path.dirname(file_path), max_pages=15)
            if tmp_chunks:
                target_path = tmp_chunks[0] # Just process the first chunk for the MVP

        # Upload the file using the File API
        uploaded_file = self.client.files.upload(file=target_path)
        
        try:
            contents = [uploaded_file, prompt]
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=InsuranceClaim,
                    temperature=0.1,
                )
            )
            return self._validate_with_self_correction(response.text, contents)
        finally:
            # Clean up the uploaded file to avoid unnecessary storage
            self.client.files.delete(name=uploaded_file.name)
            # Cleanup temporary chunk files if created
            if use_splitting and target_path != file_path:
                for chunk in tmp_chunks:
                    try:
                        os.remove(chunk)
                    except:
                        pass

    def _get_base_prompt(self) -> str:
        return (
            "You are an expert AI agent designed for an insurance claims system. "
            "Analyze the uploaded document (which may be a PDF, image, or scanned document) "
            "and extract the required structured information.\n\n"
            "Crucially, classify the claim into one of these three categories:\n"
            "- DP (Daños Propios): Own vehicle damage.\n"
            "- DPA (Daños a la Propiedad Ajena): Third-party property damage caused by the insured.\n"
            "- RC (Responsabilidad Civil): Civil liability with a judicial claim or lawsuit.\n\n"
            "If the document contains damage photographs, describe the visible damage "
            "in detail and estimate its severity within the 'description' field.\n\n"
            "*** NEW PHASE 1 CAPABILITIES ***\n"
            "1. Explainable AI: Provide a 'reasoning_trace' explaining exactly where the data was found.\n"
            "2. Confidence: Provide an 'extraction_confidence' score (0.0 - 1.0).\n"
            "3. Follow-ups: If critical data (date, amounts, parties) is missing, formulate 'missing_information_questions' for the claimant.\n"
            "4. Total Loss Predictor: Flag 'is_probable_total_loss' as true if frame/airbag damage is severe.\n"
            "5. Fraud Detection: List 'potential_fraud_flags' if the description contradicts the visible damage or facts.\n\n"
            "*** NEW PHASE 2 CAPABILITIES ***\n"
            "6. Amount Normalization: Extract 'normalized_amount_usd' as a standard float, converting euros or parsing strings like 1.000,50 to 1000.50.\n"
            "7. Subrogation Opportunity: Flag 'subrogation_opportunity' as true if the description clearly states a third party is at fault.\n"
            "8. Chronological Timeline: Create a 'chronological_timeline' list of strings detailing the sequence of events before and after the incident.\n"
            "9. Claimant Sentiment: Extract the 'claimant_sentiment' as Cooperative, Neutral, Hostile, or Distressed.\n"
            "10. Injury Severity: Extract the 'injury_severity_score' as None, Minor, Major, or Fatal.\n\n"
            "Ensure your JSON strictly matches the schema and validation rules (e.g., no future dates)."
        )

    def _validate_with_self_correction(self, raw_json: str, contents: list) -> InsuranceClaim:
        """
        Attempts to parse the JSON. If it fails Pydantic validation (e.g. date in the future),
        it feeds the error back to the LLM to correct itself once.
        """
        try:
            claim = InsuranceClaim.model_validate_json(raw_json)
        except pydantic.ValidationError as e:
            # Self-correction loop
            correction_prompt = (
                f"Your previous JSON output failed validation with the following error:\n{e}\n\n"
                "Please carefully correct the JSON output so it passes validation."
            )
            
            # Append previous JSON and the correction prompt to the context
            new_contents = contents + [raw_json, correction_prompt]
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=new_contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=InsuranceClaim,
                    temperature=0.1,
                )
            )
            claim = InsuranceClaim.model_validate_json(response.text)
            
        # Phase 1: Apply PII Redaction
        if claim.description:
            claim.description = PIIRedactor.redact(claim.description)
        if getattr(claim, 'reasoning_trace', None):
            claim.reasoning_trace = PIIRedactor.redact(claim.reasoning_trace)
            
        return claim
