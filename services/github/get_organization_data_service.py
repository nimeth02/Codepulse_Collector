import requests
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from config.api_config import GITHUB_API
from utils.errors import handle_github_error,GitHubAPIError

def get_organization_data_service(self, org_name: str) -> Dict[str, Any]:
        """
        Get organization details and create standardized project payload.
        
        Args:
            org_name: Name of the organization (format may vary by provider)
            
        Returns:
            Standardized project payload for local API
            
        Raises:
            ValueError: If org_name is not in the correct format for the provider
            requests.exceptions.RequestException: If API request fails
        """
        try:
         
            # Get organization details from GitHub
            response = requests.get(
                GITHUB_API["get_org_details"](org_name),
                headers=self.headers,
                timeout=10
            )
            # print(response.json())
            
            if response.status_code != 200:
                handle_github_error(response, f"Organization '{org_name}'")
            
            org_data = response.json()
            
            # Create standardized payload
            project_payload = {
                "projectName": org_data.get("login", org_name),
                "nodeId": org_data.get("node_id"),
                "avatarUrl": org_data.get("avatar_url", ""),
                "displayName": org_data.get("name", org_data.get("login", org_name)),
                "projectCreatedAt": org_data.get("created_at", datetime.utcnow().isoformat() + "Z"),
                "projectUpdatedAt": org_data.get("updated_at", datetime.utcnow().isoformat() + "Z"),
                # "providerType": "github",
            }
            
            return project_payload
            
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(
                "Failed to connect to GitHub API",
                str(e)
            )



