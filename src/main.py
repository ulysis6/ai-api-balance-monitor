"""
AI模型API余额监控 v2.0
主程序入口
"""

import sys
import os
import traceback

# 打包后或直接运行时，将 src 目录加入 sys.path
if getattr(sys, 'frozen', False):
    # PyInstaller 打包后
    base_dir = os.path.dirname(sys.executable)
    internal_dir = os.path.join(base_dir, '_internal')
    src_dir = os.path.join(internal_dir, 'src')
    if os.path.exists(src_dir):
        sys.path.insert(0, internal_dir)
    else:
        sys.path.insert(0, base_dir)
else:
    # 开发环境
    src_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(src_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

try:
    from PyQt5.QtWidgets import QApplication
    from src.ui.main_window import MainWindow
    from src.ui.tray_icon import TrayIcon
    from src.utils.config import Config

    def main():
        """主函数"""
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

except Exception as e:
    # 写日志到 exe 同目录
    log_path = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else '.', 'error.log')
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(traceback.format_exc())
    raise
