# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os

from flask import Flask, request, render_template_string, abort

import google.auth
import google.auth.exceptions
import google.generativeai as genai

app = Flask(__name__)

# Model Name: default if not set in environment
DEFAULT_MODEL_NAME = 'gemini-1.5-flash-latest'
MODEL_NAME = os.environ.get('GEMINI_MODEL_NAME', DEFAULT_MODEL_NAME)
logging.debug(f"Using Gemini Model: {MODEL_NAME}") # Log the model being used

model = None
initialization_error = None

# ADC authentication
try:
    SCOPES = [
        'https://www.googleapis.com/auth/generative-language',
        'https://www.googleapis.com/auth/cloud-platform'
    ]

    # Explicitly get credentials using ADC, requesting specific scopes
    # This *might* influence subsequent implicit ADC lookups by google.generativeai
    credentials, project_id = google.auth.default(scopes=SCOPES)

    logging.debug("Successfully obtained scoped ADC credentials.")
    if project_id:
         logging.debug(f"Project ID determined: {project_id}")

except google.auth.exceptions.DefaultCredentialsError as e:
    logging.error(f"FATAL: Could not get default credentials. "
                  f"Ensure the Cloud Run service account exists and has permissions. Error: {e}", exc_info=True)
    # Exit or prevent app from starting if auth fails fundamentally
    raise SystemExit(f"Authentication failed: {e}")
except Exception as e:
    logging.error(f"FATAL: An unexpected error occurred during initialization: {e}", exc_info=True)
    raise SystemExit(f"Initialization failed: {e}")

# Init model
try:
    model = genai.GenerativeModel(MODEL_NAME)
    # Perform a simple test generation during init to catch auth/config issues early (optional)
    # model.generate_content("test", generation_config=genai.types.GenerationConfig(candidate_count=1))
    logging.debug(f"Successfully initialized Gemini model '{MODEL_NAME}'.")

except Exception as e:
    initialization_error = f"Error initializing Gemini model '{MODEL_NAME}': {e}. Check Service Account permissions (needs Vertex AI User role for ADC) or API key validity."
    logging.error(initialization_error)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cloud Run Gemini Demo</title>
    <style>
        body { font-family: sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: auto; }
        h1 { text-align: center; color: #333; }
        form { display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px; }
        textarea { padding: 10px; font-size: 1em; border: 1px solid #ccc; border-radius: 4px; min-height: 80px; }
        button { padding: 10px 15px; font-size: 1em; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background-color: #45a049; }
        .result { margin-top: 20px; padding: 15px; border: 1px solid #eee; background-color: #f9f9f9; border-radius: 4px; }
        .result h2 { margin-top: 0; color: #555; }
        .result pre { white-space: pre-wrap; word-wrap: break-word; background-color: #fff; padding: 10px; border: 1px solid #ddd; }
        .error { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Ask Gemini (Model: {{ model_name }})</h1>
    <form method="post">
        <label for="prompt">Enter your prompt:</label>
        <textarea id="prompt" name="prompt" required>{{ request.form.get('prompt', '') }}</textarea>
        <button type="submit">Generate Response</button>
    </form>

    {% if error %}
        <div class="result error">
            <h2>Error</h2>
            <p>{{ error }}</p>
        </div>
    {% endif %}

    {% if response_text %}
        <div class="result">
            <h2>Gemini's Response:</h2>
            <pre>{{ response_text }}</pre>
        </div>
         <hr>
         <div class="result">
            <h2>Original Prompt:</h2>
            <pre>{{ original_prompt }}</pre>
         </div>
    {% endif %}

</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    response_text = None
    original_prompt = None
    error_message = initialization_error # Use error from initialization if any

    if model is None and not error_message:
        # This case should ideally be caught by initialization_error, but as a fallback:
        error_message = "Gemini model is not available. Check server logs."

    if request.method == 'POST' and model:
        original_prompt = request.form.get('prompt')
        if not original_prompt:
            error_message = "Please enter a prompt."
        else:
            try:
                # --- Call Gemini API ---
                logging.debug(f"Sending prompt to Gemini ({MODEL_NAME}): {original_prompt[:100]}...")
                # Simple generation:
                response = model.generate_content(original_prompt)

                # More robust error checking from the response if needed:
                # See: https://ai.google.dev/tutorials/python_quickstart#safety_settings
                # if not response.candidates:
                #    error_message = "No response generated. This might be due to safety settings or other issues."
                #    # Potentially inspect response.prompt_feedback
                # else:
                #    response_text = response.text # Access text safely

                response_text = response.text # Assuming simple success case for demo
                logging.debug(f"Received response from Gemini ({MODEL_NAME}).")

            except AttributeError as e:
                 logging.error(f"Error processing Gemini response: {e}. Response object: {response}")
                 error_message = f"Could not extract text from Gemini response. Check logs. Error: {e}"
            except Exception as e:
                # Catch other potential API errors (network, permissions, quota, invalid model, etc.)
                logging.error(f"Error calling Gemini API: {e}")
                error_message = f"An error occurred while contacting the Gemini API: {e}"

    # Pass the actual model name used to the template
    return render_template_string(
        HTML_TEMPLATE,
        model_name=MODEL_NAME,
        response_text=response_text,
        original_prompt=original_prompt,
        error=error_message
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
