import requests
from config.api_config import AZURE_DEVOPS_API
from utils.errors import handle_azure_error,AzureAPIError
from utils.hash import hash_id

def get_user_data_service(self, org_name: str) -> list[str]:
        try:
            
            parts = org_name.split('/')
            if len(parts) != 2:
                raise ValueError("Azure DevOps organization name must be in format 'organization/project'")
            
            organization, project = parts
            response = requests.get(
                AZURE_DEVOPS_API["get_org_members"](organization),
                headers=self.headers,
                timeout=10000
            )

            if response.status_code != 200:
                handle_azure_error(response, f"Organization '{org_name}'")
       
            users=[]
            users_response=response.json()
            for user in users_response['members']:
                user_details = {
                                "userName": user.get("user").get("directoryAlias"),  
                                "nodeId": hash_id(user.get("id")), 
                                "avatarUrl": user.get("user").get("_links").get("avatar").get("href"),  
                                "displayName": user.get("user").get("displayName"),  
                                "userCreatedAt": user.get("dateCreated"),  
                                "userUpdatedAt": user.get("lastAccessedDate") 
                            }
                if user_details:
                    users.append(user_details)
               
            return users 
        
        except requests.exceptions.RequestException as e:
                raise AzureAPIError(
                    "Failed to connect to Azure DevOps API",
                    str(e)
                )