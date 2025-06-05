from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, 
    QPushButton, QProgressBar, QMessageBox, QCheckBox, QListWidget,
    QListWidgetItem, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from functools import partial
import requests
from config.api_config import USER_API, GITHUB_API

def setup_user_tab(parent):
    """Initialize the Users tab with split view"""
    tab = QWidget()
    main_layout = QVBoxLayout(tab)

    # Header
    header_label = QLabel("Organization Members")
    header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    header_label.setFixedHeight(40)
    main_layout.addWidget(header_label)

    # Create split view
    splitter = QSplitter(Qt.Orientation.Horizontal)
    
    # Left panel - Saved users
    left_panel = QWidget()
    left_layout = QVBoxLayout(left_panel)
    left_layout.addWidget(QLabel("Saved Users"))
    parent.saved_users_list = QListWidget()
    left_layout.addWidget(parent.saved_users_list)
    
    # Right panel - New GitHub users
    right_panel = QWidget()
    right_layout = QVBoxLayout(right_panel)
    right_layout.addWidget(QLabel("Available GitHub Users"))
    parent.github_users_scroll = QScrollArea()
    parent.github_users_scroll.setWidgetResizable(True)
    parent.github_users_widget = QWidget()
    parent.github_users_layout = QVBoxLayout(parent.github_users_widget)
    parent.github_users_scroll.setWidget(parent.github_users_widget)
    right_layout.addWidget(parent.github_users_scroll)
    
    # Add panels to splitter
    splitter.addWidget(left_panel)
    splitter.addWidget(right_panel)
    splitter.setSizes([300, 300])
    main_layout.addWidget(splitter)

    # Save button
    parent.save_users_btn = QPushButton("Save Selected Users")
    parent.save_users_btn.clicked.connect(lambda: save_selected_users(parent))
    parent.save_users_btn.setEnabled(False)
    main_layout.addWidget(parent.save_users_btn)

    # Loading indicator
    parent.users_progress_bar = QProgressBar()
    parent.users_progress_bar.setVisible(False)
    main_layout.addWidget(parent.users_progress_bar)

    # Connect tab change signal
    parent.tab_widget.currentChanged.connect(
        lambda index: on_tab_changed(parent, index))
    
    return tab

def on_tab_changed(parent, index):
    """Load data when Users tab is selected"""
    if parent.tab_widget.tabText(index) == "Users" and parent.org_name:
        load_user_data(parent)

def load_user_data(parent):
    """Load both saved users and GitHub members"""
    try:
        parent.users_progress_bar.setVisible(True)
        QApplication.processEvents()

        # Clear existing data
        clear_user_ui(parent)

        # Load saved users from backend
        saved_users = get_saved_users(parent)
        display_saved_users(parent, saved_users)

        # Load GitHub members
        github_members = get_github_members(parent)
        unsaved_members = [
            m for m in github_members 
            if m not in [user['userName'] for user in saved_users]
        ]
        display_github_users(parent, unsaved_members)

    except Exception as e:
        QMessageBox.critical(parent, "Error", f"Failed to load users: {str(e)}")
    finally:
        parent.users_progress_bar.setVisible(False)

def get_saved_users(parent):
    """Fetch saved users from backend API"""
    try:
        response = requests.get(
            USER_API["get_user_by_project"](parent.project_id),
            timeout=10
        )
        project_data = response.json()
        print(project_data)
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

def display_saved_users(parent, users):
    """Display saved users in left panel"""
    parent.saved_users_list.clear()
    for user in users:
        item = QListWidgetItem(
            f"{user.get('displayName', user['userName'])} ({user['userName']})"
        )
        parent.saved_users_list.addItem(item)

def get_github_members(parent):
    """Fetch organization members from GitHub"""
    headers = {"Authorization": f"Bearer {parent.pat_input.text()}"} if parent.pat_input.text() else {}
    response = requests.get(
        GITHUB_API["get_org_members"](parent.org_name),
        headers=headers,
        timeout=10
    )
    response.raise_for_status()
    return [member["login"] for member in response.json()]


def display_github_users(parent, usernames):
    """Display GitHub users with checkboxes in right panel"""
    # Clear existing widgets
    for i in reversed(range(parent.github_users_layout.count())):
        widget = parent.github_users_layout.itemAt(i).widget()
        if widget:
            widget.deleteLater()
    
    # Add checkboxes with proper signal handling
    for username in usernames:
        checkbox = QCheckBox(username)
        
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
        
        # Connect with proper argument handling
        checkbox.stateChanged.connect(
            partial(handle_checkbox_change, parent, username, checkbox, spinner)
        )
        
        parent.github_users_layout.addWidget(container)

def handle_checkbox_change(parent, username, checkbox, spinner, state):
    """Handle checkbox changes safely"""
    try:
        if state == Qt.CheckState.Checked.value:
            # Show loading spinner
            spinner.setVisible(True)
            checkbox.setEnabled(False)
            QApplication.processEvents()
            
            # Fetch user details
            user_details = get_github_user_details(parent, username)
            if user_details:
                parent.selected_users[username] = user_details
            else:
                # Reset checkbox if fetch fails
                checkbox.blockSignals(True)
                checkbox.setChecked(False)
                checkbox.blockSignals(False)
                
        else:
            # Remove from selection
            parent.selected_users.pop(username, None)
            
        # Update save button state
        parent.save_users_btn.setEnabled(bool(parent.selected_users))
            
    except Exception as e:
        print(f"Checkbox error: {e}")
        QMessageBox.warning(parent, "Error", f"Failed to handle selection: {str(e)}")
    finally:
        spinner.setVisible(False)
        checkbox.setEnabled(True)

def on_user_selected(parent, state, username):
    """Handle user selection/deselection"""
    if not hasattr(parent, 'selected_users'):
        parent.selected_users = set()

    # Convert state to Qt.CheckState enum
    checked = state == Qt.CheckState.Checked.value

    if checked:
        user_details = get_github_user_details(parent, username)
        print(user_details)
        if user_details:
            parent.selected_users.add(username)
        else:
            # Safely uncheck without triggering signals
            sender = parent.sender()
            if isinstance(sender, QCheckBox):
                sender.blockSignals(True)
                sender.setChecked(False)
                sender.blockSignals(False)
    else:
        parent.selected_users.discard(username)
    
    parent.save_users_btn.setEnabled(bool(parent.selected_users))

def save_selected_users(parent):
    """Save selected users to backend"""
    try:
        parent.users_progress_bar.setVisible(True)
        parent.save_users_btn.setEnabled(False)
        QApplication.processEvents()

        # Fetch details for selected users
        users_to_save = []
        for username in parent.selected_users:
            user_details = get_github_user_details(parent, username)
            if user_details:
                users_to_save.append(user_details)

        # Prepare payload
        payload = {
            "projectId": parent.project_id,
            "users": users_to_save
        }

        # Save to backend
        response = requests.post(
            USER_API["create_user"],
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        project_data = response.json()
        if project_data.get("success"):
               QMessageBox.information(
            parent, 
            "Success", 
            f"Saved {len(users_to_save)} users successfully"
        )
        else:
                QMessageBox.critical(
                    parent,
                    str(project_data.get("errorCode", "API_ERROR")),
                    str(project_data.get("message", "Operation failed without details"))
                )


        
        
        # Refresh the view
        load_user_data(parent)

    except requests.exceptions.HTTPError as e:
        show_api_error(parent, "Failed to save users", e)
    except Exception as e:
        QMessageBox.critical(parent, "Error", f"Unexpected error: {str(e)}")
    finally:
        parent.users_progress_bar.setVisible(False)
        parent.save_users_btn.setEnabled(False)
        parent.selected_users.clear()

def get_github_user_details(parent, username):
    """Fetch detailed user info from GitHub"""
    try:
        headers = {"Authorization": f"Bearer {parent.pat_input.text()}"} if parent.pat_input.text() else {}
        response = requests.get(
            GITHUB_API["get_user_details"](username),
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        return {
            "userName": data.get("login"),
            "nodeId": data.get("node_id"),
            "avatarUrl": data.get("avatar_url"),
            "displayName": data.get("name") or data.get("login"),
            "userCreatedAt": data.get("created_at"),
            "userUpdatedAt": data.get("updated_at")
        }
    except Exception:
        return None

def clear_user_ui(parent):
    """Clear all user UI elements"""
    parent.saved_users_list.clear()
    for i in reversed(range(parent.github_users_layout.count())):
        parent.github_users_layout.itemAt(i).widget().deleteLater()
    if hasattr(parent, 'selected_users'):
        parent.selected_users.clear()

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

