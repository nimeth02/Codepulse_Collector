from models.code_repository_model import get_saved_code_repositories
from services.backend.get_last_pr_data_service import get_last_pr_data_service
from services.backend.save_pr_data_service import save_pr_data_service
from models.user_model import get_saved_users
from utils.errors import APIError


def fetch_pull_request_data(project_id, org_name, provider):
    """Load saved and provider users, and filter unsaved ones"""
    saved_repos = get_saved_code_repositories(project_id)
    saved_users = get_saved_users(project_id)
    return {"saved_repos": saved_repos, "saved_users": saved_users}


def fetch_last_pr_data(repo_id):
    response = get_last_pr_data_service(repo_id)
    response.raise_for_status()
    return response.json().get("data")


def fetch_and_save_pull_requests(
    current_provider, saved_users, selected_repo_data, filter_date
):
    pr_payload = current_provider.get_pr_data(
        saved_users, selected_repo_data, filter_date
    )

    if not pr_payload:
        return {"pr_payload": [], "response": None}

    response = save_pr_data_service(pr_payload)
    return {"pr_payload": pr_payload, "response": response}
