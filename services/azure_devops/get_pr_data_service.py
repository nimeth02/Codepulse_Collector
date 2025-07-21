import requests
from config.api_config import AZURE_DEVOPS_API
from utils.errors import handle_azure_error,AzureAPIError
from utils.hash import hash_id

def get_pr_data_service(self, saved_users, repo_data, filter_date) -> list[str]:
    try:
        org_name = self.org_name
        parts = org_name.split('/')
        if len(parts) != 2:
            raise ValueError("Azure DevOps organization name must be in format 'organization/project'")
        
        organization, project = parts
        all_prs = []
        
        # Fetch both opened and closed PRs
        for pr_type, api_key in [("Opened", "get_pull_requests_with_criteria_opened"), ("Closed", "get_pull_requests_with_criteria_closed")]:
            skip = 0
            top = 100
            has_more = True
            while has_more:
                response = requests.get(
                    AZURE_DEVOPS_API[api_key](
                        organization,
                        project,
                        repo_data.get('nodeId'),
                        "all",
                        filter_date
                    ) + f"&$skip={skip}&$top={top}",
                    headers=self.headers,
                    timeout=10000
                )
                if response.status_code != 200:
                    handle_azure_error(response, f"Organization '{org_name}' ({pr_type})")
                pr_data = response.json().get("value", [])
                if not pr_data:
                    has_more = False
                    break
                current_batch = []
                for pr in pr_data:
                    azure_user_id = pr.get('createdBy', {}).get('id')
                    user_id = None
                    for user in saved_users:
                        if user.get('nodeId') == hash_id(azure_user_id):
                            user_id = user.get('userId')
                            break
                    pr_status = pr.get('status')
                    merge_status = pr.get('mergeStatus')
                    closed_date = pr.get('closedDate')
                    pr_merged_at = closed_date if pr_status == "completed" and merge_status == "succeeded" else None
                    current_batch.append({
                        "nodeId": str(pr.get('pullRequestId')),
                        "number": pr.get('pullRequestId'),
                        "state": pr_status,
                        "prCreatedAt": pr.get('creationDate'),
                        "prUpdatedAt": pr.get('creationDate'),
                        "prMergedAt": pr_merged_at,
                        "prClosedAt": closed_date,
                        "codeRepositoryId": repo_data.get('codeRepositoryId'),
                        "projectId": repo_data.get('projectId'),
                        "userId": user_id,
                        "commits": 0,
                        "additions": 0,
                        "deletions": 0,
                        "changedFiles": 0
                    })
                all_prs.extend(current_batch)
                skip += top
        return all_prs
    except requests.exceptions.RequestException as e:
        raise AzureAPIError(
            "Failed to connect to Azure DevOps API",
            str(e)
        )
# def get_pr_data_service(self,saved_users,repo_data,filter_date)  -> list[str]:
#         try:
#             org_name=self.org_name
#             parts = org_name.split('/')
#             if len(parts) != 2:
#                 raise ValueError("Azure DevOps organization name must be in format 'organization/project'")
            
#             organization, project = parts
#             response = requests.get(
#                 AZURE_DEVOPS_API["get_pull_requests_with_criteria"](organization,project,repo_data.get('nodeId'),"all",filter_date),
#                 headers=self.headers,
#                 timeout=10000
#             )

#             if response.status_code != 200:
#                 handle_azure_error(response, f"Organization '{org_name}'")
       
#             pr_data = response.json()["value"]
#             new_prs = []
            
#             for pr in pr_data:
#                 azure_user_id = pr.get('createdBy', {}).get('id')
#                 user_id = None
               
#                 for user in saved_users:
#                     if user.get('nodeId') == azure_user_id:
#                         user_id = user.get('userId')
#                         break

#                 pr_status = pr.get('status')
#                 merge_status = pr.get('mergeStatus')
#                 closed_date = pr.get('closedDate')

#                 # Infer mergedAt only if PR is completed and mergeStatus is succeeded
#                 pr_merged_at = closed_date if pr_status == "completed" and merge_status == "succeeded" else None

#                 new_prs.append({
#                     "nodeId": str(pr.get('pullRequestId')),
#                     "number": pr.get('pullRequestId'),
#                     "state": pr_status,
#                     "prCreatedAt": pr.get('creationDate'),
#                     "prUpdatedAt": pr.get('creationDate'),  # Azure DevOps doesn't have a separate updatedAt field
#                     "prMergedAt": pr_merged_at,
#                     "prClosedAt": closed_date,
#                     "codeRepositoryId": repo_data.get('codeRepositoryId'),
#                     "userId": user_id,
#                     "commits": 0,       # Azure DevOps doesn't provide commit count in this response
#                     "additions": 0,     # Azure DevOps doesn't provide additions in this response
#                     "deletions": 0,     # Azure DevOps doesn't provide deletions in this response
#                     "changedFiles": 0   # Azure DevOps doesn't provide changed files count in this response
#                 })
#             return new_prs
        
#         except requests.exceptions.RequestException as e:
#                 raise AzureAPIError(
#                     "Failed to connect to Azure DevOps API",
#                     str(e)
#                 )