import requests
from config.api_config import AZURE_DEVOPS_API
from utils.errors import handle_azure_error,AzureAPIError

def get_repository_data_service(self, org_name: str) -> list[str]:
        try:
            
            parts = org_name.split('/')
            if len(parts) != 2:
                raise ValueError("Azure DevOps organization name must be in format 'organization/project'")
            
            organization, project = parts
            response = requests.get(
                AZURE_DEVOPS_API["get_org_repos"](organization,project),
                headers=self.headers,
                timeout=10000
            )

            if response.status_code != 200:
                handle_azure_error(response, f"Organization '{org_name}'")
       
            repos = []
            repos_response = response.json()["value"]
            
            # Format team data to match repository data format
            for repo in repos_response:
                repo_data = {
                    "nodeId": repo.get("id"),
                    "codeRepositoryName": repo.get("name"),
                    "fullName": project+"/"+repo.get("name", "")
                }
                repos.append(repo_data)
               
            return repos 
        
        except requests.exceptions.RequestException as e:
                raise AzureAPIError(
                    "Failed to connect to Azure DevOps API",
                    str(e)
                )