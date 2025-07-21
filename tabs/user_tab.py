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
from presenters.user_presenter import check_all_users, save_selected_users
from presenters.common.on_tab_change_presenter import on_tab_changed


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

    # Saved panel - Saved users
    saved_panel = QWidget()
    saved_layout = QVBoxLayout(saved_panel)
    saved_layout.addWidget(QLabel("Saved Users"))
    parent.saved_users_list = QListWidget()
    saved_layout.addWidget(parent.saved_users_list)

    # Provider panel - New provider users
    provider_panel = QWidget()
    provider_layout = QVBoxLayout(provider_panel)

    # Provider panel header with check all button
    provider_header_layout = QHBoxLayout()
    provider_header_layout.addWidget(QLabel("Available Provider Users"))
    parent.check_all_btn = QPushButton("Select All")
    parent.check_all_btn.clicked.connect(lambda: check_all_users(parent))
    provider_header_layout.addWidget(parent.check_all_btn)
    provider_layout.addLayout(provider_header_layout)

    parent.provider_users_scroll = QScrollArea()
    parent.provider_users_scroll.setWidgetResizable(True)
    parent.provider_users_widget = QWidget()
    parent.provider_users_layout = QVBoxLayout(parent.provider_users_widget)
    parent.provider_users_scroll.setWidget(parent.provider_users_widget)
    provider_layout.addWidget(parent.provider_users_scroll)

    # Add panels to splitter
    splitter.addWidget(provider_panel)
    splitter.addWidget(saved_panel)

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
        lambda index: on_tab_changed(parent, index)
    )

    return tab
