import requests
from config.api_config import  USER_API
from utils.errors import handle_api_response
import logging
from utils.errors import  APIError,handle_api_response

def save_organization_data_service(project_payload):
    try:
        response = requests.post(
            USER_API["create_project"],
            json=project_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        handle_api_response(response)
        return response

    except APIError as api_err:
        logging.error(f"API Error: {api_err}")
        raise

    except requests.RequestException as net_err:
        logging.exception("Network error occurred during API request")
        raise APIError("Network connection failed. Please check your internet or server.")