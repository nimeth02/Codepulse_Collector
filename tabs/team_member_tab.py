from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QPushButton, QProgressBar,
    QMessageBox, QCheckBox, QListWidget, QListWidgetItem, QSplitter, QComboBox, QApplication
)
from PyQt6.QtCore import Qt
from functools import partial
import requests
from config.api_config import USER_API, GITHUB_API

def setup_team_member_tab(parent):
    """Initialize the Teams tab with split view."""
    tab = QWidget()
    main_layout = QVBoxLayout(tab)

    # Header
    header_label = QLabel("Organization Teams")
    header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    header_label.setFixedHeight(40)
    main_layout.addWidget(header_label)

    # Create split view
    splitter = QSplitter(Qt.Orientation.Horizontal)
    
    # Left panel - Saved teams and members
    left_panel = QWidget()
    left_layout = QVBoxLayout(left_panel)
    left_layout.addWidget(QLabel("Saved Teams"))
    
    # Team selection dropdown
    parent.saved_teams_combo = QComboBox()
    parent.saved_teams_combo.addItem("Select a team")
    parent.saved_teams_combo.currentIndexChanged.connect(
        lambda index: display_team_members(parent, index)
    )
    left_layout.addWidget(parent.saved_teams_combo)
    
    # Team members list
    parent.team_members_list = QListWidget()
    left_layout.addWidget(parent.team_members_list)
    
    # Right panel - Available users
    right_panel = QWidget()
    right_layout = QVBoxLayout(right_panel)
    right_layout.addWidget(QLabel("Available Users"))
    parent.available_users_scroll = QScrollArea()
    parent.available_users_scroll.setWidgetResizable(True)
    parent.available_users_widget = QWidget()
    parent.available_users_layout = QVBoxLayout(parent.available_users_widget)
    parent.available_users_scroll.setWidget(parent.available_users_widget)
    right_layout.addWidget(parent.available_users_scroll)
    
    # Add panels to splitter
    splitter.addWidget(left_panel)
    splitter.addWidget(right_panel)
    splitter.setSizes([300, 300])
    main_layout.addWidget(splitter)

    # Save button
    parent.save_team_members_btn = QPushButton("Add Selected Users to Team")
    parent.save_team_members_btn.clicked.connect(lambda: save_selected_team_members(parent))
    parent.save_team_members_btn.setEnabled(False)
    main_layout.addWidget(parent.save_team_members_btn)

    # Loading indicator
    parent.teams_progress_bar = QProgressBar()
    parent.teams_progress_bar.setVisible(False)
    main_layout.addWidget(parent.teams_progress_bar)

    # Connect tab change signal
    parent.tab_widget.currentChanged.connect(
        lambda index: on_tab_changed(parent, index)
    )
    
    return tab

def on_tab_changed(parent, index):
    """Load data when Teams tab is selected."""
    if parent.tab_widget.tabText(index) == "Team Members" and parent.org_name:
        load_team_data(parent)

def load_team_data(parent):
    """Load both saved teams and available users."""
    try:
        parent.teams_progress_bar.setVisible(True)
        QApplication.processEvents()

        # Clear existing data
        clear_team_ui(parent)

        # Load saved teams from backend
        saved_teams = get_saved_teams(parent)
        display_saved_teams(parent, saved_teams)

        # Load available users from backend
        available_users = get_available_users(parent)
        parent.available_users_data = available_users
        display_available_users(parent, available_users)

    except Exception as e:
        QMessageBox.critical(parent, "Error", f"Failed to load teams: {str(e)}")
    finally:
        parent.teams_progress_bar.setVisible(False)

def get_saved_teams(parent):
    """Fetch saved teams from backend API."""
    try:
        response = requests.get(
            USER_API["get_teams"](parent.project_id),
            timeout=10
        )
        # response.raise_for_status()
        response.json()
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
def display_saved_teams(parent, teams):
    """Display saved teams in the dropdown."""
    parent.saved_teams_combo.clear()
    parent.saved_teams_combo.addItem("Select a team")
    parent.teams_data = teams  # Store teams data for member display
    for team in teams:
        parent.saved_teams_combo.addItem(team.get('teamName', 'Unknown Team'))

def get_team_members(parent, team_id):
    """Fetch team members from backend API."""
    try:
        response = requests.get(
            USER_API["get_team_members"](team_id),
            timeout=10
        )
        # response.raise_for_status()
        response.json()
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

def update_available_users(parent, team_members):
    """Update available users list to exclude team members."""
    if not hasattr(parent, 'available_users_data'):
        parent.available_users_data = []
    
    # Get usernames of team members
    team_member_usernames = {member.get('userName', '') for member in team_members}
    
    # Filter out team members from available users
    filtered_users = [
        user for user in parent.available_users_data
        if user.get('userName') not in team_member_usernames
    ]
    
    # Update the UI with filtered users
    display_available_users(parent, filtered_users)  # NEW: Added to filter available users

def display_team_members(parent, index):
    """Display members of the selected team."""
    parent.team_members_list.clear()
    if index <= 0 or index > len(parent.teams_data):
        # Reload all users if no team is selected
        all_users = get_available_users(parent)
        parent.available_users_data = all_users
        display_available_users(parent, all_users)
        return
    
    try:
        parent.teams_progress_bar.setVisible(True)
        QApplication.processEvents()

        team = parent.teams_data[index - 1]  # Adjust for "Select a team" placeholder
        team_id = team.get('teamId')
        if not team_id:
            raise ValueError("Selected team does not have a teamId")

        team_members = get_team_members(parent, team_id)
        for member in team_members:
            display_name = member.get('displayName', member.get('userName', 'Unknown'))
            username = member.get('userName', 'Unknown')
            item = QListWidgetItem(f"{display_name} ({username})")
            parent.team_members_list.addItem(item)

        update_available_users(parent, team_members)  # CHANGED: Update available users to exclude team members

    except Exception as e:
        QMessageBox.warning(parent, "Error", f"Failed to load team members: {str(e)}")
    finally:
        parent.teams_progress_bar.setVisible(False)

def get_available_users(parent):
    """Fetch all saved users from backend API."""
    try:
        response = requests.get(
            USER_API["get_user_by_project"](parent.project_id),
            timeout=10
        )
        response.raise_for_status()
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
        
def display_available_users(parent, users):
    """Display available users with checkboxes in right panel."""
    # Clear existing widgets
    for i in reversed(range(parent.available_users_layout.count())):
        widget = parent.available_users_layout.itemAt(i).widget()
        if widget:
            widget.deleteLater()
    
    # Add checkboxes with proper signal handling
    for user in users:
        username = user.get('userName')
        display_name = user.get('displayName', username)
        checkbox = QCheckBox(f"{display_name} ({username})")
        
        # Create a container with loading spinner
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
        
        # Connect with proper signal handling
        checkbox.stateChanged.connect(
            partial(handle_user_checkbox_change, parent, username, checkbox, spinner)
        )
        
        parent.available_users_layout.addWidget(container)

def handle_user_checkbox_change(parent, username, checkbox, spinner, state):
    """Handle checkbox changes for user selection."""
    try:
        if not hasattr(parent, 'selected_team_users'):
            parent.selected_team_users = set()
            
        if state == Qt.CheckState.Checked.value:
            spinner.setVisible(True)
            checkbox.setEnabled(False)
            QApplication.processEvents()
            
            parent.selected_team_users.add(username)
            spinner.setVisible(False)
            checkbox.setEnabled(True)
        else:
            parent.selected_team_users.discard(username)
            
        # Enable save button only if a team is selected and users are selected
        team_index = parent.saved_teams_combo.currentIndex()
        parent.save_team_members_btn.setEnabled(
            team_index > 0 and bool(parent.selected_team_users)
        )
            
    except Exception as e:
        print(f"Checkbox error: {e}")
        QMessageBox.warning(parent, "Error", f"Failed to handle selection: {str(e)}")
        spinner.setVisible(False)
        checkbox.setEnabled(True)

def save_selected_team_members(parent):
    """Save selected users to the selected team in the backend."""
    try:
        team_index = parent.saved_teams_combo.currentIndex()
        if team_index <= 0:
            QMessageBox.warning(parent, "No Team Selected", "Please select a team.")
            return
        
        if not parent.selected_team_users:
            QMessageBox.warning(parent, "No Users Selected", "Please select at least one user.")
            return

        parent.teams_progress_bar.setVisible(True)
        parent.save_team_members_btn.setEnabled(False)
        QApplication.processEvents()

        # Get selected team
        team = parent.teams_data[team_index - 1]
        team_id = team.get('teamId')
        if not team_id:
            raise ValueError("Selected team does not have a teamId")

        # Map usernames to userIds
        user_id_map = {user['userName']: user['userId'] for user in parent.available_users_data}  # CHANGED: Use available_users_data
        payload = [
            {
                "teamId": team_id,
                "userId": user_id_map[username]
            }
            for username in parent.selected_team_users
            if username in user_id_map
        ]

        if not payload:
            raise ValueError("No valid user IDs found for selected users")

        # Save to backend
        response = requests.post(
            USER_API["create_team_member"],
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        project_data = response.json()
        if project_data.get("success"):
               QMessageBox.information(
            parent, 
            "Success", 
            f"Saved team memberships users successfully"
        )
        else:
                QMessageBox.critical(
                    parent,
                    str(project_data.get("errorCode", "API_ERROR")),
                    str(project_data.get("message", "Operation failed without details"))
                )
        
        # Refresh the view
        load_team_data(parent)

    except requests.exceptions.HTTPError as e:
        show_api_error(parent, "Failed to save team members", e)
    except Exception as e:
        QMessageBox.critical(parent, "Error", f"Unexpected error: {str(e)}")
    finally:
        parent.teams_progress_bar.setVisible(False)
        parent.save_team_members_btn.setEnabled(False)
        if hasattr(parent, 'selected_team_users'):
            parent.selected_team_users.clear()

def clear_team_ui(parent):
    """Clear all team UI elements."""
    parent.saved_teams_combo.clear()
    parent.saved_teams_combo.addItem("Select a team")
    parent.team_members_list.clear()
    for i in reversed(range(parent.available_users_layout.count())):
        parent.available_users_layout.itemAt(i).widget().deleteLater()
    if hasattr(parent, 'selected_team_users'):
        parent.selected_team_users.clear()  # CHANGED: Removed redundant clear
    if hasattr(parent, 'teams_data'):
        parent.teams_data = []
    if hasattr(parent, 'available_users_data'):
        parent.available_users_data = []

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