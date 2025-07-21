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
from presenters.team_presenter import save_selected_teams
from presenters.common.on_tab_change_presenter import on_tab_changed


def setup_team_tab(parent):
    """Create and return the user tab"""
    tab = QWidget()
    main_layout = QVBoxLayout(tab)

    # Header
    header_label = QLabel("Organization Teams")
    header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    header_label.setFixedHeight(40)
    main_layout.addWidget(header_label)

    # Create split view
    splitter = QSplitter(Qt.Orientation.Horizontal)

    # Left panel - Saved users
    saved_panel = QWidget()
    saved_layout = QVBoxLayout(saved_panel)
    saved_layout.addWidget(QLabel("Saved Teams"))
    parent.saved_teams_list = QListWidget()
    saved_layout.addWidget(parent.saved_teams_list)

    # Right panel - New provider users
    provider_panel = QWidget()
    provider_layout = QVBoxLayout(provider_panel)
    provider_layout.addWidget(QLabel("Available Provider Teams"))
    parent.provider_teams_scroll = QScrollArea()
    parent.provider_teams_scroll.setWidgetResizable(True)
    parent.provider_teams_widget = QWidget()
    parent.provider_teams_layout = QVBoxLayout(parent.provider_teams_widget)
    parent.provider_teams_scroll.setWidget(parent.provider_teams_widget)
    provider_layout.addWidget(parent.provider_teams_scroll)

    # Add panels to splitter
    splitter.addWidget(provider_panel)
    splitter.addWidget(saved_panel)
    splitter.setSizes([300, 300])
    main_layout.addWidget(splitter)

    # Add creation button row
    button_row = QHBoxLayout()
    main_layout.addLayout(button_row)

    # Save button
    parent.save_teams_btn = QPushButton("Save Selected Teams")
    parent.save_teams_btn.clicked.connect(lambda: save_selected_teams(parent))
    parent.save_teams_btn.setEnabled(False)
    main_layout.addWidget(parent.save_teams_btn)

    # Loading indicator
    parent.teams_progress_bar = QProgressBar()
    parent.teams_progress_bar.setVisible(False)
    main_layout.addWidget(parent.teams_progress_bar)

    # Connect tab change signal
    parent.tab_widget.currentChanged.connect(
        lambda index: on_tab_changed(parent, index)
    )

    return tab
