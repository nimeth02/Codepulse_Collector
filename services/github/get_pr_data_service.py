import requests
from typing import List, Dict, Any
from utils.errors import GitHubAPIError
from utils.hash import hash_id

def get_pr_data_service(self,saved_users,repo_data,filter_date) -> List[Dict[str, Any]]:
        try:
            date_range = f"updated:>{filter_date.strftime('%Y-%m-%d')}" if filter_date else ""
            repo_query = f"repo:{repo_data.get('fullName')}"
            search_query = f"{repo_query} is:pr {date_range}".strip()
            new_prs = []
            has_next_page = True
            end_cursor = None

            print("-----------------------------------------------------",repo_data)

            while has_next_page:
                after_clause = f', after: "{end_cursor}"' if end_cursor else ""
                graphql_query = {
                    "query": f"""
                    query {{
                    search(query: "{search_query}", type: ISSUE, first: 100{after_clause}) {{
                        pageInfo {{
                        hasNextPage
                        endCursor
                        }}
                        nodes {{
                        ... on PullRequest {{
                            nodeId:id
                            number
                            title
                            state
                            createdAt
                            updatedAt
                            closedAt
                            mergedAt
                            additions
                            deletions
                            changedFiles
                            commits {{
                            totalCount
                            }}
                            author {{
                            login
                            ... on User {{
                                nodeId: id
                            }}
                            }}
                            url
                        }}
                        }}
                    }}
                    }}
                    """
                }

                response = requests.post("https://api.github.com/graphql", json=graphql_query, headers=self.headers, timeout=10)
                response.raise_for_status()
                data = response.json()

                pr_nodes = data.get('data', {}).get('search', {}).get('nodes', [])
                page_info = data.get('data', {}).get('search', {}).get('pageInfo', {})
                has_next_page = page_info.get('hasNextPage', False)
                end_cursor = page_info.get('endCursor')

                for pr in pr_nodes:
                    github_user_node_id = pr.get('author', {}).get('nodeId')
                    user_id = None
                   
                    for user in saved_users:
                        if user.get('nodeId') == hash_id(github_user_node_id):
                            user_id = user.get('userId')
                            break

                    new_prs.append({
                        "nodeId": pr.get('nodeId'),
                        "number": pr.get('number'),
                        "state": pr.get('state'),
                        "prCreatedAt": pr.get('createdAt'),
                        "prUpdatedAt": pr.get('updatedAt'),
                        "prMergedAt": pr.get('mergedAt'),
                        "prClosedAt": pr.get('closedAt'),
                        "codeRepositoryId": repo_data.get('codeRepositoryId'),
                        "projectId": repo_data.get('projectId'),
                        "userId": user_id,
                        "commits": pr.get('commits', {}).get('totalCount', 0),
                        "additions": pr.get('additions',0),
                        "deletions": pr.get('deletions',0),
                        "changedFiles": pr.get('changedFiles',0)
                    }) 
            return new_prs
                
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(
                "Failed to connect to GitHub API",
                str(e)
            )        
        