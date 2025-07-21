import sys
import logging
from PyQt6.QtWidgets import QApplication
from app import SourceProviderTool
from utils.logging import setup_logging
from utils.errors import show_error_message

def main():
    setup_logging()
    try:
        app = QApplication(sys.argv)
        window = SourceProviderTool()
        window.show()
        sys.exit(app.exec())
        
    except Exception as e:
        logging.exception("Unhandled exception occurred")
        show_error_message(str(e)) 
        sys.exit(1)

if __name__ == "__main__":
    main()