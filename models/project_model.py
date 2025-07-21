from services.backend.save_organization_data_service import save_organization_data_service 
from providers import ProviderFactory
from utils.errors import show_error_message, InputValidationError, APIError

def fetch_project_data(provider_type, org_name, pat):
    """Load saved and provider users, and filter unsaved ones"""
    provider = ProviderFactory.create_provider(provider_type, org_name, pat)
    project_payload = provider.get_organization_data(org_name)

    response = save_organization_data_service(project_payload)
    response_data = response.json()

    if not response_data.get("success"):
            raise APIError(
                response_data.get("message", "Failed to save organization"),
                error_code=response_data.get("errorCode", "API_ERROR")
            )

    return {
            "provider": provider,
            "project_id": response_data.get("data", {}).get("projectId"),
            "org_name": org_name
        }