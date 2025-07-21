import json
import requests
from PyQt6.QtWidgets import QMessageBox

class InputValidationError(Exception):
    """Raised when input validation fails."""
    def __init__(self, message="Invalid input provided"):
        self.message = message
        super().__init__(self.message)

class APIError(Exception):
    def __init__(self, message="API operation failed", status_code=None, error_code=None, details=None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details
        super().__init__(self.message)

class NetworkError(Exception):
    """Raised when there's a network-related error."""
    def __init__(self, message="Network operation failed", details=None):
        self.message = message
        self.details = details
        super().__init__(self.message)

# GitHub specific errors
class GitHubError(Exception):
    """Base class for GitHub-specific errors."""
    def __init__(self, message, details=None):
        self.message = message
        self.details = details
        super().__init__(self.message)

class GitHubAuthError(GitHubError):
    """Raised when there's an authentication error with GitHub."""
    pass

class GitHubRateLimitError(GitHubError):
    """Raised when GitHub API rate limit is exceeded."""
    pass

class GitHubNotFoundError(GitHubError):
    """Raised when a GitHub resource is not found."""
    pass

class GitHubAPIError(GitHubError):
    """Raised for general GitHub API errors."""
    pass

# Azure specific errors
class AzureError(Exception):
    """Base class for Azure-specific errors."""
    def __init__(self, message, details=None):
        self.message = message
        self.details = details
        super().__init__(self.message)

class AzureAuthError(AzureError):
    """Raised when there's an authentication error with Azure DevOps."""
    pass

class AzureNotFoundError(AzureError):
    """Raised when an Azure DevOps resource is not found."""
    pass

class AzureRateLimitError(AzureError):
    """Raised when Azure DevOps API rate limit is exceeded."""
    pass

class AzureAPIError(AzureError):
    """Raised for general Azure DevOps API errors."""
    pass

def show_error_message(parent, error, title="Error"):
    """Display an error message in a QMessageBox.
    
    Args:
        parent: The parent widget for the message box
        error: The error object or message string
        title: The title for the error message box
    """
    message = str(error)
    if hasattr(error, 'details') and error.details:
        message = f"{message}\n\nDetails: {error.details}"
        
    QMessageBox.critical(parent, title, message)

def validate_inputs(pat, org_name):
    """Validate the input parameters for organization fetch.
    
    Args:
        pat: Personal Access Token
        org_name: Organization name
        
    Raises:
        InputValidationError: If validation fails
    """
    if not pat:
        raise InputValidationError("Please enter your Personal Access Token")
    if not org_name:
        raise InputValidationError("Please enter the organization name")
    if len(pat) < 10:  # Basic validation for PAT length
        raise InputValidationError("Personal Access Token appears to be invalid")
    if len(org_name) < 2:  # Basic validation for org name length
        raise InputValidationError("Organization name appears to be invalid")

def handle_api_response(response: requests.Response):
    if response.status_code == 200 or response.status_code == 201:
        return

    error_msg, error_code, error_details = extract_common_api_error(response)
    raise APIError(error_msg, status_code=response.status_code, error_code=error_code, details=error_details)


def extract_common_api_error(response: requests.Response) -> tuple[str, str, dict]:
    """Extracts common error fields from a backend API response."""
    error_msg = f"API request failed with status code: {response.status_code}"
    error_code = None
    error_details = None

    try:
        data = response.json()
        error_msg = data.get("message", error_msg)
        error_code = data.get("errorCode")
        error_details = data.get("errors")

        if error_details and "$" in error_details:
            if isinstance(error_details["$"], list) and error_details["$"]:
                error_msg += f" | Detail: {error_details['$'][0]}"

    except (json.JSONDecodeError, ValueError):
        error_msg += " | Failed to parse error response."

    return error_msg, error_code, error_details

def handle_github_error(response: requests.Response, context: str) -> None:
    """Handle GitHub API error responses.
    
    Args:
        response: requests.Response object from GitHub API
        context: Description of the operation that failed
        
    Raises:
        GitHubAuthError: For authentication issues
        GitHubRateLimitError: When rate limit is exceeded
        GitHubNotFoundError: When resource is not found
        GitHubAPIError: For other GitHub API errors
    """
    if response.status_code == 401:
        raise GitHubAuthError(
            "Invalid or expired GitHub Personal Access Token",
            "Please check your token and ensure it has the required permissions"
        )
    elif response.status_code == 403:
        if "rate limit" in response.text.lower():
            raise GitHubRateLimitError(
                "GitHub API rate limit exceeded",
                "Please try again later or use a different token"
            )
        raise GitHubAuthError(
            "Insufficient permissions",
            "Your token doesn't have the required permissions for this operation"
        )
    elif response.status_code == 404:
        raise GitHubNotFoundError(
            f"Resource not found: {context}",
            "Please check if the resource exists and you have access to it"
        )
    else:
        try:
            error_data = response.json()
            error_message = error_data.get("message", "Unknown error")
            error_details = error_data.get("documentation_url", "")
            raise GitHubAPIError(
                f"GitHub API error: {error_message}",
                f"Documentation: {error_details}" if error_details else None
            )
        except ValueError:
            raise GitHubAPIError(
                f"GitHub API error (Status {response.status_code})",
                response.text[:200] if response.text else None
            )

def handle_azure_error(response: requests.Response, context: str) -> None:
    """Handle Azure DevOps API error responses.
    
    Args:
        response: requests.Response object from Azure DevOps API
        context: Description of the operation that failed
        
    Raises:
        AzureAuthError: For authentication issues
        AzureRateLimitError: When rate limit is exceeded
        AzureNotFoundError: When resource is not found
        AzureAPIError: For other Azure DevOps API errors
    """
    error_message = f"Azure DevOps API error ({response.status_code}) while {context}."
    error_details = None

    try:
        
        error_data = response.json()
        if "message" in error_data:
            error_message = error_data["message"]
        elif "value" in error_data and isinstance(error_data["value"], list) and error_data["value"]:
            # Handle cases where messages are in a 'value' list (common in Azure DevOps)
            first_error = error_data["value"][0]
            if isinstance(first_error, dict) and "message" in first_error:
                error_message = first_error["message"]
            elif isinstance(first_error, str):
                error_message = first_error # Sometimes the value list contains simple strings

        if "errorCode" in error_data:
            error_details = f"Error Code: {error_data["errorCode"]}"
        elif "typeKey" in error_data:
            error_details = f"Type Key: {error_data["typeKey"]}"
        elif "$id" in error_data and "innerException" in error_data and "message" in error_data["innerException"]:
            # This pattern is also seen in Azure DevOps errors
            error_message = error_data["innerException"]["message"]

    except (json.JSONDecodeError, KeyError):
        # Check if the response is HTML, which often indicates a redirection or authentication issue
        if 'text/html' in response.headers.get('Content-Type', '').lower():
            error_message = f"Unexpected HTML response ({response.status_code}) from Azure DevOps API."
            error_details = "This often indicates an authentication issue or redirection. Please ensure your PAT is correct and formatted properly (e.g., with a dummy username if using Basic Auth)."
        elif response.text:
            error_details = response.text[:200]  # Fallback to response text if JSON parsing fails and not HTML
    print(response.status_code)
    if response.status_code == 401:
        raise AzureAuthError(
            "Unauthorized: Invalid or expired Azure DevOps token.",
            error_details or "Please check your token and ensure it has the required permissions."
        )
    elif response.status_code == 403:
        # Broaden checks for 403 to include general forbidden/permissions issues
        if "rate limit" in (error_details or "").lower() or "throttled" in (error_details or "").lower():
            raise AzureRateLimitError(
                "Azure DevOps API rate limit exceeded.",
                error_details or "Please try again later or reduce your request frequency."
            )
        else:
            raise AzureAuthError(
                "Forbidden: Insufficient permissions or access denied for Azure DevOps operation.",
                error_details or "Your token might lack required permissions or access is denied."
            )
    elif response.status_code == 404:
        raise AzureNotFoundError(
            f"Azure DevOps resource not found: {context}.",
            error_details or "Please check if the resource exists and you have access to it."
        )
    elif response.status_code == 203:
        # Explicitly handle 203, which can sometimes appear with authentication issues
        raise AzureAuthError(
            "Non-Authoritative Information: Possible authentication redirection or invalid PAT.",
            error_details or "Ensure your PAT is correctly configured, including any dummy username for Basic Auth."
        )
    else:
        raise AzureAPIError(
            error_message,
            error_details
        )