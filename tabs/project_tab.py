from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
import requests
import json
from datetime import datetime, timezone
from config.api_config import GITHUB_API, USER_API

def setup_project_tab(parent):
    """Set up the Project/Organization tab with all functionality."""
    tab = QWidget()
    layout = QVBoxLayout(tab)

    # Header
    header_label = QLabel("GitHub Organization Fetcher")
    header_label.setObjectName("headerLabel")
    header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(header_label)

    # PAT input
    layout.addWidget(QLabel("GitHub Personal Access Token:"))
    parent.pat_input = QLineEdit()
    parent.pat_input.setPlaceholderText("Enter your GitHub PAT")
    parent.pat_input.setEchoMode(QLineEdit.EchoMode.Password)
    parent.pat_input.setToolTip("Enter a GitHub PAT with 'read:org' scope")
    layout.addWidget(parent.pat_input)

    # Organization input
    layout.addWidget(QLabel("Organization Name:"))
    parent.org_input = QLineEdit()
    parent.org_input.setPlaceholderText("e.g., codefusionuom")
    parent.org_input.setToolTip("Enter the GitHub organization name")
    layout.addWidget(parent.org_input)

    # Buttons layout
    button_layout = QHBoxLayout()
    parent.fetch_btn = QPushButton("Fetch & Save")
    parent.fetch_btn.setToolTip("Fetch organization data and members")
    parent.fetch_btn.clicked.connect(lambda: fetch_organization(parent))
    button_layout.addWidget(parent.fetch_btn)

    parent.clear_btn = QPushButton("Clear")
    parent.clear_btn.setObjectName("clearButton")
    parent.clear_btn.setToolTip("Clear inputs")
    parent.clear_btn.clicked.connect(lambda: clear_organization_fields(parent))
    button_layout.addWidget(parent.clear_btn)
    layout.addLayout(button_layout)

    # Loading indicator
    parent.org_progress_bar = QProgressBar()
    parent.org_progress_bar.setRange(0, 0)
    parent.org_progress_bar.setVisible(False)
    layout.addWidget(parent.org_progress_bar)

    layout.addStretch()
    return tab

def clear_organization_fields(parent):
    """Clear inputs in the Organization tab."""
    parent.pat_input.clear()
    parent.org_input.clear()
    parent.org_members = []
    parent.org_name = ""
    if hasattr(parent, 'clear_users_fields'):
        parent.clear_users_fields()
    if hasattr(parent, 'clear_teams_fields'):
        parent.clear_teams_fields()

def fetch_organization(parent):
    """Fetch organization details and members, then populate Users and Teams tabs."""
    pat = parent.pat_input.text().strip()
    org_name = parent.org_input.text().strip()

    # Input validation
    if not pat:
        QMessageBox.warning(parent, "Missing Input", "Please enter your GitHub Personal Access Token.")
        return
    if not org_name:
        QMessageBox.warning(parent, "Missing Input", "Please enter the organization name.")
        return

    # UI state management
    parent.fetch_btn.setEnabled(False)
    parent.clear_btn.setEnabled(False)
    parent.org_progress_bar.setVisible(True)
    QApplication.processEvents()

    try:
        headers = {
            "Authorization": f"Bearer {pat}", 
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"  # Recommended by GitHub
        }

        # 1. GitHub API Request
        org_response = requests.get(
            GITHUB_API["get_org_details"](org_name),
            headers=headers,
            timeout=10
        )
        
        # Handle GitHub API errors
        try:
            org_response.raise_for_status()
            org_data = org_response.json()
        except requests.exceptions.HTTPError as gh_err:
            error_msg = f"GitHub API Error ({gh_err.response.status_code})"
            if gh_err.response.headers.get('Content-Type', '').startswith('application/json'):
                error_details = gh_err.response.json().get('message', 'Unknown error')
                error_msg += f": {error_details}"
            QMessageBox.critical(parent, "GitHub Error", error_msg)
            return

        # 2. Prepare payload for local API
        project_payload = {
            "projectName": org_data.get("login", org_name),
            "nodeId": org_data.get("node_id", f"node-{org_name}"),
            "avatarUrl": org_data.get("avatar_url", ""),
            "displayName": org_data.get("name", org_data.get("login", org_name)),
            "projectCreatedAt": org_data.get("created_at", datetime.utcnow().isoformat() + "Z"),
            "projectUpdatedAt": org_data.get("updated_at", datetime.utcnow().isoformat() + "Z")
        }

        # 3. Local API Request
        post_response = requests.post(
            USER_API["create_project"],
            json=project_payload
        )
        
        # Handle local API response
        try:
            # post_response.raise_for_status()
            project_data = post_response.json()
            
            if not isinstance(project_data, dict):
                raise ValueError("Invalid response format from local API")
                
            if project_data.get("success"):
                parent.project_id = project_data.get("data", {}).get("projectId")
                print(f"Project ID: {parent.project_id}")
                parent.org_name = org_name
                QMessageBox.information(
                    parent, 
                    "Success", 
                    f"Project data for {org_name} saved successfully"
                )
            else:
                QMessageBox.critical(
                    parent,
                    str(project_data.get("errorCode", "API_ERROR")),
                    str(project_data.get("message", "Operation failed without details"))
                )
                
        except requests.exceptions.HTTPError as local_err:
            error_msg = "Local API Error"
            if local_err.response.headers.get('Content-Type', '').startswith('application/json'):
                error_data = local_err.response.json()
                error_msg = error_data.get("message", error_msg)
            QMessageBox.critical(
                parent,
                "Local API Error",
                f"{error_msg} (Status: {local_err.response.status_code})"
            )
            
    except requests.exceptions.RequestException as e:
        QMessageBox.critical(
            parent,
            "Connection Error",
            f"Network operation failed: {str(e)}"
        )
        
    except json.JSONDecodeError:
        QMessageBox.critical(
            parent,
            "Data Error",
            "Received invalid JSON response from server"
        )
        
    except Exception as e:
        QMessageBox.critical(
            parent,
            "Unexpected Error",
            f"An unexpected error occurred: {str(e)}"
        )
        
    finally:
        # Clean up UI state
        parent.org_progress_bar.setVisible(False)
        parent.fetch_btn.setEnabled(True)
        parent.clear_btn.setEnabled(True)