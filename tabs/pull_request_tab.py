from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QProgressBar,
    QMessageBox, QApplication
)
from PyQt6.QtCore import Qt
import requests
from config.api_config import USER_API, GITHUB_API
from datetime import datetime
try:
    import iso8601
except ImportError:
    iso8601 = None
    print("Warning: iso8601 module not found, using datetime fallback")

def parse_iso_date(date_str):
    """Parse ISO 8601 date with fallback if iso8601 is unavailable."""
    if iso8601:
        return iso8601.parse_date(date_str)
    else:
        try:
            for fmt in (
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S"
            ):
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            raise ValueError(f"Invalid date format: {date_str}")
        except Exception as e:
            print(f"Date parsing error: {e}")
            raise

def setup_pull_request_tab(parent):
    """Initialize the Pull Request tab."""
    print("Setting up pull request tab")
    tab = QWidget()
    main_layout = QVBoxLayout(tab)

    # Header
    header_label = QLabel("Pull Requests")
    header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    header_label.setFixedHeight(40)
    main_layout.addWidget(header_label)

    # Repository selection
    main_layout.addWidget(QLabel("Select Repository:"))
    parent.repo_combo = QComboBox()
    parent.repo_combo.addItem("Select a repository")
    parent.repo_combo.currentIndexChanged.connect(
        lambda: fetch_last_pull_request(parent)
    )
    main_layout.addWidget(parent.repo_combo)

    # Last pull request label
    parent.last_pr_label = QLabel("Last PR Created: Not fetched")
    main_layout.addWidget(parent.last_pr_label)

    # Fetch pull requests button
    parent.fetch_prs_btn = QPushButton("Fetch and Save New Pull Requests")
    parent.fetch_prs_btn.clicked.connect(lambda: fetch_and_save_new_pull_requests(parent))
    parent.fetch_prs_btn.setEnabled(False)
    main_layout.addWidget(parent.fetch_prs_btn)

    # Loading indicator
    parent.pr_progress_bar = QProgressBar()
    parent.pr_progress_bar.setVisible(False)
    main_layout.addWidget(parent.pr_progress_bar)

    # Stretch to push content up
    main_layout.addStretch()

 # Connect tab change signal
    parent.tab_widget.currentChanged.connect(
        lambda index: on_tab_changed(parent, index))

    return tab

def on_tab_changed(parent, index):
    """Load data when Pull Requests tab is selected"""
    if parent.tab_widget.tabText(index) == "Pull Requests" and parent.org_name:
        load_saved_repositories(parent)

def load_saved_repositories(parent):
    """Load saved repositories into the QComboBox."""
    try:
        parent.pr_progress_bar.setVisible(True)
        QApplication.processEvents()

        # Clear existing items
        parent.repo_combo.clear()
        parent.repo_combo.addItem("Select a repository")

        # Fetch saved repositories
        saved_repos = get_saved_repositories(parent)
        parent.saved_repos_data = saved_repos
        for repo in saved_repos:
            name = repo.get('codeRepositoryName', 'Unknown Repo')
            full_name = repo.get('fullName', 'Unknown/Unknown')
            parent.repo_combo.addItem(f"{name} ({full_name})", repo)

        parent.saved_users = get_saved_users(parent)     
        print(parent.saved_users)
    except Exception as e:
        QMessageBox.critical(parent, "Error", f"Failed to load repositories: {str(e)}")
    finally:
        parent.pr_progress_bar.setVisible(False)

def get_saved_repositories(parent):
    """Fetch saved repositories from backend API."""
    try:
        response = requests.get(
            USER_API["get_repositories"](parent.project_id),
            timeout=10
        )
        # response.raise_for_status()
        project_data = response.json()
        if project_data.get("success"):
                return project_data.get("data")
        else:
                QMessageBox.critical(
                    parent,
                    str(project_data.get("errorCode", "API_ERROR")),
                    str(project_data.get("message", "Operation failed without details"))
                )
                return []
    except Exception:
        return []

def get_saved_users(parent):
    """Fetch saved users from backend API"""
    try:
        response = requests.get(
            USER_API["get_user_by_project"](parent.project_id),
            timeout=10
        )
        project_users_data = response.json()
        # print(project_users_data.get("data"))
        if project_users_data.get("success"):
                return project_users_data.get("data")
        else:
                QMessageBox.critical(
                    parent,
                    str(project_users_data.get("errorCode", "API_ERROR")),
                    str(project_users_data.get("message", "Operation failed without details"))
                )
                return []
    except Exception:
        return []

def fetch_last_pull_request(parent):
    """Fetch the last pull request for the selected repository."""
    try:
        current_index = parent.repo_combo.currentIndex()
        if current_index <= 0:  # "Select a repository" or no selection
            parent.last_pr_label.setText("Last PR Created: Select a repository")
            parent.fetch_prs_btn.setEnabled(False)
            parent.last_pr_date = None
            parent.selected_repo_id = None
            parent.selected_repo_full_name = None
            return

        repo_data = parent.repo_combo.itemData(current_index)
        repo_id = repo_data.get('codeRepositoryId')
        full_name = repo_data.get('fullName')

        if not repo_id:
            raise ValueError("Selected repository has no codeRepositoryId")

        parent.pr_progress_bar.setVisible(True)
        QApplication.processEvents()

        response = requests.get(
            USER_API["get_last_pull_requests"](repo_id),
            timeout=10
        )
        
        # Store repository info regardless of PR status
        parent.selected_repo_id = repo_id
        parent.selected_repo_full_name = full_name

        # For other status codes, raise for error handling
        response.raise_for_status()
        last_pr = response.json().get("data")
        print(last_pr)
        if(last_pr):
        # Valid PR with 'prCreatedAt'
            if 'prCreatedAt' in last_pr:
                pr_created_at = last_pr['prCreatedAt']
                parsed_date = parse_iso_date(pr_created_at)
                parent.last_pr_label.setText(f"Last PR Created: {parsed_date.strftime('%Y-%m-%d %H:%M:%S')}")
                parent.last_pr_date = parsed_date
                parent.fetch_prs_btn.setEnabled(True)
            else:
                parent.last_pr_label.setText("Last PR Created: Invalid PR data format")
                parent.fetch_prs_btn.setEnabled(False)
                parent.last_pr_date = None
        else:
            parent.last_pr_label.setText("Last PR Created: No previous pull requests")  
            parent.fetch_prs_btn.setEnabled(True)  # Enable fetch button for new repos
            parent.last_pr_date = None
            return      

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            parent.last_pr_label.setText("Last PR Created: No previous pull requests")
            parent.fetch_prs_btn.setEnabled(True)  # Enable fetch button for new repos
        else:
            parent.last_pr_label.setText("Last PR Created: Error fetching data")
            QMessageBox.critical(parent, "API Error", f"Failed to fetch PRs (HTTP {e.response.status_code})")
            parent.fetch_prs_btn.setEnabled(False)
        parent.last_pr_date = None

    except Exception as e:
        parent.last_pr_label.setText("Last PR Created: Error fetching data")
        QMessageBox.critical(parent, "Error", f"Unexpected error: {str(e)}")
        parent.fetch_prs_btn.setEnabled(False)
        parent.last_pr_date = None

    finally:
        parent.pr_progress_bar.setVisible(False)

def fetch_and_save_new_pull_requests(parent):
    """Fetch all pull requests using GitHub GraphQL API with pagination and save to backend."""
    try:
        if not parent.selected_repo_id or not parent.selected_repo_full_name:
            QMessageBox.warning(parent, "No Repository", "No repository selected.")
            return

        parent.pr_progress_bar.setVisible(True)
        parent.fetch_prs_btn.setEnabled(False)
        QApplication.processEvents()

        token = parent.pat_input.text()
        if not token:
            raise ValueError("GitHub Personal Access Token is empty")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        filter_date = getattr(parent, 'last_pr_date', None)
        date_range = f"created:>{filter_date.strftime('%Y-%m-%d')}" if filter_date else ""
        repo_query = f"repo:{parent.selected_repo_full_name}"
        search_query = f"{repo_query} is:pr {date_range}".strip()

        new_prs = []
        has_next_page = True
        end_cursor = None

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

            response = requests.post("https://api.github.com/graphql", json=graphql_query, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            pr_nodes = data.get('data', {}).get('search', {}).get('nodes', [])
            page_info = data.get('data', {}).get('search', {}).get('pageInfo', {})
            has_next_page = page_info.get('hasNextPage', False)
            end_cursor = page_info.get('endCursor')

            for pr in pr_nodes:
                github_user_node_id = pr.get('author', {}).get('nodeId')
                user_id = None
                if hasattr(parent, 'saved_users'):
                    for user in parent.saved_users:
                        if user.get('nodeId') == github_user_node_id:
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
                    "codeRepositoryId": parent.selected_repo_id,
                    "userId": user_id,
                    "commits": pr.get('commits', {}).get('totalCount', 0),
                    "additions": pr.get('additions',0),
                    "deletions": pr.get('deletions',0),
                    "changedFiles": pr.get('changedFiles',0)
                })

        if not new_prs:
            QMessageBox.information(parent, "No PRs", "No pull requests found." if not filter_date else "No new pull requests found after the last PR date.")
            return

        print("Total PRs fetched:", len(new_prs))

        try:
            response = requests.post(USER_API["create_pull_request"], json=new_prs, timeout=10)
            response.raise_for_status()

            response_data = response.json()
            if not response_data.get("success"):
                error_msg = f"Backend save failed: {response_data.get('message', 'Unknown error')}"
                print(error_msg)
                QMessageBox.critical(parent, "Save Error", error_msg)
                return

            QMessageBox.information(parent, "Success", f"Saved {len(new_prs)} pull requests successfully")
            fetch_last_pull_request(parent)

        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP Error saving PRs: {e.response.status_code}\nResponse: {e.response.text}"
            print(error_msg)
            QMessageBox.critical(parent, "Save Error", error_msg)
        except Exception as e:
            error_msg = f"Error saving PRs: {str(e)}"
            print(error_msg)
            QMessageBox.critical(parent, "Save Error", error_msg)
            return

    except requests.exceptions.HTTPError as e:
        show_api_error(parent, "Failed to fetch or save pull requests", e)
    except Exception as e:
        QMessageBox.critical(parent, "Error", f"Unexpected error: {str(e)}")
    finally:
        parent.pr_progress_bar.setVisible(False)
        parent.fetch_prs_btn.setEnabled(True)


def show_api_error(parent, context, exception):
    """Show formatted API error message."""
    error_msg = f"{context}\n"
    if hasattr(exception, 'response'):
        error_msg += f"Status: {exception.response.status_code}\n"
        if exception.response.text:
            error_msg += f"Details: {exception.response.text[:200]}..."
    else:
        error_msg += str(exception)
    
    QMessageBox.critical(parent, "API Error", error_msg)
