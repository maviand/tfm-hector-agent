import json
from typing import List
from PIL import Image
from google import genai
from google.genai import types

from .schema import InsuranceClaim

class InsuranceClaimAgent:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-pro" # or gemini-1.5-pro

    def extract(self, images: List[Image.Image]) -> InsuranceClaim:
        """
        Extract structured data from a list of images representing a document.
        """
        prompt = (
            "You are an expert AI agent designed for an insurance claims system. "
            "Analyze the following document images (which may contain text, photos, and forms) "
            "and extract the required structured information.\n\n"
            "Crucially, classify the claim into one of these three categories:\n"
            "- DP (Daños Propios): Own vehicle damage.\n"
            "- DPA (Daños a la Propiedad Ajena): Third-party property damage caused by the insured.\n"
            "- RC (Responsabilidad Civil): Civil liability with a judicial claim or lawsuit.\n\n"
            "Also, extract any involved parties, incident dates, and evaluate the "
            "probability of judicialization based on the severity and context of the documents. "
            "Ensure your JSON strictly matches the schema."
        )
        
        # Prepare contents
        contents = [prompt] + images
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=InsuranceClaim,
                temperature=0.1, # Low temperature for extraction tasks
            )
        )
        
        # The response is guaranteed to match the JSON schema by the Gemini API
        raw_json = response.text
        return InsuranceClaim.model_validate_json(raw_json)

    def extract_from_file(self, file_path: str) -> InsuranceClaim:
        """
        Uploads a file (PDF, image, or scanned document) to the Gemini API and extracts structured data.
        """
        prompt = (
            "You are an expert AI agent designed for an insurance claims system. "
            "Analyze the uploaded document (which may be a PDF, image, or scanned document) "
            "and extract the required structured information.\n\n"
            "Crucially, classify the claim into one of these three categories:\n"
            "- DP (Daños Propios): Own vehicle damage.\n"
            "- DPA (Daños a la Propiedad Ajena): Third-party property damage caused by the insured.\n"
            "- RC (Responsabilidad Civil): Civil liability with a judicial claim or lawsuit.\n\n"
            "Also, extract any involved parties, incident dates, and evaluate the "
            "probability of judicialization based on the severity and context of the documents.\n"
            "If the document contains damage photographs, describe the visible damage "
            "in detail and estimate its severity within the 'description' field.\n"
            "Ensure your JSON strictly matches the schema."
        )
        
        # Upload the file using the File API
        uploaded_file = self.client.files.upload(file=file_path)
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[uploaded_file, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=InsuranceClaim,
                    temperature=0.1,
                )
            )
            raw_json = response.text
            return InsuranceClaim.model_validate_json(raw_json)
        finally:
            # Clean up the uploaded file to avoid unnecessary storage
            self.client.files.delete(name=uploaded_file.name)
