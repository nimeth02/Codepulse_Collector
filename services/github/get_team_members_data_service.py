import requests
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from config.api_config import GITHUB_API
from utils.errors import handle_github_error,GitHubAPIError
from utils.hash import hash_id

def get_team_members_data_service(self,teamName: str) -> Dict[str, Any]:
        try:

            response = requests.get(
                GITHUB_API["get_org_teams"](self.org_name),
                headers=self.headers,
                timeout=10
            ) 
            if response.status_code != 200:
                handle_github_error(response, f"Organization '{self.org_name}'")


            teams_response=response.json()
            team_slug=None
            for team in teams_response:
                if team.get("name") == teamName:
                        team_slug=team.get("slug")
                        break

            response = requests.get(
                GITHUB_API["get_team_members"](team_slug,self.org_name),
                headers=self.headers,
                timeout=10
            ) 
            if response.status_code != 200:
                handle_github_error(response, f"Organization team")

            members = []
            team_member_response=response.json()
            print(team_member_response)

            for user in team_member_response:
                user_details = {
                                "userName": user.get("login"),  
                                "nodeId": hash_id(user.get("node_id")), 
                            }
                if user_details:
                    members.append(user_details)
               
            return members        
           
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(
                "Failed to connect to GitHub API",
                str(e)
            )        
        
