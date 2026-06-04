# TFM Hector Agent: Insurance Claim Extractor

This repository contains a Python agent powered by multimodal AI to extract structured information from insurance claim PDFs and images.

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   Create a `.env` file and add your AI API Key:
   ```env
   GEMINI_API_KEY=your_google_gemini_api_key
   # or OPENAI_API_KEY=... if using OpenAI
   ```

## Usage

Place your PDF or image insurance claims in the `data/input/` directory, then run the agent:

```bash
python src/main.py --input data/input/sample_claim.pdf
```

The extracted structured JSON will be printed to the console and saved in `data/output/`.
