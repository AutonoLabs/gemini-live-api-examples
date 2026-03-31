from firebase_functions import https_fn, options
from google import genai
import os

@https_fn.on_call() # Or use on_request if you want a standard REST endpoint
def get_ephemeral_token(req: https_fn.Request) -> https_fn.Response:
    # Set CORS for your hosting domain
    if req.method == 'OPTIONS':
        return https_fn.Response(status=204, headers={'Access-Control-Allow-Origin': '*'})
        
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    try:
        # Generate the ephemeral token for the Live API
        response = client.models.create_ephemeral_token(
            model="gemini-2.0-flash-exp" # Or the model used in the example
        )
        return https_fn.Response(
            response.token, 
            status=200, 
            headers={'Access-Control-Allow-Origin': '*'}
        )
    except Exception as e:
        return https_fn.Response(str(e), status=500)