from services.backend.save_user_data_service import save_user_data_service 
from services.backend.get_user_data_service import get_user_data_service
from utils.errors import  APIError

def fetch_user_data(project_id, org_name, provider):
    """Load saved and provider users, and filter unsaved ones"""
    saved_users = get_saved_users(project_id)
    provider_members = get_provider_members(org_name,provider)

    unsaved_members = [
            m for m in provider_members
            if m["nodeId"] not in [user['nodeId'] for user in saved_users]
        ]

    return {
        "saved_users": saved_users,
        "unsaved_members": unsaved_members,
    }

def get_saved_users(project_id):
    """Fetch saved users from backend API"""
    try:
        response = get_user_data_service(project_id)
        user_data = response.json()
        print(user_data)
        if user_data.get("success"):
            return user_data.get("data")
        else:
            raise APIError(
                user_data.get("message", "Failed to load users"),
                error_code=user_data.get("errorCode", "API_ERROR")
            )
    except Exception as e:
        raise e


def get_provider_members(org_name,provider):
    """Fetch saved users from provider API"""
    project_payload = provider.get_user_data(org_name)
    # parent.provider_members=project_payload  
    return project_payload

def save_users(project_id, users):
    """Save users"""
            # response = save_user_data_service(payload)
        # response_data = response.json()

        # if not response_data.get("success"):
        #     raise APIError(response_data.get("message", "Failed to save users"))

        # # After saving, reload users
        
        # # saved_users = get_saved_users(parent)
        # # provider_members = get_provider_members(parent)
        # # unsaved_members = [
        # #     m for m in provider_members
        # #     if m["nodeId"] not in [user['nodeId'] for user in saved_users]
        # # ]

        # return {
        #     # "saved_users": saved_users,
        #     # "unsaved_members": unsaved_members,
        #     "saved_count": len(payload["users"])
        # }
    payload = {"projectId": project_id, "users": users}
    response = save_user_data_service(payload)
    result = response.json()

    if not result.get("success"):
        raise APIError(result.get("message", "Failed to save users"))

    return {"saved_count": len(users)}
