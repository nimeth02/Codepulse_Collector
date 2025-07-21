from services.backend.save_team_members_data_service import (
    save_team_members_data_service,
)
from services.backend.get_team_member_data_service import get_team_member_data_service
from models.user_model import get_saved_users
from models.team_model import get_saved_teams
from utils.errors import  APIError


def fetch_team_member_data(project_id, org_name, provider):
    saved_teams = get_saved_teams(project_id)
    available_users = get_saved_users(project_id)
    return {
            "saved_teams": saved_teams,
            "available_users": available_users,
        }

def fetch_team_members(project_id,team):
    teamName = team.get("teamName")
    team_id = team.get("teamId")
    if not team_id:
            raise ValueError("Selected team has no teamId")

    team_members = get_team_members(team_id)
    available_users = get_saved_users(project_id)

    return {
            "team": team,
            "team_members": team_members,
            "available_users": available_users,
        }

def get_team_members(team_id):
    """Fetch team members from backend API."""
    try:
        response = get_team_member_data_service(team_id)

        team_member_data = response.json()
        if team_member_data.get("success"):
            return team_member_data.get("data")
        else:
            raise APIError(
                team_member_data.get("message", "Failed to load teams"),
                error_code=team_member_data.get("errorCode", "API_ERROR"),
            )
    except Exception as e:
        raise e        

def save_team_members(payload):
    """Saves team members using backend API."""
    response = save_team_members_data_service(payload)
    return response.json()
