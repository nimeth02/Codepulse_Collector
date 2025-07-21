from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QPushButton,
    QProgressBar,
    QMessageBox,
    QCheckBox,
    QListWidget,
    QListWidgetItem,
    QSplitter,
    QComboBox,
    QApplication,
)
from PyQt6.QtCore import Qt
from functools import partial
from utils.errors import show_error_message, APIError, InputValidationError
from utils.threading import worker_spinner
from models.user_model import get_saved_users
from models.team_model import get_saved_teams
from models.team_member_model import (
    fetch_team_member_data,
    save_team_members,
    fetch_team_members,
)


def load_team_member_data(parent):
    """Load saved teams and available users in a background thread."""

    def task():
        return fetch_team_member_data(
            parent.project_id, parent.org_name, parent.current_provider
        )

    def on_success(result):
        clear_team_member_ui(parent)
        display_saved_teams(parent, result["saved_teams"])
        parent.available_users_data = result["available_users"]
        display_available_users(parent, result["available_users"])

    def on_error(e):
        from requests.exceptions import ConnectionError, Timeout

        if isinstance(e, ConnectionError):
            msg = "Unable to connect to backend server."
        elif isinstance(e, Timeout):
            msg = "Request timed out. Please try again."
        else:
            msg = str(e)

        QMessageBox.critical(parent, "Error", f"Failed to load users:\n{msg}")

    # Start background worker
    worker_spinner(
        parent=parent,
        progress_bar=parent.team_members_progress_bar,
        task_fn=task,
        on_success=on_success,
        on_error=on_error,
    )


def display_saved_teams(parent, teams):
    """Display saved teams in the dropdown."""
    parent.saved_teams_combo.clear()
    parent.saved_teams_combo.addItem("Select a team")
    parent.teams_data = teams  # Store teams data for member display
    for team in teams:
        parent.saved_teams_combo.addItem(team.get("teamName", "Unknown Team"))


def update_available_users(parent, team_members, teamName, teamId):
    """Update available users list to exclude team members."""
    if not hasattr(parent, "available_users_data"):
        parent.available_users_data = []

    # Get usernames of team members
    provider_team_member_payload = parent.current_provider.get_team_members_data(
        teamName, teamId
    )
    provider_team_member_usernames = {
        member.get("nodeId", "") for member in provider_team_member_payload
    }
    team_member_usernames = {member.get("nodeId", "") for member in team_members}

    # Filter out team members from available users
    filtered_users = [
        user
        for user in parent.available_users_data
        if user.get("nodeId") not in team_member_usernames
        and user.get("nodeId") in provider_team_member_usernames
    ]
    # Update the UI with filtered users
    display_available_users(
        parent, filtered_users
    )  # NEW: Added to filter available users


def display_team_members(parent, index):
    """Display members of the selected team using background thread."""

    # If no team selected, fallback to showing all users
    if index <= 0 or index > len(parent.teams_data):
        display_available_users(parent, parent.available_users_data)
        # def fallback_task():
        #     all_users = get_saved_users(parent.project_id)
        #     return {"available_users": all_users}

        # def fallback_success(result):
        #     parent.available_users_data = result["available_users"]
        #     display_available_users(parent, result["available_users"])

        # def fallback_error(e):
        #     msg = (
        #         "Cannot connect to backend."
        #         if isinstance(e, ConnectionError)
        #         else str(e)
        #     )
        #     QMessageBox.warning(parent, "Error", f"Failed to load users: {msg}")

        # worker_spinner(
        #     parent=parent,
        #     progress_bar=parent.team_members_progress_bar,
        #     task_fn=fallback_task,
        #     on_success=fallback_success,
        #     on_error=fallback_error,
        # )
        return

    # Background task for valid team
    def task():
        team = parent.teams_data[index - 1]
        return fetch_team_members(parent.project_id, team)

    def on_success(result):
        team = result["team"]
        team_members = result["team_members"]
        parent.team_members_list.clear()

        for member in team_members:
            display_name = member.get("displayName", member.get("userName", "Unknown"))
            username = member.get("userName", "Unknown")
            item = QListWidgetItem(f"{display_name} ({username})")
            parent.team_members_list.addItem(item)

        parent.available_users_data = result["available_users"]
        update_available_users(
            parent, team_members, team.get("teamName", ""), team.get("nodeId")
        )

    def on_error(e):
        msg = "Failed to connect to API." if isinstance(e, ConnectionError) else str(e)
        QMessageBox.warning(parent, "Error", f"Failed to load team members: {msg}")

    worker_spinner(
        parent=parent,
        progress_bar=parent.team_members_progress_bar,
        task_fn=task,
        on_success=on_success,
        on_error=on_error,
    )


def display_available_users(parent, users):
    """Display available users with checkboxes in right panel."""
    # Clear existing widgets
    for i in reversed(range(parent.available_users_layout.count())):
        widget = parent.available_users_layout.itemAt(i).widget()
        if widget:
            widget.deleteLater()

    # Add checkboxes with proper signal handling
    for user in users:
        username = user.get("userName")
        display_name = user.get("displayName", username)
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
        if state == Qt.CheckState.Checked.value:
            spinner.setVisible(True)
            checkbox.setEnabled(False)
            QApplication.processEvents()

            parent.selected_team_users.add(username)
            spinner.setVisible(False)
            checkbox.setEnabled(True)
        else:
            parent.selected_team_users.remove(username)

        # Enable save button only if a team is selected and users are selected
        team_index = parent.saved_teams_combo.currentIndex()
        parent.save_team_members_btn.setEnabled(
            team_index > 0 and bool(parent.selected_team_users)
        )

    except Exception as e:
        print(f"Checkbox error: {e}")
        QMessageBox.warning(parent, "Error", f"Failed to handle selection: {str(e)}")
    finally:
        spinner.setVisible(False)
        checkbox.setEnabled(True)


def check_all_users(parent):
    """Check all available user checkboxes."""
    try:
        if not hasattr(parent, "selected_team_users"):
            parent.selected_team_users = set()

        # Get all checkboxes in the available users layout
        for i in range(parent.available_users_layout.count()):
            container = parent.available_users_layout.itemAt(i).widget()
            if container:
                # Find the checkbox in the container
                for j in range(container.layout().count()):
                    widget = container.layout().itemAt(j).widget()
                    if isinstance(widget, QCheckBox):
                        checkbox = widget
                        if not checkbox.isChecked():
                            checkbox.setChecked(True)
                        break

        # Enable save button if a team is selected
        team_index = parent.saved_teams_combo.currentIndex()
        parent.save_team_members_btn.setEnabled(team_index > 0)

    except Exception as e:
        print(f"Check all error: {e}")
        QMessageBox.warning(parent, "Error", f"Failed to check all users: {str(e)}")


def save_selected_team_members(parent):
    """Save selected users to the selected team using a background thread."""

    try:
        team_index = parent.saved_teams_combo.currentIndex()
        if team_index <= 0:
            raise InputValidationError("Please select a team to save members.")

        if not parent.selected_team_users:
            raise InputValidationError("Please select at least one user.")

        # Prepare data outside thread (can raise errors early)
        team = parent.teams_data[team_index - 1]
        team_id = team.get("teamId")
        if not team_id:
            raise ValueError("Selected team does not have a teamId")

        user_id_map = {
            user["userName"]: user["userId"] for user in parent.available_users_data
        }
        payload = [
            {"teamId": team_id, "userId": user_id_map[username]}
            for username in parent.selected_team_users
            if username in user_id_map
        ]

        if not payload:
            raise InputValidationError("No valid users found for the selected team.")

    except Exception as e:
        parent.save_team_members_btn.setEnabled(bool(parent.selected_team_users))
        show_error_message(parent, e, "Validation Error")
        return

    # Background task
    def task():
        return save_team_members(payload)

    def on_success(response_data):
        parent.save_team_members_btn.setEnabled(bool(parent.selected_team_users))
        parent.selected_team_users.clear()

        if response_data.get("success"):
            QMessageBox.information(
                parent, "Success", "Saved team members successfully."
            )
            load_team_member_data(parent)  # Refresh view
        else:
            QMessageBox.critical(
                parent,
                str(response_data.get("errorCode", "API_ERROR")),
                str(response_data.get("message", "Operation failed without details")),
            )

    def on_error(e):
        parent.save_team_members_btn.setEnabled(bool(parent.selected_team_users))
        parent.selected_team_users.clear()
        show_error_message(parent, e, "Unexpected Error")

    worker_spinner(
        parent=parent,
        progress_bar=parent.team_members_progress_bar,
        task_fn=task,
        on_success=on_success,
        on_error=on_error,
    )


def clear_team_member_ui(parent):
    """Clear all team member UI elements."""
    parent.saved_teams_combo.clear()
    parent.saved_teams_combo.addItem("Select a team")
    parent.team_members_list.clear()
    for i in reversed(range(parent.available_users_layout.count())):
        parent.available_users_layout.itemAt(i).widget().deleteLater()
    if hasattr(parent, "selected_team_users"):
        parent.selected_team_users.clear()  # CHANGED: Removed redundant clear
    if hasattr(parent, "teams_data"):
        parent.teams_data = []
    if hasattr(parent, "available_users_data"):
        parent.available_users_data = []
