import requests
from config.api_config import  USER_API
from utils.errors import handle_api_response

def get_code_repository_data_service(project_id):
    response = requests.get(
            USER_API["get_repositories"](project_id),
            timeout=10
        )
    handle_api_response(response)
    return response