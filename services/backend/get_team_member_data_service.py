import requests
from config.api_config import  USER_API
from utils.errors import handle_api_response

def get_team_member_data_service(team_id):
    response = requests.get(
            USER_API["get_team_members"](team_id),
            timeout=10
        )
    handle_api_response(response)
    return response