import os
import sys
import time
import json
from dotenv import load_dotenv
from google import genai
from src.agent.agent import InsuranceClaimAgent

def main():
    load_dotenv()
    
    # 1. Setup directories
    synthetic_dir = os.path.join("data", "synthetic", "DP")
    results_dir = os.path.join(synthetic_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    
    template_pdf = os.path.join("data", "samples", "DP", "DP-001_Own_Damage_Rear_Collision.pdf")
    if not os.path.exists(template_pdf):
        print(f"Template not found: {template_pdf}")
        sys.exit(1)
        
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    agent = InsuranceClaimAgent(api_key=api_key)
    
    # 2. Upload template and generate synthetic data
    print("Uploading template PDF for synthetic generation...")
    uploaded_template = client.files.upload(file=template_pdf)
    
    prompt = """
    This is an insurance claim document. Use its structure and tone as a template.
    Generate 10 synthetic variations of this insurance claim with different but realistic data 
    (different incident dates, different amounts, different descriptions of damage, different 
    involved parties, varied probabilities of judicialization, etc.).
    
    Output the 10 variations as plain text. 
    Separate each variation EXACTLY with the string: ===CLAIM_SEPARATOR===
    Do not add any other markdown or intro/outro text. Just the 10 variations separated by the string.
    """
    
    print("Generating 10 synthetic claims...")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[uploaded_template, prompt]
        )
        content = response.text
    except Exception as e:
        print(f"Failed to generate synthetic data: {e}")
        sys.exit(1)
        
    # 3. Parse and save synthetic claims
    claims = [c.strip() for c in content.split("===CLAIM_SEPARATOR===") if c.strip()]
    if not claims:
        print("Failed to split claims correctly.")
        sys.exit(1)
        
    print(f"Successfully generated {len(claims)} synthetic claims.")
    
    synthetic_files = []
    for i, claim_text in enumerate(claims):
        file_path = os.path.join(synthetic_dir, f"synthetic_dp_{i+1:02d}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(claim_text)
        synthetic_files.append(file_path)
        print(f"Saved {file_path}")
        
    # Delete the uploaded template from API to clean up
    try:
        client.files.delete(name=uploaded_template.name)
    except:
        pass
        
    # Wait before we start extraction due to rate limits
    print("Waiting 15 seconds to respect rate limits...")
    time.sleep(15)
    
    # 4. Extract data from synthetic claims
    print("\nStarting extraction on synthetic files...")
    for file_path in synthetic_files:
        basename = os.path.basename(file_path)
        print(f"Processing {basename}...")
        try:
            claim_data = agent.extract_from_file(file_path)
            claim_dict = claim_data.model_dump()
            
            result_path = os.path.join(results_dir, f"{basename}.json")
            with open(result_path, "w", encoding="utf-8") as f:
                json.dump(claim_dict, f, indent=2, default=str)
                
            print(f"  -> Extracted successfully. Saved to {result_path}")
        except Exception as e:
            print(f"  -> Failed: {e}")
            
        print("Waiting 15 seconds before next extraction...")
        time.sleep(15)
        
    print("\nProcess completed successfully.")

if __name__ == '__main__':
    main()
