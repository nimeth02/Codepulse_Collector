from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

class SourceControlProvider(ABC):
    """Abstract base class for source control providers."""
    
    @abstractmethod
    def __init__(self,org_name:str, token: str):
        """Initialize the provider with authentication token."""
        pass

    @abstractmethod
    def get_organization_data(self, org_name: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_user_data(self, org_name: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_team_data(self,org_name:str) -> Dict[str,Any]:
        pass

    @abstractmethod
    def get_repository_data(self,org_name:str) -> Dict[str,Any]:
        pass

    @abstractmethod
    def get_pr_data(self,saved_users,repo_data,filter_date) -> Dict[str,Any]:
        pass

    @abstractmethod
    def get_team_members_data(self,teamName:str,teamId:str) -> Dict[str,Any]:
        pass