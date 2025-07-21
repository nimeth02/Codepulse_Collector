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
    QComboBox,
)
from PyQt6.QtCore import Qt
from presenters.team_member_presenter import (
    save_selected_team_members,
    display_team_members,
    check_all_users,
)
from presenters.common.on_tab_change_presenter import on_tab_changed


def setup_team_member_tab(parent):
    """Initialize the Teams tab with split view."""
    tab = QWidget()
    main_layout = QVBoxLayout(tab)

    # Header
    header_label = QLabel("Team Members")
    header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    header_label.setFixedHeight(40)
    main_layout.addWidget(header_label)

    # Create split view
    splitter = QSplitter(Qt.Orientation.Horizontal)

    # Left panel - Saved teams and members
    saved_panel = QWidget()
    saved_layout = QVBoxLayout(saved_panel)
    saved_layout.addWidget(QLabel("Saved Teams"))

    # Team selection dropdown
    parent.saved_teams_combo = QComboBox()
    parent.saved_teams_combo.addItem("Select a team")
    parent.saved_teams_combo.currentIndexChanged.connect(
        lambda index: display_team_members(parent, index)
    )
    saved_layout.addWidget(parent.saved_teams_combo)

    # Team members list
    parent.team_members_list = QListWidget()
    saved_layout.addWidget(parent.team_members_list)

    # Right panel - Available users
    provider_panel = QWidget()
    provider_layout = QVBoxLayout(provider_panel)

    # Right panel header with select all button
    provider_header_layout = QHBoxLayout()
    provider_header_layout.addWidget(QLabel("Available Users"))
    parent.check_all_users_btn = QPushButton("Select All")
    parent.check_all_users_btn.clicked.connect(lambda: check_all_users(parent))
    provider_header_layout.addWidget(parent.check_all_users_btn)
    provider_layout.addLayout(provider_header_layout)

    parent.available_users_scroll = QScrollArea()
    parent.available_users_scroll.setWidgetResizable(True)
    parent.available_users_widget = QWidget()
    parent.available_users_layout = QVBoxLayout(parent.available_users_widget)
    parent.available_users_scroll.setWidget(parent.available_users_widget)
    provider_layout.addWidget(parent.available_users_scroll)

    # Add panels to splitter
    splitter.addWidget(provider_panel)
    splitter.addWidget(saved_panel)
    splitter.setSizes([300, 300])
    main_layout.addWidget(splitter)

    # Save button
    parent.save_team_members_btn = QPushButton("Add Selected Users to Team")
    parent.save_team_members_btn.clicked.connect(
        lambda: save_selected_team_members(parent)
    )
    parent.save_team_members_btn.setEnabled(False)
    main_layout.addWidget(parent.save_team_members_btn)

    # Loading indicator
    parent.team_members_progress_bar = QProgressBar()
    parent.team_members_progress_bar.setVisible(False)
    main_layout.addWidget(parent.team_members_progress_bar)

    # Connect tab change signal
    parent.tab_widget.currentChanged.connect(
        lambda index: on_tab_changed(parent, index)
    )

    return tab
