import requests
from config.api_config import  USER_API
from utils.errors import handle_api_response

def get_last_pr_data_service(repo_id):
    response = requests.get(
            USER_API["get_last_pull_requests"](repo_id),
            timeout=10
        )
    handle_api_response(response)
    return response