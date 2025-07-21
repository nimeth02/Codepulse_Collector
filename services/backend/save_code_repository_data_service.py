import requests
from config.api_config import  USER_API
from utils.errors import handle_api_response

def save_code_repository_data_service(payload):
    response = requests.post(
            USER_API["create_repository"],
            json=payload,
            timeout=10
        )
    handle_api_response(response)
    return response