from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QProgressBar,
    QMessageBox,
    QCheckBox,
    QListWidgetItem,
)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from functools import partial
from utils.threading import worker_spinner
from models.team_model import fetch_team_data, save_teams


# def on_tab_changed(parent, index):
#     """Load data when Teams tab is selected"""
#     if parent.tab_widget.tabText(index) == "Teams" and parent.org_name:
#         load_team_data(parent)


def load_team_data(parent):
    """Load both saved teams and provider teams using a background thread."""
    def task():
        """Background work (runs in thread): fetch backend + provider teams"""
        return fetch_team_data(
            parent.project_id, parent.org_name, parent.current_provider
        )

    def on_success(result):
        clear_team_ui(parent)
        display_saved_teams(parent, result["saved_teams"])
        display_provider_teams(parent, result["unsaved_teams"])

    def on_error(e):
        from requests.exceptions import ConnectionError, Timeout

        if isinstance(e, ConnectionError):
            msg = "Unable to connect to backend server."
        elif isinstance(e, Timeout):
            msg = "Request timed out. Please try again."
        else:
            msg = str(e)

        QMessageBox.critical(parent, "Error", f"Failed to load teams:\n{msg}")
   
    worker_spinner(
        parent=parent,
        progress_bar=parent.teams_progress_bar,
        task_fn=task,
        on_success=on_success,
        on_error=on_error,
    )


def display_saved_teams(parent, teams):
    """Display saved teams in left panel"""
    parent.saved_teams_list.clear()
    for team in teams:
        item = QListWidgetItem(f"{team['teamName']} - {team.get('description', '')}")
        item.setData(Qt.ItemDataRole.UserRole, team)
        parent.saved_teams_list.addItem(item)


def display_provider_teams(parent, teams):
    """Display provider teams with checkboxes in right panel"""
    # Clear existing widgets
    for i in reversed(range(parent.provider_teams_layout.count())):
        widget = parent.provider_teams_layout.itemAt(i).widget()
        if widget:
            widget.deleteLater()

    # Add checkboxes for each unsaved team
    for team in teams:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        checkbox = QCheckBox(f"{team['teamName']} - {team.get('description', '')}")
        spinner = QProgressBar()
        spinner.setRange(0, 0)
        spinner.setFixedSize(20, 20)
        spinner.setVisible(False)

        layout.addWidget(checkbox)
        layout.addWidget(spinner)
        layout.addStretch()

        # Store full team data in the checkbox
        checkbox.team_data = {
            "nodeId": team["nodeId"],
            "teamName": team["teamName"],
            "description": team.get("description", ""),
        }

        checkbox.stateChanged.connect(
            partial(handle_checkbox_change, parent,team, checkbox, spinner)
        )

        parent.provider_teams_layout.addWidget(container)


def handle_checkbox_change(parent,team, checkbox, spinner, state):
    """Handle team checkbox changes with full team data"""
    try:
        team_data = checkbox.team_data

        if state == Qt.CheckState.Checked.value:
            spinner.setVisible(True)
            checkbox.setEnabled(False)
            QApplication.processEvents()

            # Store the full team data
            parent.selected_teams.append(team)
        else:
            parent.selected_teams.remove(team)

        parent.save_teams_btn.setEnabled(bool(parent.selected_teams))

    except Exception as e:
        print(f"Team checkbox error: {e}")
        QMessageBox.warning(parent, "Error", f"Failed to handle selection: {str(e)}")
        checkbox.setChecked(False)
    finally:
        spinner.setVisible(False)
        checkbox.setEnabled(True)


def save_selected_teams(parent):
    """Save selected teams to backend using background thread."""

    if not parent.selected_teams:
        QMessageBox.information(parent, "No Teams", "No teams selected to save.")
        return

    # Show loading indicator
    parent.save_teams_btn.setEnabled(False)
    QApplication.processEvents()

    def task():
        """Runs in background: Save teams, then reload them"""
        return save_teams(parent.project_id, parent.selected_teams)

    def on_success(result):
        parent.save_teams_btn.setEnabled(True)

        QMessageBox.information(
            parent, "Success", f"Saved {result['saved_count']} teams successfully."
        )

        load_team_data(parent)
        parent.selected_teams.clear()

    def on_error(e):
        parent.save_teams_btn.setEnabled(bool(parent.selected_teams))
        show_error_message(parent, e, "Failed to Save Teams")

    # Start threaded worker
    worker_spinner(
        parent=parent,
        progress_bar=parent.teams_progress_bar,
        task_fn=task,
        on_success=on_success,
        on_error=on_error,
    )


def clear_team_ui(parent):
    """Clear all team UI elements"""
    parent.saved_teams_list.clear()
    for i in reversed(range(parent.provider_teams_layout.count())):
        parent.provider_teams_layout.itemAt(i).widget().deleteLater()
    if hasattr(parent, "selected_teams"):
        parent.selected_teams.clear()
