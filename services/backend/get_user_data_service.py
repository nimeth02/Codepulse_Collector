import requests
from config.api_config import  USER_API
from utils.errors import handle_api_response

def get_user_data_service(project_id):
    response = requests.get(
            USER_API["get_user_by_project"](project_id),
            timeout=10
        )
    handle_api_response(response)
    return response