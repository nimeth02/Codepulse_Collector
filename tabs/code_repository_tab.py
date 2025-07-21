from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QPushButton,
    QProgressBar,
    QListWidget,
    QSplitter,
)
from PyQt6.QtCore import Qt
from presenters.code_repository_presenter import (
    check_all_repositories,
    save_selected_repositories,
)
from presenters.common.on_tab_change_presenter import on_tab_changed


def setup_repositories_tab(parent):
    """Initialize the Repositories tab with split view."""
    tab = QWidget()
    main_layout = QVBoxLayout(tab)

    # Header
    header_label = QLabel("Organization Repositories")
    header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    header_label.setFixedHeight(40)
    main_layout.addWidget(header_label)

    # Create split view
    splitter = QSplitter(Qt.Orientation.Horizontal)

    # Left panel - Saved repositories
    saved_panel = QWidget()
    saved_layout = QVBoxLayout(saved_panel)
    saved_layout.addWidget(QLabel("Saved Repositories"))
    parent.left_saved_repos_list = (
        QListWidget()
    )  # CHANGED: Renamed to left_saved_repos_list
    saved_layout.addWidget(parent.left_saved_repos_list)

    # Right panel - Unsaved provider repositories
    provider_panel = QWidget()
    provider_layout = QVBoxLayout(provider_panel)
    provider_header_layout = QHBoxLayout()

    provider_header_layout.addWidget(QLabel("Unsaved Provider Repositories"))
    parent.check_all_repos_btn = QPushButton("Select All")
    parent.check_all_repos_btn.clicked.connect(lambda: check_all_repositories(parent))
    provider_header_layout.addWidget(parent.check_all_repos_btn)
    provider_layout.addLayout(provider_header_layout)
    parent.right_unsaved_repos_scroll = (
        QScrollArea()
    )  # CHANGED: Renamed to right_unsaved_repos_scroll
    parent.right_unsaved_repos_scroll.setWidgetResizable(True)
    parent.right_unsaved_repos_widget = QWidget()
    parent.right_unsaved_repos_layout = QVBoxLayout(parent.right_unsaved_repos_widget)
    parent.right_unsaved_repos_scroll.setWidget(parent.right_unsaved_repos_widget)
    provider_layout.addWidget(parent.right_unsaved_repos_scroll)

    # Add panels to splitter  
    splitter.addWidget(provider_panel)
    splitter.addWidget(saved_panel)
    splitter.setSizes([300, 300])
    main_layout.addWidget(splitter)

    # Save button
    parent.save_repos_btn = QPushButton("Save Selected Repositories")
    parent.save_repos_btn.clicked.connect(lambda: save_selected_repositories(parent))
    parent.save_repos_btn.setEnabled(False)
    main_layout.addWidget(parent.save_repos_btn)

    # Loading indicator
    parent.repos_progress_bar = QProgressBar()
    parent.repos_progress_bar.setVisible(False)
    main_layout.addWidget(parent.repos_progress_bar)

    # Connect tab change signal
    parent.tab_widget.currentChanged.connect(
        lambda index: on_tab_changed(parent, index)
    )

    return tab
