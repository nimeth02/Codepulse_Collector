from presenters.user_presenter import load_user_data
from presenters.team_presenter import load_team_data
from presenters.team_member_presenter import load_team_member_data
from presenters.code_repository_presenter import load_repos_data
from presenters.pull_request_presenter import load_pull_request_data

TAB_LOADERS = {
    "Users": load_user_data,
    "Teams": load_team_data,
    "Team Members":load_team_member_data,
    "Repositories":load_repos_data,
    "Pull Requests":load_pull_request_data
}