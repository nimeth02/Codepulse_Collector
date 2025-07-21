from services.backend.get_team_data_service import get_team_data_service
from services.backend.save_team_data_service import save_team_data_service
from utils.errors import APIError


def fetch_team_data(project_id, org_name, provider):
    saved_teams = get_saved_teams(project_id)
    provider_teams = get_provider_teams(org_name, provider)

    saved_team_ids = {team["nodeId"] for team in saved_teams}
    unsaved_teams = [
        team for team in provider_teams if team["nodeId"] not in saved_team_ids
    ]

    return {"saved_teams": saved_teams, "unsaved_teams": unsaved_teams}


def get_provider_teams(org_name, provider):
    """Fetch organization teams from provider with full details"""
    project_payload = provider.get_team_data(org_name)
    # parent.provider_members=project_payload

    return project_payload


def get_saved_teams(project_id):
    """Fetch saved teams from backend API"""
    try:
        response = get_team_data_service(project_id)
        team_data = response.json()

        if team_data.get("success"):
            return team_data.get("data")
        else:
            raise APIError(
                team_data.get("message", "Failed to load teams"),
                error_code=team_data.get("errorCode", "API_ERROR"),
            )
    except Exception as e:
        raise e


def save_teams(project_id, teams):
    """Save teamss"""
    payload = {"projectId": project_id, "teams": teams}
    response = save_team_data_service(payload)
    response_data = response.json()

    if not response_data.get("success"):
        raise APIError(response_data.get("message", "Failed to save teams"))

    # # Reload updated team data
    # refreshed_data = get_saved_teams(parent)
    return {
        "saved_count": len(payload["teams"]),
        # "refreshed_data": refreshed_data
    }
    payload = {"projectId": project_id, "users": users}
