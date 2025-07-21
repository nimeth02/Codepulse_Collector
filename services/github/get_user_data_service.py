import requests
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from config.api_config import GITHUB_API
from utils.errors import handle_github_error,GitHubAPIError
from utils.hash import hash_id

def get_user_data_service(self,org_name: str) -> Dict[str, Any]:
        try:
            print(self.headers)
            response = requests.get(
                        GITHUB_API["get_org_members"](org_name),
                        headers=self.headers,
                        timeout=10
                    )
            if response.status_code != 200:
                handle_github_error(response, f"Organization '{org_name}'")

            users=[]
            users_logins = [member["login"] for member in response.json()]
            for username in users_logins:
                user_details = get_github_user_details(self,username)
                if user_details:
                    users.append(user_details)
               
            return users        
           
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(
                "Failed to connect to GitHub API",
                str(e)
            )        
        
def get_github_user_details(self,username):
        """Fetch detailed user info from GitHub"""
        try:
            response = requests.get(
                GITHUB_API["get_user_details"](username),
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "userName": data.get("login"),
                "nodeId": hash_id(data.get("node_id")),
                "avatarUrl": data.get("avatar_url"),
                "displayName": data.get("name") or data.get("login"),
                "userCreatedAt": data.get("created_at"),
                "userUpdatedAt": data.get("updated_at")
            }
        except Exception:
            return None 