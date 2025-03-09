# Intelligent Excel Analyzer with Gemma-7B 📊🤖

<div style="text-align: center;">
  <img src="https://github.com/TheAwaken1/Intelligent-Excel-Analyzer/raw/main/icon.png" width="300" alt="App Icon">
</div>

An AI-powered tool to analyze Excel and CSV files using natural language queries with the Gemma-7B model.

## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/Intelligent-Excel-Analyzer.git
   cd Intelligent-Excel-Analyzer

Set Up a Virtual Environment (recommended):
bash

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install Dependencies:
bash

pip install -r requirements.txt

This installs all required libraries, including openpyxl for Excel export support.

Access the Gemma-7B Model (One-Time Setup):
Create a Hugging Face Account: Sign up at huggingface.co.

Request Access to Gemma-7B: Visit https://huggingface.co/google/gemma-7b-it, agree to the terms (approval is instant!).

Log In with Token:
bash

pip install huggingface_hub
huggingface-cli login

Generate a token from Hugging Face Settings and paste it when prompted.

Note: If you’ve accessed Gemma-7B before, skip to step 5.

Run the App:
bash

python app.py

The first run downloads Gemma-7B (several GB, ~5-10 mins depending on speed). Open the Gradio UI at http://127.0.0.1:7860.

Usage
Upload an Excel or CSV file.

Use natural language requests (e.g., "show items X, Y", "average Quantity").

Export results as Excel or CSV with the AI response included.

Custom Models
Want to use a different model? You can swap Gemma-7B for any compatible model from Hugging Face!
Edit the Code:
Open app.py and find the line: model_name = "google/gemma-7b-it".

Change it to your preferred model (e.g., "mistralai/Mixtral-8x7B-Instruct-v0.1").

Save the file.

Request Access:
Visit the model’s page (e.g., https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1 for Mixtral).

Agree to the terms if required (approval is usually instant).

Run the App:
Ensure you’re logged in (huggingface-cli login with your token).

Run python app.py. The new model will download on first use.

Notes:
Use models compatible with AutoModelForCausalLM (e.g., instruction-tuned models).

Larger models may need more VRAM or adjusted quantization settings.

If the AI response format changes, you might need to tweak the JSON parsing in filter_data (advanced users only).

Requirements
Hardware: GPU with 8GB+ VRAM (recommended) or CPU (slower).

Software: Python 3.8+, libraries in requirements.txt.

Troubleshooting
403 Forbidden Error: Ensure you’re logged in (huggingface-cli login) and have access to the model.

No GPU: Install CPU-only torch or add CUDA support: pip install torch --index-url https://download.pytorch.org/whl/cu118.

License
MIT License (LICENSE) (add a LICENSE file later).







