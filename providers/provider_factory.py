from enum import Enum
from typing import Optional
from .base_provider import SourceControlProvider
from .github_provider import GitHubProvider
from .azure_devops_provider import AzureDevOpsProvider

class ProviderType(Enum):
    """Enum for supported source control providers."""
    GITHUB = "github"
    AZURE_DEVOPS = "azure_devops"

class ProviderFactory:
    """Factory class for creating source control providers."""
    
    @staticmethod
    def create_provider(provider_type: ProviderType,org_name:str, token: str) -> SourceControlProvider:
        """
        Create a source control provider instance.
        
        Args:
            provider_type: Type of provider to create
            token: Authentication token for the provider
            
        Returns:
            Instance of the requested provider
            
        Raises:
            ValueError: If provider_type is not supported
        """
        if provider_type == ProviderType.GITHUB:
            return GitHubProvider(org_name,token)
        elif provider_type == ProviderType.AZURE_DEVOPS:
            return AzureDevOpsProvider(org_name,token)
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")
   