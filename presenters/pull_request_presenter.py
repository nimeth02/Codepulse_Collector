from PyQt6.QtWidgets import QMessageBox, QApplication
import requests
from utils.errors import (
    show_error_message,
    APIError,
    NetworkError,
    InputValidationError,
)
from datetime import datetime
from utils.threading import worker_spinner
from models.pull_request_model import (
    fetch_pull_request_data,
    fetch_last_pr_data,
    fetch_and_save_pull_requests,
)

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
                "%Y-%m-%dT%H:%M:%S",
            ):
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            raise ValueError(f"Invalid date format: {date_str}")
        except Exception as e:
            print(f"Date parsing error: {e}")
            raise


def load_pull_request_data(parent):
    """Load saved repositories and users in the background."""

    def task():
        """Background thread: fetch repos and users from APIs"""
        return fetch_pull_request_data(
            parent.project_id, parent.org_name, parent.current_provider
        )

    def on_success(result):
        parent.repo_combo.clear()
        parent.repo_combo.addItem("Select a repository")
        parent.saved_repos_data = result["saved_repos"]
        parent.saved_users = result["saved_users"]

        for repo in result["saved_repos"]:
            name = repo.get("codeRepositoryName", "Unknown Repo")
            full_name = repo.get("fullName", "Unknown/Unknown")
            parent.repo_combo.addItem(f"{name} ({full_name})", repo)

    def on_error(e):
        from requests.exceptions import ConnectionError, Timeout

        if isinstance(e, ConnectionError):
            msg = "Unable to connect to backend server."
        elif isinstance(e, Timeout):
            msg = "Request timed out. Please try again."
        else:
            msg = str(e)

        QMessageBox.critical(parent, "Error", f"Failed to load users:\n{msg}")

    # Launch in background
    worker_spinner(
        parent=parent,
        progress_bar=parent.pr_progress_bar,
        task_fn=task,
        on_success=on_success,
        on_error=on_error,
    )


def fetch_last_pull_request(parent):
    """Fetch the last pull request using a background thread."""

    current_index = parent.repo_combo.currentIndex()
    if current_index <= 0:
        parent.last_pr_label.setText("Last PR Created: Select a repository")
        parent.fetch_prs_btn.setEnabled(False)
        parent.last_pr_date = None
        parent.selected_repo_data = None
        return

    repo_data = parent.repo_combo.itemData(current_index)
    repo_id = repo_data.get("codeRepositoryId")
    full_name = repo_data.get("fullName")

    if not repo_id:
        QMessageBox.critical(
            parent, "Error", "Selected repository has no codeRepositoryId"
        )
        return

    parent.selected_repo_data = repo_data

    def task():
        """Runs in background thread"""
        return fetch_last_pr_data(repo_id)

    def on_success(last_pr):

        if last_pr:
            if "prCreatedAt" in last_pr:
                pr_created_at = last_pr["prCreatedAt"]
                parsed_date = parse_iso_date(pr_created_at)
                parent.last_pr_label.setText(
                    f"Last PR Created: {parsed_date.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                parent.last_pr_date = parsed_date
                parent.fetch_prs_btn.setEnabled(True)
            else:
                parent.last_pr_label.setText("Last PR Created: Invalid PR data format")
                parent.fetch_prs_btn.setEnabled(False)
                parent.last_pr_date = None
        else:
            parent.last_pr_label.setText("Last PR Created: No previous pull requests")
            parent.fetch_prs_btn.setEnabled(True)
            parent.last_pr_date = None

    def on_error(e):
        parent.last_pr_date = None

        if isinstance(e, requests.exceptions.HTTPError):
            if e.response.status_code == 404:
                parent.last_pr_label.setText(
                    "Last PR Created: No previous pull requests"
                )
                parent.fetch_prs_btn.setEnabled(True)
            else:
                parent.last_pr_label.setText("Last PR Created: Error fetching data")
                QMessageBox.critical(
                    parent,
                    "API Error",
                    f"Failed to fetch PRs (HTTP {e.response.status_code})",
                )
                parent.fetch_prs_btn.setEnabled(False)
        else:
            parent.last_pr_label.setText("Last PR Created: Error fetching data")
            show_error_message(parent, e, "Unexpected Error")
            parent.fetch_prs_btn.setEnabled(False)

    worker_spinner(
        parent=parent,
        progress_bar=parent.pr_progress_bar,
        task_fn=task,
        on_success=on_success,
        on_error=on_error,
    )


def fetch_and_save_new_pull_requests(parent):
    """Fetch and save PRs using background thread."""
    if not parent.selected_repo_data:
        show_error_message(
            parent, InputValidationError("No repository selected."), "Input Error"
        )
        return

    parent.pr_progress_bar.setVisible(True)
    parent.pr_progress_bar.setRange(0, 0)
    parent.fetch_prs_btn.setEnabled(False)
    QApplication.processEvents()

    # Date filter (for incremental PR fetch)
    filter_date = getattr(parent, "last_pr_date", None)

    def task():
        """This runs in a background thread"""
        return fetch_and_save_pull_requests(
            parent.current_provider,
            parent.saved_users,
            parent.selected_repo_data,
            filter_date,
        )

    def on_success(result):
        parent.pr_progress_bar.setVisible(False)
        parent.fetch_prs_btn.setEnabled(True)

        pr_payload = result.get("pr_payload", [])
        response = result.get("response")

        if not pr_payload:
            msg = (
                "No pull requests found."
                if not filter_date
                else "No new pull requests found since the last fetch."
            )
            QMessageBox.information(parent, "No PRs", msg)
            return

        response_data = response.json()

        if response_data.get("success"):
            QMessageBox.information(
                parent, "Success", f"Saved {len(pr_payload)} pull requests successfully"
            )
            fetch_last_pull_request(parent)
        else:
            raise APIError(response_data.get("message", "Failed to save pull requests"))

    def on_error(e):
        parent.pr_progress_bar.setVisible(False)
        parent.fetch_prs_btn.setEnabled(True)

        if isinstance(e, InputValidationError):
            show_error_message(parent, e, "Input Error")
        elif isinstance(e, APIError):
            show_error_message(parent, e, "API Error")
        elif isinstance(e, requests.exceptions.RequestException):
            show_error_message(
                parent, NetworkError("Network error occurred", str(e)), "Network Error"
            )
        else:
            show_error_message(parent, e, "Unexpected Error")

    # Start background task
    worker_spinner(
        parent=parent,
        progress_bar=parent.pr_progress_bar,
        task_fn=task,
        on_success=on_success,
        on_error=on_error,
    )
