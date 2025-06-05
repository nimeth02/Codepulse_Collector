from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, 
    QPushButton, QProgressBar, QMessageBox, QCheckBox, QListWidget,
    QListWidgetItem, QSplitter,QDialog, QFormLayout, QLineEdit, QDialogButtonBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from functools import partial
import requests
import uuid
from config.api_config import USER_API, GITHUB_API

def setup_team_tab(parent):
    """Create and return the user tab"""
    tab = QWidget()
    main_layout = QVBoxLayout(tab)

    # Header
    header_label = QLabel("Team Members")
    header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    header_label.setFixedHeight(40)
    main_layout.addWidget(header_label)
    
        # Create split view
    splitter = QSplitter(Qt.Orientation.Horizontal)
    
    # Left panel - Saved users
    left_panel = QWidget()
    left_layout = QVBoxLayout(left_panel)
    left_layout.addWidget(QLabel("Saved Teams"))
    parent.saved_teams_list = QListWidget()
    left_layout.addWidget(parent.saved_teams_list)
    
    # Right panel - New GitHub users
    right_panel = QWidget()
    right_layout = QVBoxLayout(right_panel)
    right_layout.addWidget(QLabel("Available GitHub Teams"))
    parent.github_teams_scroll = QScrollArea()
    parent.github_teams_scroll.setWidgetResizable(True)
    parent.github_teams_widget = QWidget()
    parent.github_teams_layout = QVBoxLayout(parent.github_teams_widget)
    parent.github_teams_scroll.setWidget(parent.github_teams_widget)
    right_layout.addWidget(parent.github_teams_scroll)

    # Add panels to splitter
    splitter.addWidget(left_panel)
    splitter.addWidget(right_panel)
    splitter.setSizes([300, 300])
    main_layout.addWidget(splitter)

     # Add creation button row
    button_row = QHBoxLayout()
    
    parent.create_team_btn = QPushButton("Create New Team")
    parent.create_team_btn.clicked.connect(lambda: show_create_team_dialog(parent))
    button_row.addWidget(parent.create_team_btn)
    
    parent.save_teams_btn = QPushButton("Save Selected Teams")
    parent.save_teams_btn.clicked.connect(lambda: save_selected_teams(parent))
    parent.save_teams_btn.setEnabled(False)
    button_row.addWidget(parent.save_teams_btn)
    
    main_layout.addLayout(button_row)

    # Save button
    parent.save_teams_btn = QPushButton("Save Selected Teams")
    parent.save_teams_btn.clicked.connect(lambda: save_selected_teams(parent))
    parent.save_teams_btn.setEnabled(False)
    main_layout.addWidget(parent.save_teams_btn)

    # Loading indicator
    parent.teams_progress_bar = QProgressBar()
    parent.teams_progress_bar.setVisible(False)
    main_layout.addWidget(parent.teams_progress_bar)

    # Connect tab change signal
    parent.tab_widget.currentChanged.connect(
        lambda index: on_tab_changed(parent, index))
    
    return tab

def on_tab_changed(parent, index):
    """Load data when Teams tab is selected"""
    if parent.tab_widget.tabText(index) == "Teams" and parent.org_name:
        load_team_data(parent)
    
def load_team_data(parent):
    """Load both saved teams and GitHub teams"""
    try:
        parent.teams_progress_bar.setVisible(True)
        QApplication.processEvents()

        # Clear existing data
        clear_team_ui(parent)

        # Load saved teams from backend
        saved_teams = get_saved_teams(parent)
        display_saved_teams(parent, saved_teams)

        # Load GitHub teams and filter out already saved ones
        github_teams = get_github_teams(parent)
        saved_team_names = {team['nodeId'] for team in saved_teams}
        unsaved_teams = [
            team for team in github_teams 
            if team['node_id'] not in saved_team_names
        ]
        
        display_github_teams(parent, unsaved_teams)

    except Exception as e:
        QMessageBox.critical(parent, "Error", f"Failed to load teams: {str(e)}")
    finally:
        parent.teams_progress_bar.setVisible(False)

def get_github_teams(parent):
    """Fetch organization teams from GitHub with full details"""
    headers = {"Authorization": f"Bearer {parent.pat_input.text()}"} if parent.pat_input.text() else {}
    response = requests.get(
        GITHUB_API["get_org_teams"](parent.org_name),
        headers=headers,
        timeout=10
    )
    response.raise_for_status()
    return response.json()       

def get_saved_teams(parent):
    """Fetch saved teams from backend API"""
    try:
        response = requests.get(
            USER_API["get_teams"](parent.project_id),
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

def display_saved_teams(parent, teams):
    """Display saved teams in left panel"""
    parent.saved_teams_list.clear()
    for team in teams:
        item = QListWidgetItem(f"{team['teamName']} - {team.get('description', '')}")
        item.setData(Qt.ItemDataRole.UserRole, team)  
        parent.saved_teams_list.addItem(item)

def display_github_teams(parent, teams):
    """Display GitHub teams with checkboxes in right panel"""
    # Clear existing widgets
    for i in reversed(range(parent.github_teams_layout.count())):
        widget = parent.github_teams_layout.itemAt(i).widget()
        if widget:
            widget.deleteLater()
    
    # Add checkboxes for each unsaved team
    for team in teams:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        checkbox = QCheckBox(f"{team['name']} - {team.get('description', '')}")
        spinner = QProgressBar()
        spinner.setRange(0, 0)
        spinner.setFixedSize(20, 20)
        spinner.setVisible(False)
        
        layout.addWidget(checkbox)
        layout.addWidget(spinner)
        layout.addStretch()
        
        # Store full team data in the checkbox
        checkbox.team_data = {
            "nodeId": team['node_id'],
            "teamName": team['name'],
            "description": team.get('description', '')
        }
        
        checkbox.stateChanged.connect(
            partial(handle_checkbox_change, parent, checkbox, spinner)
        )
        
        parent.github_teams_layout.addWidget(container)

def handle_checkbox_change(parent, checkbox, spinner, state):
    """Handle team checkbox changes with full team data"""
    try:
        if not hasattr(parent, 'selected_teams'):
            parent.selected_teams = {}
            
        team_data = checkbox.team_data
        
        if state == Qt.CheckState.Checked.value:
            spinner.setVisible(True)
            checkbox.setEnabled(False)
            QApplication.processEvents()
            
            # Store the full team data
            parent.selected_teams[team_data['nodeId']] = team_data
        else:
            parent.selected_teams.pop(team_data['nodeId'], None)
            
        parent.save_teams_btn.setEnabled(bool(parent.selected_teams))
            
    except Exception as e:
        print(f"Team checkbox error: {e}")
        checkbox.setChecked(False)
    finally:
        spinner.setVisible(False)
        checkbox.setEnabled(True)     

def save_selected_teams(parent):
    """Save selected teams to backend"""
    try:
        parent.teams_progress_bar.setVisible(True)
        parent.save_teams_btn.setEnabled(False)
        QApplication.processEvents()

        # Prepare payload - same structure as before
        payload = {
            "projectId": parent.project_id,
            "teams": list(parent.selected_teams.values())
        }

        response = requests.post(
            USER_API["create_team"],
            json=payload,
            timeout=10
        )
        
        if response.status_code == 400:
            errors = response.json().get('errors', {})
            error_msg = "Validation errors:\n"
            for field, messages in errors.items():
                error_msg += f"- {field}: {', '.join(messages)}\n"
            raise requests.exceptions.HTTPError(error_msg)
            
        response.raise_for_status()

        QMessageBox.information(
            parent, 
            "Success", 
            f"Saved {len(parent.selected_teams)} teams successfully"
        )
        
        # Refresh the view after save
        load_team_data(parent)

    except requests.exceptions.HTTPError as e:
        QMessageBox.critical(parent, "API Error", str(e))
    except Exception as e:
        QMessageBox.critical(parent, "Error", f"Failed to save teams: {str(e)}")
    finally:
        parent.teams_progress_bar.setVisible(False)
        parent.save_teams_btn.setEnabled(bool(parent.selected_teams))

def clear_team_ui(parent):
    """Clear all team UI elements"""
    parent.saved_teams_list.clear()
    for i in reversed(range(parent.github_teams_layout.count())):
        parent.github_teams_layout.itemAt(i).widget().deleteLater()
    if hasattr(parent, 'selected_teams'):
        parent.selected_teams.clear()

def show_api_error(parent, context, exception):
    """Show formatted API error message"""
    error_msg = f"{context}\n"
    if hasattr(exception, 'response'):
        error_msg += f"Status: {exception.response.status_code}\n"
        if exception.response.text:
            error_msg += f"Details: {exception.response.text[:200]}..."
    else:
        error_msg += str(exception)
    
    QMessageBox.critical(parent, "API Error", error_msg)                


def show_create_team_dialog(parent):
    """Show dialog for creating a new custom team"""
    dialog = QDialog(parent)
    dialog.setWindowTitle("Create New Team")
    dialog.setMinimumWidth(400)
    
    layout = QFormLayout(dialog)
    
    # Team name field
    name_edit = QLineEdit()
    name_edit.setPlaceholderText("Enter team name")
    layout.addRow("Team Name:", name_edit)
    
    # Description field
    desc_edit = QLineEdit()
    desc_edit.setPlaceholderText("Enter team description")
    layout.addRow("Description:", desc_edit)
    
    # Buttons
    buttons = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
        Qt.Orientation.Horizontal,
        dialog
    )
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    layout.addRow(buttons)
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        team_name = name_edit.text().strip()
        team_desc = desc_edit.text().strip()
        
        if not team_name:
            QMessageBox.warning(parent, "Error", "Team name cannot be empty")
            return
            
        create_custom_team(parent, team_name, team_desc)    


def create_custom_team(parent, team_name, team_description=""):
    """Create and save a new custom team"""
    try:
        parent.teams_progress_bar.setVisible(True)
        QApplication.processEvents()
        
        # Generate a node ID (similar to GitHub's format)
        node_id = f"team-{uuid.uuid4().hex[:8]}"
        
        team_data = {
            "nodeId": node_id,
            "teamName": team_name,
            "description": team_description
        }
        
        # Add to selected teams immediately
        if not hasattr(parent, 'selected_teams'):
            parent.selected_teams = {}
        parent.selected_teams[node_id] = team_data
        
        # Enable save button
        parent.save_teams_btn.setEnabled(True)
        
        # Add to the UI
        add_team_to_ui(parent, team_data, is_custom=True)
        
        QMessageBox.information(
            parent,
            "Team Created",
            f"Team '{team_name}' created successfully!\n"
            f"Remember to click 'Save Selected Teams' to persist it."
        )
        
    except Exception as e:
        QMessageBox.critical(parent, "Error", f"Failed to create team: {str(e)}")
    finally:
        parent.teams_progress_bar.setVisible(False)

def add_team_to_ui(parent, team_data, is_custom=False):
    """Add a team to the appropriate UI list"""
    if is_custom:
        # Add to GitHub teams list (right panel) with checkbox checked
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        checkbox = QCheckBox(f"{team_data['teamName']} - {team_data['description']}")
        checkbox.setChecked(True)
        checkbox.team_data = team_data
        
        spinner = QProgressBar()
        spinner.setRange(0, 0)
        spinner.setFixedSize(20, 20)
        spinner.setVisible(False)
        
        layout.addWidget(checkbox)
        layout.addWidget(spinner)
        layout.addStretch()
        
        checkbox.stateChanged.connect(
            partial(handle_checkbox_change, parent, checkbox, spinner)
        )
        
        parent.github_teams_layout.addWidget(container)
    else:
        # For saved teams (left panel)
        item = QListWidgetItem(f"{team_data['teamName']} - {team_data['description']}")
        item.setData(Qt.ItemDataRole.UserRole, team_data)
        parent.saved_teams_list.addItem(item)