from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QProgressBar,
    QMessageBox,
    QCheckBox,
    QListWidgetItem,
    QRadioButton,
)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from functools import partial
from utils.errors import show_error_message
from utils.threading import worker_spinner
from models.user_model import fetch_user_data, save_users


def load_user_data(parent):
    """Load saved users and Provider members using reusable threaded runner."""

    def task():
        return fetch_user_data(
            parent.project_id, parent.org_name, parent.current_provider
        )

    def on_success(result):
        clear_user_ui(parent)
        display_saved_users(parent, result["saved_users"])
        display_provider_users(parent, result["unsaved_members"])

    def on_error(e):
        from requests.exceptions import ConnectionError, Timeout

        if isinstance(e, ConnectionError):
            msg = "Unable to connect to backend server."
        elif isinstance(e, Timeout):
            msg = "Request timed out. Please try again."
        else:
            msg = str(e)

        QMessageBox.critical(parent, "Error", f"Failed to load users:\n{msg}")

    worker_spinner(
        parent=parent,
        progress_bar=parent.users_progress_bar,
        task_fn=task,
        on_success=on_success,
        on_error=on_error,
    )


def display_saved_users(parent, users):
    """Display saved users in left panel"""
    parent.saved_users_list.clear()
    for user in users:
        item = QListWidgetItem(
            f"{user.get('displayName', user['userName'])} ({user['userName']})"
        )
        # Make item non-interactive by removing selection and focus flags
        item.setFlags(
            item.flags() & ~Qt.ItemFlag.ItemIsSelectable & ~Qt.ItemFlag.ItemIsEnabled
        )
        parent.saved_users_list.addItem(item)


def display_provider_users(parent, users):
    """Display Provider users with checkboxes in right panel"""
    # Clear existing widgets
    for i in reversed(range(parent.provider_users_layout.count())):
        widget = parent.provider_users_layout.itemAt(i).widget()
        if widget:
            widget.deleteLater()

    parent.user_checkboxes = []

    # Add checkboxes with proper signal handling
    for user in users:
        username = user["userName"]
        checkbox = QCheckBox(username)

        # Create a container with loading spinner and radio button
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        spinner = QProgressBar()
        spinner.setRange(0, 0)
        spinner.setFixedSize(20, 20)
        spinner.setVisible(False)

        # Add Mask radio button
        mask_radio = QRadioButton("Mask")

        # Connect radio button to handler
        mask_radio.toggled.connect(
            partial(handle_mask_radio, user, checkbox)
        )

        layout.addWidget(checkbox)
        layout.addWidget(spinner)
        # Add spacing between spinner and radio button
        layout.addSpacing(10)  # 10 pixels of space
        layout.addWidget(mask_radio)
        layout.addStretch()

        # Connect with proper argument handling
        checkbox.stateChanged.connect(
            partial(handle_checkbox_change, parent, user, checkbox, spinner)
        )

        # Store checkbox reference for check all functionality
        parent.user_checkboxes.append((checkbox, user, spinner, mask_radio))
        parent.provider_users_layout.addWidget(container)


def handle_checkbox_change(parent, user, checkbox, spinner, state):
    """Handle checkbox changes safely"""
    try:
        if state == Qt.CheckState.Checked.value:
            spinner.setVisible(True)
            checkbox.setEnabled(False)
            QApplication.processEvents()

            if user:
                parent.selected_users.append(user)
            else:
                checkbox.blockSignals(True)
                checkbox.setChecked(False)
                checkbox.blockSignals(False)

        else:
            if user:
                parent.selected_users.remove(user)

        parent.save_users_btn.setEnabled(bool(parent.selected_users))

    except Exception as e:
        print(f"Checkbox error: {e}")
        QMessageBox.warning(parent, "Error", f"Failed to handle selection: {str(e)}")
    finally:
        spinner.setVisible(False)
        checkbox.setEnabled(True)

def check_all_users(parent):
    """Check all available provider users"""
    try:
        if not hasattr(parent, "user_checkboxes") or not parent.user_checkboxes:
            return

        # Check all checkboxes
        for checkbox, user, *_ in parent.user_checkboxes:  # unpack only needed items
            if not checkbox.isChecked():
                checkbox.blockSignals(True)
                checkbox.setChecked(True)
                checkbox.blockSignals(False)

                if user not in parent.selected_users:
                    parent.selected_users.append(user)

        parent.save_users_btn.setEnabled(bool(parent.selected_users))

    except Exception as e:
        print(f"Check all error: {e}")
        QMessageBox.warning(parent, "Error", f"Failed to check all users: {str(e)}")

def handle_mask_radio(user, checkbox, checked):
    """Mask the user's name to first 3 characters when radio is checked."""
    if checked:
        original_name = user.get("name", user.get("userName", ""))
        masked_name = original_name[:3]
        user["name"] = masked_name
        # Optionally update the checkbox label to show masked name
        checkbox.setText(masked_name)
    else:
        # Optionally restore the original name if you store it somewhere
        pass

def save_selected_users(parent):
    """Save selected users to backend using a background thread."""

    if not parent.selected_users:
        QMessageBox.information(parent, "No Users", "No users selected to save.")
        return

    # Mask names for users whose radio button is checked
    for checkbox, user, spinner, mask_radio in getattr(parent, "user_checkboxes", []):
        if mask_radio.isChecked():
            original_name = user.get("userName", "")
            masked_name = original_name[:3]
            user["userName"] = masked_name
            user["displayName"] = masked_name

    parent.save_users_btn.setEnabled(False)

    def task():
        """Background thread: save users + fetch updated user data"""
        return save_users(parent.project_id, parent.selected_users)

    def on_success(result):
        parent.save_users_btn.setEnabled(True)
        parent.selected_users.clear()

        QMessageBox.information(
            parent, "Success", f"Saved {result['saved_count']} users successfully."
        )

        clear_user_ui(parent)
        # display_saved_users(parent, result["saved_users"])
        # display_provider_users(parent, result["unsaved_members"])
        load_user_data(parent)

    def on_error(e):
        parent.save_users_btn.setEnabled(True)
        show_error_message(parent, e, "Failed to Save Users")

    worker_spinner(
        parent=parent,
        progress_bar=parent.users_progress_bar,
        task_fn=task,
        on_success=on_success,
        on_error=on_error,
    )


def clear_user_ui(parent):
    """Clear all user UI elements"""
    parent.saved_users_list.clear()
    for i in reversed(range(parent.provider_users_layout.count())):
        parent.provider_users_layout.itemAt(i).widget().deleteLater()
    if hasattr(parent, "selected_users"):
        parent.selected_users.clear()
    if hasattr(parent, "user_checkboxes"):
        parent.user_checkboxes.clear()
