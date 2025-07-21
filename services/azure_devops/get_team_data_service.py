import requests
from config.api_config import AZURE_DEVOPS_API
from utils.errors import handle_azure_error,AzureAPIError

def get_team_data_service(self, org_name: str) -> list[str]:
        try:
            
            parts = org_name.split('/')
            if len(parts) != 2:
                raise ValueError("Azure DevOps organization name must be in format 'organization/project'")
            
            organization, project = parts
            response = requests.get(
                AZURE_DEVOPS_API["get_org_teams"](organization,project),
                headers=self.headers,
                timeout=10000
            )

            if response.status_code != 200:
                handle_azure_error(response, f"Organization '{org_name}'")
       
            teams = []
            teams_response = response.json()["value"]
            
            # Format team data to match repository data format
            for team in teams_response:
                team_data = {
                    "nodeId": team.get("id"),
                    "teamName": team.get("name"),
                    "description": team.get("description", "")
                }
                teams.append(team_data)
               
            return teams 
        
        except requests.exceptions.RequestException as e:
                raise AzureAPIError(
                    "Failed to connect to Azure DevOps API",
                    str(e)
                )