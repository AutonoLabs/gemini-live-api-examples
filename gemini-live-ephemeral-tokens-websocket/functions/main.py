from firebase_functions import https_fn
from google import genai
import datetime
import json
import logging
import os
import traceback

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@https_fn.on_request(secrets=["GEMINI_API_KEY"])
def get_ephemeral_token(req: https_fn.Request) -> https_fn.Response:
    logger.info("=== get_ephemeral_token called ===")
    logger.info(f"Request method: {req.method}")

    headers = {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"}

    if req.method == "OPTIONS":
        logger.info("Handling OPTIONS preflight")
        return https_fn.Response(status=204, headers=headers)

    api_key = os.environ.get("GEMINI_API_KEY")
    logger.info(f"GEMINI_API_KEY present: {bool(api_key)}")
    if api_key:
        logger.info(f"GEMINI_API_KEY prefix: {api_key[:8]}...")

    try:
        logger.info("Initializing genai.Client with api_version=v1alpha")
        client = genai.Client(api_key=api_key, http_options={"api_version": "v1alpha"})
        logger.info(f"google-genai version: {getattr(genai, '__version__', 'unknown')}")

        now = datetime.datetime.now(tz=datetime.timezone.utc)
        expire_time = now + datetime.timedelta(minutes=30)
        new_session_expire_time = now + datetime.timedelta(minutes=1)

        config = {
            "uses": 1,
            "expire_time": expire_time.isoformat(),
            "new_session_expire_time": new_session_expire_time.isoformat(),
            "http_options": {"api_version": "v1alpha"},
        }
        logger.info(f"Calling client.auth_tokens.create with config: {config}")

        token = client.auth_tokens.create(config=config)

        logger.info(f"Token response type: {type(token)}")
        logger.info(f"Token name present: {bool(getattr(token, 'name', None))}")

        return https_fn.Response(
            json.dumps({"token": token.name, "expires_at": expire_time.isoformat()}),
            status=200,
            headers=headers,
        )
    except Exception as e:
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Exception message: {e}")
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        return https_fn.Response(
            json.dumps({"error": str(e)}),
            status=500,
            headers=headers,
        )
