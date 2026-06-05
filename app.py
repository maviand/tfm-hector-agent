import streamlit as st
import pandas as pd
import json
import os
import time
import tempfile
from dotenv import load_dotenv

from src.agent.agent import InsuranceClaimAgent

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Hector.ai Batch Dashboard", page_icon="🛡️", layout="wide")

st.title("🛡️ Hector.ai - Insurance Claim Extractor (Batch Processing)")
st.markdown("Upload one or multiple claim documents (PDF, Image, or Text) to instantly extract structured JSON using Gemini 2.5 Flash with PII Redaction.")

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("GEMINI_API_KEY not found in environment. Please add it to your .env file.")
    st.stop()

# Initialize Agent
agent = InsuranceClaimAgent(api_key=api_key)

uploaded_files = st.file_uploader("Upload Claim Documents", type=["pdf", "png", "jpg", "jpeg", "txt"], accept_multiple_files=True)

if uploaded_files:
    if st.button(f"Extract Data for {len(uploaded_files)} File(s)"):
        results_data = []
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, file in enumerate(uploaded_files):
            status_text.text(f"Processing file {i+1} of {len(uploaded_files)}: {file.name}...")
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.name.split('.')[-1]}") as tmp:
                tmp.write(file.getvalue())
                tmp_path = tmp.name

            try:
                # Extract
                result = agent.extract_from_file(tmp_path)
                
                # Flatten the JSON for table
                json_str = result.model_dump_json()
                data = json.loads(json_str)
                # Convert complex types to string for CSV
                data['involved_parties'] = json.dumps(data.get('involved_parties', []))
                data['missing_information_questions'] = json.dumps(data.get('missing_information_questions', []))
                data['potential_fraud_flags'] = json.dumps(data.get('potential_fraud_flags', []))
                data['chronological_timeline'] = json.dumps(data.get('chronological_timeline', []))
                
                # Add filename
                data['filename'] = file.name
                results_data.append(data)
                
            except Exception as e:
                st.error(f"Error processing {file.name}: {str(e)}")
            finally:
                os.unlink(tmp_path)
            
            # Update progress
            progress_bar.progress((i + 1) / len(uploaded_files))
            
            # Rate limiting for Gemini API (if there are more files to process)
            if i < len(uploaded_files) - 1:
                status_text.text(f"Sleeping for 4 seconds to respect API rate limits...")
                time.sleep(4)

        status_text.text("Extraction Complete!")
        st.success(f"Successfully processed {len(results_data)} files.")
        
        if results_data:
            st.subheader("Batch Extraction Results")
            
            # Create DataFrame
            df = pd.DataFrame(results_data)
            
            # Reorder columns to put filename first
            cols = ['filename'] + [c for c in df.columns if c != 'filename']
            df = df[cols]
            
            st.dataframe(df, use_container_width=True)
            
            # CSV Export
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Combined Results as CSV",
                data=csv,
                file_name='hector_batch_results.csv',
                mime='text/csv',
            )
