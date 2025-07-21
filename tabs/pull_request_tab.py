from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QProgressBar,
)
from PyQt6.QtCore import Qt
from presenters.pull_request_presenter import (
    fetch_and_save_new_pull_requests,
    fetch_last_pull_request,
)
from presenters.common.on_tab_change_presenter import on_tab_changed


def setup_pull_request_tab(parent):
    """Initialize the Pull Request tab."""
    print("Setting up pull request tab")
    tab = QWidget()
    main_layout = QVBoxLayout(tab)

    # Header
    header_label = QLabel("Pull Requests")
    header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    header_label.setFixedHeight(40)
    main_layout.addWidget(header_label)

    # Repository selection
    main_layout.addWidget(QLabel("Select Repository:"))
    parent.repo_combo = QComboBox()
    parent.repo_combo.addItem("Select a repository")
    parent.repo_combo.currentIndexChanged.connect(
        lambda: fetch_last_pull_request(parent)
    )
    main_layout.addWidget(parent.repo_combo)

    # Last pull request label
    parent.last_pr_label = QLabel("Last PR Created: Not fetched")
    main_layout.addWidget(parent.last_pr_label)

    # Fetch pull requests button
    parent.fetch_prs_btn = QPushButton("Fetch and Save New Pull Requests")
    parent.fetch_prs_btn.clicked.connect(
        lambda: fetch_and_save_new_pull_requests(parent)
    )
    parent.fetch_prs_btn.setEnabled(False)
    main_layout.addWidget(parent.fetch_prs_btn)

    # Loading indicator
    parent.pr_progress_bar = QProgressBar()
    parent.pr_progress_bar.setVisible(False)
    main_layout.addWidget(parent.pr_progress_bar)

    # Stretch to push content up
    main_layout.addStretch()

    # Connect tab change signal
    parent.tab_widget.currentChanged.connect(
        lambda index: on_tab_changed(parent, index)
    )

    return tab
