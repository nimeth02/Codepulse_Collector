import requests
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from config.api_config import GITHUB_API
from utils.errors import handle_github_error,GitHubAPIError

def get_team_slug_data_service(self,org_name: str) -> Dict[str, Any]:
        try:
            print(self.headers)
            response = requests.get(
                GITHUB_API["get_org_teams"](org_name),
                headers=self.headers,
                timeout=10
            ) 
            if response.status_code != 200:
                handle_github_error(response, f"Organization '{org_name}'")

            teams = []
            teams_response=response.json()

            for team in teams_response:
                team_data = {
                    "nodeId": team.get("node_id"),
                    "teamName": team.get("teamName"),
                    "description": team.get("description", "")
                }
                teams.append(team_data)
               
            return teams        
           
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(
                "Failed to connect to GitHub API",
                str(e)
            )        
        
