from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QPushButton, QProgressBar,
    QMessageBox, QCheckBox, QListWidget, QListWidgetItem, QSplitter, QApplication
)
from PyQt6.QtCore import Qt
from functools import partial
import requests
from config.api_config import USER_API, GITHUB_API

def setup_repositories_tab(parent):
    """Initialize the Repositories tab with split view."""
    tab = QWidget()
    main_layout = QVBoxLayout(tab)

    # Header
    header_label = QLabel("Organization Repositories")
    header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    header_label.setFixedHeight(40)
    main_layout.addWidget(header_label)

    # Create split view
    splitter = QSplitter(Qt.Orientation.Horizontal)

    # Left panel - Saved repositories
    left_panel = QWidget()
    left_layout = QVBoxLayout(left_panel)
    left_layout.addWidget(QLabel("Saved Repositories"))
    parent.left_saved_repos_list = QListWidget()  # CHANGED: Renamed to left_saved_repos_list
    left_layout.addWidget(parent.left_saved_repos_list)
    
    # Right panel - Unsaved GitHub repositories
    right_panel = QWidget()
    right_layout = QVBoxLayout(right_panel)
    right_layout.addWidget(QLabel("Unsaved GitHub Repositories"))
    parent.right_unsaved_repos_scroll = QScrollArea()  # CHANGED: Renamed to right_unsaved_repos_scroll
    parent.right_unsaved_repos_scroll.setWidgetResizable(True)
    parent.right_unsaved_repos_widget = QWidget()
    parent.right_unsaved_repos_layout = QVBoxLayout(parent.right_unsaved_repos_widget)
    parent.right_unsaved_repos_scroll.setWidget(parent.right_unsaved_repos_widget)
    right_layout.addWidget(parent.right_unsaved_repos_scroll)
    
    # Add panels to splitter
    splitter.addWidget(left_panel)
    splitter.addWidget(right_panel)
    splitter.setSizes([300, 300])
    main_layout.addWidget(splitter)

    # Save button
    parent.save_repos_btn = QPushButton("Save Selected Repositories")
    parent.save_repos_btn.clicked.connect(lambda: save_selected_repositories(parent))
    parent.save_repos_btn.setEnabled(False)
    main_layout.addWidget(parent.save_repos_btn)

    # Loading indicator
    parent.repos_progress_bar = QProgressBar()
    parent.repos_progress_bar.setVisible(False)
    main_layout.addWidget(parent.repos_progress_bar)

    # Connect tab change signal
    parent.tab_widget.currentChanged.connect(
        lambda index: on_tab_changed(parent, index)
    )
    
    return tab

def on_tab_changed(parent, index):
    """Load data when Repositories tab is selected."""
    if parent.tab_widget.tabText(index) == "Repositories" and parent.org_name:
        load_repos_data(parent)

def load_repos_data(parent):
    """Load both saved and unsaved repositories."""
    try:
        parent.repos_progress_bar.setVisible(True)
        QApplication.processEvents()

        # Clear existing data
        clear_repos_ui(parent)

        # Load saved repositories from backend
        saved_repos = get_saved_repositories(parent)
        display_saved_repositories(parent, saved_repos)

        # Load unsaved repositories from GitHub
        unsaved_repos = get_unsaved_repositories(parent, saved_repos)
        display_unsaved_repositories(parent, unsaved_repos)

    except Exception as e:
        QMessageBox.critical(parent, "Error", f"Failed to load repositories: {str(e)}")
    finally:
        parent.repos_progress_bar.setVisible(False)

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

def display_saved_repositories(parent, repos):
    """Display saved repositories in the left panel."""  # CHANGED: Corrected docstring
    parent.left_saved_repos_list.clear()  # CHANGED: Use left_saved_repos_list
    parent.saved_repos_data = repos
    for repo in repos:
        name = repo.get('codeRepositoryName', 'Unknown Repo')
        full_name = repo.get('fullName', 'Unknown/Unknown')
        item = QListWidgetItem(f"{name} ({full_name})")
        parent.left_saved_repos_list.addItem(item)

def get_unsaved_repositories(parent, saved_repos):
    """Fetch GitHub repositories and filter out saved ones."""
    try:
        # Validate PAT and org_name
        if not hasattr(parent, 'pat_input') or not parent.pat_input.text():
            raise ValueError("GitHub Personal Access Token is not provided")
        if not parent.org_name:
            raise ValueError("Organization name is not set")
        
        # Fetch all repositories from GitHub
        github_repos = get_github_repositories(parent)
        
        
        # Get NodeIds of saved repositories, handle multiple field names
        saved_node_ids = set()
        for repo in saved_repos:
            # Try different possible field names
            node_id = repo.get('NodeId') or repo.get('nodeId') or repo.get('node_id') or ''
            if node_id:
                saved_node_ids.add(node_id)
        
        
        # Filter out saved repositories
        unsaved_repos = [
            repo for repo in github_repos
            if repo.get('node_id') not in saved_node_ids
        ]
        
        
        return unsaved_repos
    except Exception as e:
        print(f"Error fetching unsaved repositories: {str(e)}")
        return []

def get_github_repositories(parent):
    """Fetch all repositories for the organization from GitHub API."""
    try:
        token = parent.pat_input.text()       
        if not token:
            raise ValueError("GitHub Personal Access Token is empty")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
        response = requests.get(
            GITHUB_API["get_org_repos"](parent.org_name),
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching GitHub repositories: {str(e)}")
        raise

def display_unsaved_repositories(parent, repos):
    """Display unsaved repositories with checkboxes in the right panel."""  # CHANGED: Corrected docstring
    for i in reversed(range(parent.right_unsaved_repos_layout.count())):  # CHANGED: Use right_unsaved_repos_layout
        widget = parent.right_unsaved_repos_layout.itemAt(i).widget()
        if widget:
            widget.deleteLater()
    
    parent.unsaved_repos_data = repos
    for repo in repos:
        name = repo.get('name', 'Unknown Repo')
        full_name = repo.get('full_name', 'Unknown/Unknown')
        checkbox = QCheckBox(f"{name} ({full_name})")
        
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        spinner = QProgressBar()
        spinner.setRange(0, 0)
        spinner.setFixedSize(20, 20)
        spinner.setVisible(False)
        
        layout.addWidget(checkbox)
        layout.addWidget(spinner)
        layout.addStretch()
        
        node_id = repo.get('node_id')
        checkbox.stateChanged.connect(
            partial(handle_repo_checkbox_change, parent, node_id, checkbox, spinner)
        )
        
        parent.right_unsaved_repos_layout.addWidget(container)  # CHANGED: Use right_unsaved_repos_layout

def handle_repo_checkbox_change(parent, node_id, checkbox, spinner, state):
    """Handle checkbox changes for repository selection."""
    try:
        if not hasattr(parent, 'selected_repos'):
            parent.selected_repos = set()
            
        if state == Qt.CheckState.Checked.value:
            spinner.setVisible(True)
            checkbox.setEnabled(False)
            QApplication.processEvents()
            
            parent.selected_repos.add(node_id)
            spinner.setVisible(False)
            checkbox.setEnabled(True)
        else:
            parent.selected_repos.discard(node_id)
            
        parent.save_repos_btn.setEnabled(bool(parent.selected_repos))
            
    except Exception as e:
        print(f"Checkbox error: {e}")
        QMessageBox.warning(parent, "Error", f"Failed to handle selection: {str(e)}")
        spinner.setVisible(False)
        checkbox.setEnabled(True)

def save_selected_repositories(parent):
    """Save selected repositories to the backend."""
    try:
        if not parent.selected_repos:
            QMessageBox.warning(parent, "No Repositories Selected", "Please select at least one repository.")
            return

        parent.repos_progress_bar.setVisible(True)
        parent.save_repos_btn.setEnabled(False)
        QApplication.processEvents()

        payload = [
            {
                "NodeId": repo['node_id'],
                "codeRepositoryName": repo['name'],
                "fullName": repo['full_name'],
                "defaultBranch": repo['default_branch'],
                "projectId": parent.project_id
            }
            for repo in parent.unsaved_repos_data
            if repo['node_id'] in parent.selected_repos
        ]

        if not payload:
            raise ValueError("No valid repositories selected")

        response = requests.post(
            USER_API["create_repository"],
            json=payload,
            timeout=10
        )
        response.raise_for_status()

        QMessageBox.information(
            parent, 
            "Success", 
            f"Saved {len(payload)} repositories successfully"
        )
        
        load_repos_data(parent)

    except requests.exceptions.HTTPError as e:
        show_api_error(parent, "Failed to save repositories", e)
    except Exception as e:
        QMessageBox.critical(parent, "Error", f"Unexpected error: {str(e)}")
    finally:
        parent.repos_progress_bar.setVisible(False)
        parent.save_repos_btn.setEnabled(False)
        if hasattr(parent, 'selected_repos'):
            parent.selected_repos.clear()

def clear_repos_ui(parent):
    """Clear all repository UI elements."""
    parent.left_saved_repos_list.clear()  # CHANGED: Use left_saved_repos_list
    for i in reversed(range(parent.right_unsaved_repos_layout.count())):  # CHANGED: Use right_unsaved_repos_layout
        parent.right_unsaved_repos_layout.itemAt(i).widget().deleteLater()
    if hasattr(parent, 'selected_repos'):
        parent.selected_repos.clear()
    if hasattr(parent, 'saved_repos_data'):
        parent.saved_repos_data = []
    if hasattr(parent, 'unsaved_repos_data'):
        parent.unsaved_repos_data = []

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