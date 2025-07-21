# Base API URL
BASE_API_URL = "http://localhost:5113"

# User endpoints
USER_API = {
    "get_users": f"{BASE_API_URL}/api/user",
    "get_user_by_project": lambda project_id: f"{BASE_API_URL}/api/user/{project_id}",
    "create_user": f"{BASE_API_URL}/api/user",
    "create_project": f"{BASE_API_URL}/api/project",
    "get_teams": lambda project_id: f"{BASE_API_URL}/api/team/{project_id}",
    "create_team": f"{BASE_API_URL}/api/team",
    "get_team_members": lambda team_id: f"{BASE_API_URL}/api/team/{team_id}/members",
    "create_team_member": f"{BASE_API_URL}/api/team/members",
    "get_repositories": lambda project_id: f"{BASE_API_URL}/api/coderepository/{project_id}",
    "create_repository": f"{BASE_API_URL}/api/coderepository",
    "get_pull_requests": lambda repo_id: f"{BASE_API_URL}/api/pullrequest/{repo_id}",
    "get_last_pull_requests": lambda repo_id: f"{BASE_API_URL}/api/pullrequest/{repo_id}/last",
    "create_pull_request": f"{BASE_API_URL}/api/pullrequest"
}

# GitHub API endpoints
GITHUB_API = {
    "get_org_members": lambda org_name: f"https://api.github.com/orgs/{org_name}/members",
    "get_user_details": lambda username: f"https://api.github.com/users/{username}",
    "get_org_details": lambda org_name: f"https://api.github.com/orgs/{org_name}",
    "get_org_teams": lambda org_name: f"https://api.github.com/orgs/{org_name}/teams",
    "get_team_members": lambda teamName,org_name: f"https://api.github.com/orgs/{org_name}/teams/{teamName}/members",
    
    "get_org_repos": lambda org_name: f"https://api.github.com/orgs/{org_name}/repos",
    "get_pull_requests": lambda owner, repo: f"https://api.github.com/repos/{owner}/{repo}/pulls",
    "get_pull_request_details": lambda owner, repo, number: f"https://api.github.com/repos/{owner}/{repo}/pulls/{number}",
    "search_issues": lambda: "https://api.github.com/search/issues",
    "get_pull_request_more_details":"https://api.github.com/graphql"
}


AZURE_DEVOPS_API = {
    "get_org_details": lambda org_name: f"https://dev.azure.com/{org_name}/_apis/organizations?api-version=7.0",
    "get_project_details": lambda org_name, project: f"https://dev.azure.com/{org_name}/_apis/projects/{project}?api-version=7.0",
    "get_org_members": lambda org_name: f"https://vsaex.dev.azure.com/{org_name}/_apis/userentitlements?api-version=7.0",
    "get_user_details": lambda username: f"https://vssps.dev.azure.com/_apis/graph/users?api-version=7.0&subjectTypes=user&query={username}",
    "get_org_teams": lambda org_name, project: f"https://dev.azure.com/{org_name}/_apis/projects/{project}/teams?api-version=7.0",
    "get_team_members": lambda org_name, project, team_id: f"https://dev.azure.com/{org_name}/_apis/projects/{project}/teams/{team_id}/members?api-version=7.0",
    "get_org_repos": lambda org_name, project: f"https://dev.azure.com/{org_name}/{project}/_apis/git/repositories?api-version=7.0",
    "get_pull_requests": lambda org_name, project, repo: f"https://dev.azure.com/{org_name}/{project}/_apis/git/repositories/{repo}/pullrequests?api-version=7.2-preview.2",
    "get_pull_requests_with_criteria_closed": lambda org_name, project, repo, status="all", min_time=None: f"https://dev.azure.com/{org_name}/{project}/_apis/git/repositories/{repo}/pullrequests?api-version=7.2-preview.2&searchCriteria.status={status}&searchCriteria.queryTimeRangeType=Closed" + (f"&searchCriteria.minTime={min_time}" if min_time else ""),
    "get_pull_requests_with_criteria_opened": lambda org_name, project, repo, status="all", min_time=None: f"https://dev.azure.com/{org_name}/{project}/_apis/git/repositories/{repo}/pullrequests?api-version=7.2-preview.2&searchCriteria.status={status}&searchCriteria.queryTimeRangeType=Opened" + (f"&searchCriteria.minTime={min_time}" if min_time else ""),
    "get_pull_request_details": lambda org_name, project, repo, pr_id: f"https://dev.azure.com/{org_name}/{project}/_apis/git/repositories/{repo}/pullrequests/{pr_id}?api-version=7.2-preview.2"
}