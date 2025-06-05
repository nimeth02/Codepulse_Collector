from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget
from PyQt6.QtCore import Qt
import sys
import os

class GitHubTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GitHub Organization Fetching Tool")
        self.setFixedSize(600, 600)
        
        # Data storage
        self.selected_users = {}
        self.available_users={}
        self.selected_repos = set()
        self.repo_combo=set()
        self.selected_team_users = set()
        self.selected_teams = {}
        self.pending_fetches = set()
        self.org_members = []
        self.org_name = ""
        self.project_id = ""
        
        # Create ONE central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create and add tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Setup tabs
        self.setup_tabs()

        # Load stylesheet
        stylesheet = self.load_stylesheet("main_py.style")
        if stylesheet:
            central_widget.setStyleSheet(stylesheet)

    def setup_tabs(self):
        """Initialize all application tabs"""
        from tabs.project_tab import setup_project_tab
        from tabs.user_tab import setup_user_tab
        from tabs.team_tab import setup_team_tab
        from tabs.team_member_tab import setup_team_member_tab
        from tabs.code_repository_tab import setup_repositories_tab
        from tabs.pull_request_tab import setup_pull_request_tab
        from tabs.data_access_tab import setup_data_access_tab 
        
        # Add tabs
        self.tab_widget.addTab(setup_project_tab(self), "Projects")
        self.tab_widget.addTab(setup_user_tab(self), "Users")
        self.tab_widget.addTab(setup_team_tab(self), "Teams")
        self.tab_widget.addTab(setup_team_member_tab(self), "Team Members")
        self.tab_widget.addTab(setup_repositories_tab(self), "Repositories")
        self.tab_widget.addTab(setup_pull_request_tab(self), "Pull Requests")
        self.tab_widget.addTab(setup_data_access_tab(self), "Data Access")
        self.tab_widget.setCurrentIndex(0)

    def load_stylesheet(self, filename):
        """Load stylesheet from file"""
        try:
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(sys.executable)
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))

            stylesheet_path = os.path.join(base_path, filename)
            if os.path.exists(stylesheet_path):
                with open(stylesheet_path, "r", encoding="utf-8") as f:
                    return f.read()
            return ""
        except Exception as e:
            print(f"Stylesheet error: {e}")
            return ""