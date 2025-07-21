import sys
import os
import logging
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget
from PyQt6.QtCore import QThreadPool
from utils.errors import show_error_message


class SourceProviderTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Organization Fetching Tool")
        self.setFixedSize(600, 600)
        
        self.init_state()
        self.init_ui()
        self.threadpool = QThreadPool()

    def init_state(self):
        """Initialize application state variables"""
        self.selected_users = []
        self.selected_teams = []
        self.selected_repos = []
        self.org_name = ""
        self.project_id = ""
        self.available_users = {}  
        self.repo_combo = set()
        self.selected_team_users = set()
        self.available_users_data=[]

    def init_ui(self):
        """Initialize UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        self.setup_tabs()

        stylesheet = self.load_stylesheet("main_py.style")
        if stylesheet:
            central_widget.setStyleSheet(stylesheet)
        else:
            logging.warning("Stylesheet not applied: File not found or empty.")

    def setup_tabs(self):
        """Initialize and load all application tabs"""
        try:
            from tabs.project_tab import setup_project_tab
            from tabs.user_tab import setup_user_tab
            from tabs.team_tab import setup_team_tab
            from tabs.team_member_tab import setup_team_member_tab
            from tabs.code_repository_tab import setup_repositories_tab
            from tabs.pull_request_tab import setup_pull_request_tab
            from tabs.data_access_tab import setup_data_access_tab 

            self.tab_widget.addTab(setup_project_tab(self), "Projects")
            self.tab_widget.addTab(setup_user_tab(self), "Users")
            self.tab_widget.addTab(setup_team_tab(self), "Teams")
            self.tab_widget.addTab(setup_team_member_tab(self), "Team Members")
            self.tab_widget.addTab(setup_repositories_tab(self), "Repositories")
            self.tab_widget.addTab(setup_pull_request_tab(self), "Pull Requests")
            self.tab_widget.addTab(setup_data_access_tab(self), "Data Access")
            self.tab_widget.setCurrentIndex(0)
        except Exception as e:
            logging.exception("Failed to load tabs")
            show_error_message(str(e))

    def load_stylesheet(self, filename: str) -> str:
        """Load stylesheet from file, supporting frozen executables"""
        try:
            base_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base_path, filename)

            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            logging.warning(f"Stylesheet file not found: {path}")
            show_error_message("Stylesheet file not found") 
            return ""
        except Exception as e:
            logging.exception("Error loading stylesheet")
            show_error_message(str(e)) 
            return ""
