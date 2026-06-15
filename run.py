"""
打包入口 - 给 PyInstaller 用
"""
import sys
import os

# 将项目根目录加入 sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from PyQt5.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.ui.tray_icon import TrayIcon
from src.utils.config import Config


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    config = Config()
    main_window = MainWindow(config)

    tray_icon = TrayIcon(main_window, config)
    tray_icon.show()

    main_window.tray_icon = tray_icon
    main_window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
