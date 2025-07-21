from PyQt6.QtWidgets import QMessageBox
from providers import ProviderType
from utils.errors import show_error_message, InputValidationError
from utils.threading import worker_spinner
from models.project_model import fetch_project_data


def fetch_and_save_organization(parent):
    """Fetch and save organization details using a background thread."""
    try:

        provider_type = ProviderType(parent.provider_combo.currentText().lower())
        pat = parent.pat_input.text().strip()
        org_name = parent.org_input.text().strip()
        validate_inputs(pat, org_name)

        # Disable UI and show spinner
        parent.fetch_btn.setEnabled(False)
        parent.clear_btn.setEnabled(False)

    except Exception as e:
        parent.org_progress_bar.setVisible(False)
        parent.fetch_btn.setEnabled(True)
        parent.clear_btn.setEnabled(True)
        show_error_message(parent, e, "Validation Error")
        return

    def task():
        return fetch_project_data(provider_type, org_name, pat)

    def on_success(result):
        parent.fetch_btn.setEnabled(True)
        parent.clear_btn.setEnabled(True)

        # Save provider state and update UI
        parent.current_provider = result["provider"]
        parent.project_id = result["project_id"]
        parent.org_name = result["org_name"]
        parent.org_members = []

        # Clear inputs but keep org/project ID
        parent.pat_input.clear()
        parent.org_input.clear()

        QMessageBox.information(
            parent, "Success", "Organization details saved successfully!"
        )

    def on_error(e):
        parent.fetch_btn.setEnabled(True)
        parent.clear_btn.setEnabled(True)
        show_error_message(parent, e, "Error")
        

    worker_spinner(
        parent=parent,
        progress_bar=parent.org_progress_bar,
        task_fn=task,
        on_success=on_success,
        on_error=on_error,
    )


def clear_organization_fields(parent):
    """Clear inputs in the Organization tab."""
    parent.pat_input.clear()
    parent.org_input.clear()
    parent.org_members = []
    parent.org_name = ""


def validate_inputs(pat, org_name):
    """Validate input fields and raise appropriate errors."""
    if not pat:
        raise InputValidationError("Please enter a Personal Access Token")
    if not org_name:
        raise InputValidationError("Please enter an organization name")


def update_provider_fields(parent):
    """Update UI fields based on selected provider."""

    provider = parent.provider_combo.currentText()

    if provider == ProviderType.GITHUB.value:
        parent.pat_input.setToolTip("Enter a GitHub PAT with 'read:org' scope")
        parent.org_input.setPlaceholderText("e.g., codefusionuom")
        parent.org_input.setToolTip("Enter the GitHub organization name")
    elif provider == ProviderType.AZURE_DEVOPS.value:
        parent.pat_input.setToolTip(
            "Enter an Azure DevOps PAT with appropriate permissions"
        )
        parent.org_input.setPlaceholderText("e.g., organization/project")
        parent.org_input.setToolTip("Enter in format 'organization/project'")
