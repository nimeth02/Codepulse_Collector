from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QProgressBar,
    QMessageBox,
    QCheckBox,
    QListWidgetItem,
    QApplication,
)
from PyQt6.QtCore import Qt
from functools import partial
from utils.errors import show_error_message, APIError, InputValidationError
from utils.threading import worker_spinner
from models.code_repository_model import (
    fetch_code_repository_data,
    save_code_repositories,
)


def load_repos_data(parent):
    """Load saved and unsaved repositories in a background thread."""
    def task():
        """Runs in background thread."""
        return fetch_code_repository_data(
            parent.project_id, parent.org_name, parent.current_provider
        )

    def on_success(result):
        """Runs in main thread."""
        clear_repos_ui(parent)
        display_saved_repositories(parent, result["saved"])
        display_provider_repositories(parent, result["unsaved"])
        print("repos")

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
        progress_bar=parent.repos_progress_bar,
        task_fn=task,
        on_success=on_success,
        on_error=on_error,
    )


def display_saved_repositories(parent, repos):
    """Display saved repositories in the left panel."""
    parent.left_saved_repos_list.clear()
    parent.saved_repos_data = repos
    for repo in repos:
        name = repo.get("codeRepositoryName", "Unknown Repo")
        full_name = repo.get("fullName", "Unknown/Unknown")
        item = QListWidgetItem(f"{name} ({full_name})")
        parent.left_saved_repos_list.addItem(item)


def display_provider_repositories(parent, repos):
    """Display unsaved repositories with checkboxes in the right panel."""

    # Clear previous entries
    for i in reversed(range(parent.right_unsaved_repos_layout.count())):
        widget = parent.right_unsaved_repos_layout.itemAt(i).widget()
        if widget:
            widget.deleteLater()

    # Reset and store checkboxes
    parent.repo_checkboxes = []
    parent.unsaved_repos_data = repos

    for repo in repos:
        name = repo.get("codeRepositoryName", "Unknown Repo")
        full_name = repo.get("fullName", "Unknown/Unknown")
        node_id = repo.get("nodeId")

        # Checkbox UI
        checkbox = QCheckBox(f"{name} ({full_name})")

        # Container and layout
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        # Spinner next to checkbox
        spinner = QProgressBar()
        spinner.setRange(0, 0)
        spinner.setFixedSize(20, 20)
        spinner.setVisible(False)

        layout.addWidget(checkbox)
        layout.addWidget(spinner)
        layout.addStretch()

        # Connect event
        checkbox.stateChanged.connect(
            partial(handle_repo_checkbox_change, parent, repo, checkbox, spinner)
        )

        parent.repo_checkboxes.append((checkbox, repo, spinner))
        parent.right_unsaved_repos_layout.addWidget(container)


def handle_repo_checkbox_change(parent, repo, checkbox, spinner, state):
    """Handle checkbox changes for repository selection."""
    try:
        if state == Qt.CheckState.Checked.value:
            spinner.setVisible(True)
            checkbox.setEnabled(False)
            QApplication.processEvents()

            parent.selected_repos.append(repo)
            spinner.setVisible(False)
            checkbox.setEnabled(True)
        else:
            parent.selected_repos.remove(repo)

        parent.save_repos_btn.setEnabled(bool(parent.selected_repos))

    except Exception as e:
        print(f"Checkbox error: {e}")
        QMessageBox.warning(parent, "Error", f"Failed to handle selection: {str(e)}")
    finally:    
        spinner.setVisible(False)
        checkbox.setEnabled(True)


def check_all_repositories(parent):
    """Check all available provider repositories"""
    try:
        if not hasattr(parent, "repo_checkboxes") or not parent.repo_checkboxes:
            return

        for checkbox, repo, spinner in parent.repo_checkboxes:
            if not checkbox.isChecked():
                checkbox.blockSignals(True)
                checkbox.setChecked(True)
                checkbox.blockSignals(False)

                # Manually add to selected
                if not hasattr(parent, "selected_repos"):
                    parent.selected_repos = []
                parent.selected_repos.append(repo)

        parent.save_repos_btn.setEnabled(bool(parent.selected_repos))

    except Exception as e:
        print(f"Check all repos error: {e}")
        QMessageBox.warning(
            parent, "Error", f"Failed to check all repositories: {str(e)}"
        )


def save_selected_repositories(parent):
    """Save selected repositories using a background thread."""

    try:
        if not parent.selected_repos:
            raise InputValidationError("Please select at least one repository.")

        parent.save_repos_btn.setEnabled(False)

        selected_repos = (
            parent.selected_repos.copy()
        )  # Use copy to avoid future mutation
        project_id = parent.project_id

        def task():
            return save_code_repositories(project_id, selected_repos)

        def on_success(result):
            QMessageBox.information(
                parent,
                "Success",
                f"Saved {result['saved_count']} repositories successfully.",
            )
            load_repos_data(parent)

        def on_error(e):
            show_error_message(parent, e, "Error")

        worker_spinner(
            parent=parent,
            progress_bar=parent.repos_progress_bar,
            task_fn=task,
            on_success=on_success,
            on_error=on_error,
        )

    except (InputValidationError, Exception) as e:
        parent.repos_progress_bar.setVisible(False)
        show_error_message(parent, e, "Error")
    finally:
        parent.save_repos_btn.setEnabled(bool(parent.selected_repos))
        parent.selected_repos.clear()


def clear_repos_ui(parent):
    """Clear all repository UI elements."""
    parent.left_saved_repos_list.clear()  # CHANGED: Use left_saved_repos_list
    for i in reversed(
        range(parent.right_unsaved_repos_layout.count())
    ):  # CHANGED: Use right_unsaved_repos_layout
        parent.right_unsaved_repos_layout.itemAt(i).widget().deleteLater()
    if hasattr(parent, "selected_repos"):
        parent.selected_repos.clear()
    if hasattr(parent, "saved_repos_data"):
        parent.saved_repos_data = []
    if hasattr(parent, "unsaved_repos_data"):
        parent.unsaved_repos_data = []
