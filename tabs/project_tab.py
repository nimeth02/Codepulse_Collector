from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QProgressBar,
    QMessageBox,
    QComboBox,
    QApplication,
)
from PyQt6.QtCore import Qt
from services.backend.save_organization_data_service import (
    save_organization_data_service,
)
from providers import ProviderFactory, ProviderType
from presenters.project_presenter import (
    update_provider_fields,
    fetch_and_save_organization,
    clear_organization_fields,
)


def setup_project_tab(parent):
    """Set up the Project/Organization tab with all functionality."""
    tab = QWidget()
    layout = QVBoxLayout(tab)

    header_label = QLabel("Organization Fetcher")
    header_label.setObjectName("headerLabel")
    header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(header_label)

    layout.addWidget(QLabel("Source Control Provider:"))
    parent.provider_combo = QComboBox()
    parent.provider_combo.addItems([pt.value for pt in ProviderType])
    parent.provider_combo.currentTextChanged.connect(
        lambda: update_provider_fields(parent)
    )
    layout.addWidget(parent.provider_combo)

    # PAT input
    layout.addWidget(QLabel("Personal Access Token:"))
    parent.pat_input = QLineEdit()
    parent.pat_input.setPlaceholderText("Enter your  PAT")
    parent.pat_input.setEchoMode(QLineEdit.EchoMode.Password)
    parent.pat_input.setToolTip("Enter a  PAT with 'read:org' scope")
    layout.addWidget(parent.pat_input)

    # Organization input
    layout.addWidget(QLabel("Organization Name:"))
    parent.org_input = QLineEdit()
    parent.org_input.setPlaceholderText("e.g., codefusionuom")
    parent.org_input.setToolTip("Enter the  organization name")
    layout.addWidget(parent.org_input)

    # Buttons layout
    button_layout = QHBoxLayout()
    parent.fetch_btn = QPushButton("Fetch & Save")
    parent.fetch_btn.setToolTip("Fetch organization data and members")
    parent.fetch_btn.clicked.connect(lambda: fetch_and_save_organization(parent))
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
