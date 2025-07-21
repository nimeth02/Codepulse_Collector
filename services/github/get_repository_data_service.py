import requests
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from config.api_config import GITHUB_API
from utils.errors import handle_github_error,GitHubAPIError

def get_repository_data_service(self,org_name: str) -> List[Dict[str, Any]]:
        try:
            print("---------",self)
            response = requests.get(
                    GITHUB_API["get_org_repos"](org_name),
                    headers=self.headers,
                    timeout=100
                )
            if response.status_code != 200:
                handle_github_error(response, f"Organization '{org_name}'")

            repos = response.json()
            
            # Transform the repository data to include only the required fields
            transformed_repos = [
                {
                    "nodeId": repo['node_id'],
                    "codeRepositoryName": repo['name'],
                    "fullName": repo['full_name']
                }
                for repo in repos
            ]
               
            return transformed_repos        
           
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(
                "Failed to connect to GitHub API",
                str(e)
            )        
        
