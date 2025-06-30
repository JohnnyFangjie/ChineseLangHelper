"""
Main application entry point for the Chinese Learning Helper
"""
import sys
from PySide6.QtWidgets import QApplication
from controllers.controllers import MainController


def main():
    """Main entry point for the application"""
    # Create QApplication instance
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Set application metadata
    app.setApplicationName("Chinese Learning Helper")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Chinese Learning Tools")
    
    # Create and show main controller/window
    controller = MainController()
    controller.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()