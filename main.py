import sys
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from app import GitHubTool

def main():
    try:
        app = QApplication(sys.argv)
        window = GitHubTool()
        window.show()
        sys.exit(app.exec())
        
    except Exception as e:
        print("ERROR:", traceback.format_exc())
        input("Press Enter to exit...")  # Keeps console open
        sys.exit(1)

if __name__ == "__main__":
    main() 