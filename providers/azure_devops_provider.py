import requests
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from .base_provider import SourceControlProvider
from config.api_config import AZURE_DEVOPS_API
import base64
from utils.errors import handle_azure_error,AzureAPIError
from services.azure_devops.get_organization_data_service import get_organization_data_service
from services.azure_devops.get_user_data_service import get_user_data_service
from services.azure_devops.get_team_data_service import get_team_data_service
from services.azure_devops.get_repository_data_service import get_repository_data_service
from services.azure_devops.get_pr_data_service import get_pr_data_service
from services.azure_devops.get_team_members_data_service import get_team_members_data_service


class AzureDevOpsProvider(SourceControlProvider):
    """Azure DevOps implementation of the source control provider."""
    
    def __init__(self,org_name:str, token: str):
        """Initialize Azure DevOps provider with PAT token."""
        self.token = token
        self.org_name=org_name
        # Azure DevOps PAT requires a colon prepended before Base64 encoding
        self.pat_encoded = base64.b64encode(f":{token}".encode()).decode()
        
        self.headers = {
            "Authorization": f"Basic {self.pat_encoded}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def get_organization_data(self, org_name: str) -> Dict[str, Any]:
        try:
            project_payload=get_organization_data_service(self,org_name)
                
            return project_payload
        
        except requests.exceptions.RequestException as e:
            raise AzureAPIError(
                "Failed to connect to Azure DevOps API",
                str(e)
            )

    def get_user_data(self, org_name: str) -> list[str]:
        try:
            
            users=get_user_data_service(self,org_name)
               
            return users 
        
        except requests.exceptions.RequestException as e:
                raise AzureAPIError(
                    "Failed to connect to Azure DevOps API",
                    str(e)
                )
        
    def get_team_data(self, org_name: str) -> list[str]:
        try:
            
            teams=get_team_data_service(self,org_name)
               
            return teams 
        
        except requests.exceptions.RequestException as e:
                raise AzureAPIError(
                    "Failed to connect to Azure DevOps API",
                    str(e)
                )
        
    def get_repository_data(self,org_name:str) -> Dict[str,Any]:
        try:
            print(org_name)
            repos=get_repository_data_service(self,org_name)
             
            return repos        
           
        except requests.exceptions.RequestException as e:
                raise AzureAPIError(
                    "Failed to connect to Azure DevOps API",
                    str(e)
                )  
          
    def get_pr_data(self,saved_users,repo_data,filter_date) -> Dict[str,Any]:
        try:
            repos=get_pr_data_service(self,saved_users,repo_data,filter_date)
             
            return repos        
           
        except requests.exceptions.RequestException as e:
                raise AzureAPIError(
                    "Failed to connect to Azure DevOps API",
                    str(e)
                ) 
                   
    def get_team_members_data(self, teamName:str,teamId:str) -> list[str]:
        try:
            
            teams=get_team_members_data_service(self,teamId)
               
            return teams 
        
        except requests.exceptions.RequestException as e:
                raise AzureAPIError(
                    "Failed to connect to Azure DevOps API",
                    str(e)
                )        