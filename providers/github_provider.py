import requests
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from .base_provider import SourceControlProvider
from config.api_config import GITHUB_API
from utils.errors import handle_github_error,GitHubAPIError
from services.github.get_organization_data_service import get_organization_data_service
from services.github.get_user_data_service import get_user_data_service
from services.github.get_team_data_service import get_team_data_service
from services.github.get_pr_data_service import get_pr_data_service
from services.github.get_repository_data_service import get_repository_data_service
from services.github.get_team_members_data_service import get_team_members_data_service

class GitHubProvider(SourceControlProvider):
    """GitHub implementation of the source control provider."""
    
    def __init__(self,org_name:str, token: str):
        """Initialize GitHub provider with PAT token."""
        self.token = token
        self.org_name=org_name
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    
    def get_organization_data(self, org_name: str) -> Dict[str, Any]:
 
        try:
            project_payload=get_organization_data_service(self,org_name)
             
            return project_payload
            
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(
                "Failed to connect to GitHub API",
                str(e)
            )
        
    def get_user_data(self,org_name: str) -> Dict[str, Any]:
        try:
            users=get_user_data_service(self,org_name)
  
            return users        
           
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(
                "Failed to connect to GitHub API",
                str(e)
            ) 
               
    def get_team_data(self,org_name:str) -> Dict[str,Any]:
        try:
            teams=get_team_data_service(self,org_name)
             
            return teams        
           
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(
                "Failed to connect to GitHub API",
                str(e)
            )
        
    def get_repository_data(self,org_name:str) -> Dict[str,Any]:
        try:
            print(org_name)
            repos=get_repository_data_service(self,org_name)
             
            return repos        
           
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(
                "Failed to connect to GitHub API",
                str(e)
            )
           
    def get_pr_data(self,saved_users,repo_data,filter_date) -> Dict[str,Any]:
        try:
            repos=get_pr_data_service(self,saved_users,repo_data,filter_date)
             
            return repos        
           
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(
                "Failed to connect to GitHub API",
                str(e)
            ) 
                  
    def get_team_members_data(self,teamName:str,teamId:str) -> Dict[str,Any]:
        try:
            teams=get_team_members_data_service(self,teamName)
             
            return teams        
           
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(
                "Failed to connect to GitHub API",
                str(e)
            )    