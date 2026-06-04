import argparse
import os
import sys
from dotenv import load_dotenv

from agent.agent import InsuranceClaimAgent
from utils.document_parser import DocumentParser

def main():
    parser = argparse.ArgumentParser(description="Extract structured data from insurance claims.")
    parser.add_argument("--input", type=str, required=True, help="Path to the input PDF or image.")
    parser.add_argument("--output_dir", type=str, default="data/output", help="Directory to save the extracted JSON.")
    
    args = parser.parse_args()
    
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables.", file=sys.stderr)
        sys.exit(1)
        
    print(f"Processing: {args.input}")
    
    # Process document
    parser_util = DocumentParser()
    try:
        images = parser_util.extract_images_from_file(args.input)
    except Exception as e:
        print(f"Failed to parse document: {e}", file=sys.stderr)
        sys.exit(1)
        
    print(f"Extracted {len(images)} page(s) from document. Running extraction...")
    
    # Run Agent
    agent = InsuranceClaimAgent(api_key=api_key)
    try:
        result = agent.extract(images)
        print("\n--- Extraction Result ---")
        print(result.model_dump_json(indent=2))
        
        # Save output
        os.makedirs(args.output_dir, exist_ok=True)
        base_name = os.path.basename(args.input)
        name, _ = os.path.splitext(base_name)
        output_path = os.path.join(args.output_dir, f"{name}_extracted.json")
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result.model_dump_json(indent=2))
        print(f"\nSaved result to: {output_path}")
        
    except Exception as e:
        print(f"Extraction failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
