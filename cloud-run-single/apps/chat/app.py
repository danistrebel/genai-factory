import os
import logging
from flask import Flask, request, jsonify

# Import the Vertex AI SDK - ADC is handled automatically!
from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
import google.api_core.exceptions

from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    Image,
    Part,
    SafetySetting,
)

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# --- Configuration (read from environment variables) ---
try:
    PROJECT_ID = os.environ['GOOGLE_CLOUD_PROJECT'] # Automatically set by Cloud Run
    REGION = os.environ.get('VERTEX_AI_REGION', 'europe-west1') # Default if not set
    # Example using a common text generation model.
    # You might want to make this configurable via env var too.
    MODEL_ENDPOINT_ID = os.environ.get('VERTEX_MODEL_ENDPOINT_ID', 'gemini-2.0-flash')
    # If using a deployed Endpoint instead of a foundation model:
    # ENDPOINT_ID = os.environ.get('VERTEX_ENDPOINT_ID') # e.g., projects/../endpoints/..

except KeyError as e:
    logging.error(f"Missing required environment variable: {e}")
    # Handle missing configuration appropriately (e.g., exit or raise)
    # For Cloud Run, GOOGLE_CLOUD_PROJECT is usually set automatically.
    raise SystemExit(f"Environment variable {e} not set.")

# --- Initialize Vertex AI Client ---
# ADC is used automatically by the client library when no credentials
# are explicitly provided. It will use the Cloud Run service account.
try:
    logging.info(f"Initializing Vertex AI client for project={PROJECT_ID}, region={REGION}")
    aiplatform.init(project=PROJECT_ID, location=REGION)
    logging.info("Vertex AI client initialized successfully.")

    # Prepare Vertex AI Endpoint reference (for prediction)
    # Use this line if you are calling a specific *deployed* Endpoint resource
    # endpoint = aiplatform.Endpoint(ENDPOINT_ID)

    # Use this line if you are calling a *pre-trained model* directly (like PaLM/Gemini)
    # Replace with appropriate class if using Gemini (e.g., GenerativeModel)
    model = GenerativeModel(MODEL_ENDPOINT_ID)
    logging.info(f"Loaded Vertex AI model: {MODEL_ENDPOINT_ID}")

except Exception as e:
    logging.error(f"Error initializing Vertex AI Client or loading model: {e}", exc_info=True)
    # Decide how to handle this - maybe the app can't start
    raise SystemExit(f"Failed to initialize Vertex AI: {e}")


# --- Flask Routes ---
@app.route('/')
def index():
    """Basic health check / info endpoint."""
    return jsonify({
        "message": "Vertex AI ADC Sample App is running.",
        "project_id": PROJECT_ID,
        "region": REGION,
        "model_endpoint_id": MODEL_ENDPOINT_ID
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint to make a prediction using Vertex AI."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    prompt = data.get('prompt')

    if not prompt:
        return jsonify({"error": "Missing 'prompt' in request body"}), 400

    logging.info(f"Received prediction request with prompt: '{prompt[:50]}...'") # Log truncated prompt

    try:
        # --- Call Vertex AI API ---
        # Define parameters (adjust as needed)
        parameters = GenerationConfig(
            temperature=0.9,
            top_p=1.0,
            top_k=32,
            candidate_count=1,
            max_output_tokens=8192,
        )

        # Make the prediction call using the loaded model
        response = model.generate_content(prompt, generation_config=parameters)

        # --- Process Response ---
        prediction_text = response.text # Adapt based on the exact model/response structure
        logging.info(f"Successfully received prediction from Vertex AI.")

        return jsonify({
            "prompt": prompt,
            "prediction": prediction_text
        })

    # Example using a deployed Endpoint instead:
    # try:
    #     # --- Call Vertex AI API (Deployed Endpoint Example) ---
    #     # Structure your instance based on your deployed model's expected input format
    #     instances = [json_format.ParseDict({"prompt": prompt}, Value())]
    #     parameters_dict = { # Optional parameters for the endpoint
    #         "temperature": 0.2,
    #         "maxOutputTokens": 256
    #     }
    #     parameters = json_format.ParseDict(parameters_dict, Value())

    #     logging.info(f"Sending request to Vertex AI Endpoint: {endpoint.resource_name}")
    #     response = endpoint.predict(instances=instances, parameters=parameters)
    #     logging.info("Successfully received prediction from Vertex AI Endpoint.")

    #     # --- Process Response (Endpoint Example) ---
    #     # The response structure depends heavily on how your model outputs results.
    #     # This is a generic example assuming a 'predictions' list with text content.
    #     if response.predictions:
    #         # You might need to parse the prediction content further
    #         prediction_result = json_format.MessageToDict(response.predictions[0])
    #         # Adjust the key based on your model's output signature
    #         prediction_text = prediction_result.get('content', 'No content found')
    #     else:
    #         prediction_text = "No prediction returned from the endpoint."

    #     return jsonify({
    #         "prompt": prompt,
    #         "prediction": prediction_text
    #     })

    except google.api_core.exceptions.GoogleAPIError as e:
        logging.error(f"Vertex AI API call failed: {e}", exc_info=True)
        # Provide more specific error details if possible
        error_details = f"Vertex AI API error: {e.message} (Code: {e.code})"
        status_code = e.code if isinstance(e.code, int) and 400 <= e.code < 600 else 500
        return jsonify({"error": "Failed to get prediction from Vertex AI", "details": error_details}), status_code
    except Exception as e:
        logging.error(f"An unexpected error occurred during prediction: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred"}), 500

if __name__ == '__main__':
    # Get port from environment variable or default to 8080
    port = int(os.environ.get('PORT', 8080))
    # Run development server (for local testing only)
    # Use Gunicorn in Dockerfile for production
    app.run(debug=False, host='0.0.0.0', port=port)
