import requests
from config.api_config import AZURE_DEVOPS_API
from utils.errors import handle_azure_error,AzureAPIError
from utils.hash import hash_id

def get_team_members_data_service(self,teamId:str) -> list[str]:
        try:
            
            parts = self.org_name.split('/')
            if len(parts) != 2:
                raise ValueError("Azure DevOps organization name must be in format 'organization/project'")
            
            organization, project = parts
            print(teamId)
            response = requests.get(
                AZURE_DEVOPS_API["get_team_members"](organization,project,teamId),
                headers=self.headers,
                timeout=10000
            )

            if response.status_code != 200:
                handle_azure_error(response, f"Organization '{self.org_name}'")
       
            members = []
            team_member_response=response.json()["value"]
            print(team_member_response)

            for user in team_member_response:
                user_details = {
                                "userName": user["identity"].get("displayName"),  
                                "nodeId": hash_id(user["identity"].get("id")), 
                            }
                if user_details:
                    members.append(user_details)

            return members 
        
        except requests.exceptions.RequestException as e:
                raise AzureAPIError(
                    "Failed to connect to Azure DevOps API",
                    str(e)
                )