from services.backend.get_code_repository_data_service import get_code_repository_data_service
from utils.errors import APIError
from services.backend.save_code_repository_data_service import (
    save_code_repository_data_service,
)

def fetch_code_repository_data(project_id, org_name, provider):
    """Load saved and provider repositories, and filter unsaved ones."""
    saved_repos = get_saved_code_repositories(project_id)
    provider_repos = get_provider_repositories(org_name, provider)

    saved_node_ids = {repo.get("nodeId") for repo in saved_repos if repo.get("nodeId")}

    unsaved_repos = [
        repo for repo in provider_repos
        if repo.get("nodeId") not in saved_node_ids
    ]

    return {
        "saved": saved_repos,
        "unsaved": unsaved_repos
    }

def get_saved_code_repositories(project_id):
    """Fetch saved repositories from backend API."""
    try:
        response = get_code_repository_data_service(project_id)
        repo_data = response.json()

        if repo_data.get("success"):
            return repo_data.get("data")
        else:
            raise APIError(
                repo_data.get("message", "Failed to load repositories"),
                error_code=repo_data.get("errorCode", "API_ERROR")
            )

    except Exception as e:
        raise e


def get_provider_repositories(org_name, provider):
    """Fetch repositories from  provider API."""
    try:
        return provider.get_repository_data(org_name)
    except Exception as e:
        raise APIError(f"Failed to fetch provider repositories: {str(e)}")  

def save_code_repositories(project_id, repos):
    """Save selected repositories to the backend."""
    payload = {"projectId": project_id, "codeRepositories": repos}
    print(payload)
    response = save_code_repository_data_service(payload)
    response_data = response.json()

    if not response_data.get("success"):
        raise APIError(response_data.get("message", "Failed to save repositories"))

    return {
        "saved_count": len(repos)
    }
