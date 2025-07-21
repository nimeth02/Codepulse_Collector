import requests
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from config.api_config import AZURE_DEVOPS_API
from utils.errors import handle_azure_error,AzureAPIError

def get_organization_data_service(self, org_name: str) -> Dict[str, Any]:
        try:
            """
            Get Azure DevOps organization details and create standardized project payload.
            
            Args:
                org_name: Azure DevOps organization name in format 'organization/project'
                
            Returns:
                Standardized project payload for local API
                
            Raises:
                ValueError: If organization name format is incorrect
                requests.exceptions.RequestException: If Azure DevOps API request fails
            """
            # Split organization and project name
            parts = org_name.split('/')
            if len(parts) != 2:
                raise ValueError("Azure DevOps organization name must be in format 'organization/project'")
            
            organization, project = parts
            
            # Get organization details (needed for avatar URL) and project details

            url = AZURE_DEVOPS_API["get_project_details"](organization, project)
            response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=10
                )
            if response.status_code != 200:
                    handle_azure_error(response, f"Organization '{org_name}'")
                
            project_data = response.json()
            
            # Create standardized payload
            project_payload = {
                "projectName": project_data.get("name", project),
                "nodeId": project_data.get("id", f"node-{project}"),
                "displayName": project_data.get("name", project),
                "projectCreatedAt": project_data.get("lastUpdateTime", datetime.utcnow().isoformat() + "Z"),
                "projectUpdatedAt": project_data.get("lastUpdateTime", datetime.utcnow().isoformat() + "Z"),
                # "providerType": "azure_devops"
            }
            
            return project_payload
        
        except requests.exceptions.RequestException as e:
            raise AzureAPIError(
                "Failed to connect to Azure DevOps API",
                str(e)
            )