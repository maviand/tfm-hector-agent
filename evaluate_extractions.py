import os
import sys
import json
from dotenv import load_dotenv
from src.agent.agent import InsuranceClaimAgent

def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found.")
        sys.exit(1)
        
    agent = InsuranceClaimAgent(api_key=api_key)
    samples_dir = "data/samples/DP"
    
    if not os.path.exists(samples_dir):
        print(f"Directory {samples_dir} does not exist.")
        sys.exit(1)
        
    files = [f for f in os.listdir(samples_dir) if f.startswith("RC-")]
    
    results = {}
    
    for file in files:
        file_path = os.path.join(samples_dir, file)
        print(f"Processing {file}...")
        try:
            claim = agent.extract_from_file(file_path)
            claim_dict = claim.model_dump()
            
            extracted_fields = []
            for field, value in claim_dict.items():
                if field == "involved_parties":
                    if value and len(value) > 0:
                        extracted_fields.append(field)
                elif value is not None and value != "":
                    extracted_fields.append(field)
                    
            results[file] = {
                "extracted_fields": extracted_fields,
                "missing_fields": [f for f in claim_dict.keys() if f not in extracted_fields],
                "data": claim_dict
            }
        except Exception as e:
            print(f"Failed processing {file}: {e}")
            results[file] = {"error": str(e)}
            
        import time
        time.sleep(15)

    # Print summary
    print("\n--- Summary of Extractions ---")
    for file, res in results.items():
        if "error" in res:
            print(f"{file}: ERROR - {res['error']}")
        else:
            print(f"{file}:")
            print(f"  Extracted: {', '.join(res['extracted_fields'])}")
            if res['missing_fields']:
                print(f"  Missing:   {', '.join(res['missing_fields'])}")
            else:
                print("  Missing:   None (All fields extracted!)")
            print(f"  Category:  {res['data'].get('category')}")
            print(f"  Date:      {res['data'].get('incident_date')}")
            print(f"  Amount:    {res['data'].get('total_estimated_amount')}")
            print(f"  Judicial Claim Present: {res['data'].get('judicial_claim_present')}")
            print(f"  Prob of Judicialization: {res['data'].get('probability_of_judicialization')}")
            print()

if __name__ == '__main__':
    main()
