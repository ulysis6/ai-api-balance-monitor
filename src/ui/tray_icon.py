"""
系统托盘
"""

from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QApplication
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import Qt

from src.utils.config import Config


def create_icon(color: str = "#89b4fa") -> QIcon:
    """创建托盘图标"""
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # 画圆形背景
    painter.setBrush(QColor(color))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(2, 2, 28, 28)

    # 画文字
    painter.setPen(QColor("#1e1e2e"))
    painter.setFont(QFont("Arial", 14, QFont.Bold))
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "AI")

    painter.end()

    return QIcon(pixmap)


class TrayIcon(QSystemTrayIcon):
    """系统托盘图标"""

    def __init__(self, main_window, config: Config, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.config = config

        self.setIcon(create_icon())
        self.setToolTip("AI模型API余额监控")

        # 创建菜单
        self.create_menu()

        # 连接信号
        self.activated.connect(self.on_activated)

    def create_menu(self):
        """创建菜单"""
        menu = QMenu()

        # 显示主窗口
        show_action = QAction("显示主窗口", menu)
        show_action.triggered.connect(self.show_main_window)
        menu.addAction(show_action)

        # 立即刷新
        refresh_action = QAction("立即刷新", menu)
        refresh_action.triggered.connect(self.main_window.refresh_all)
        menu.addAction(refresh_action)

        menu.addSeparator()

        # 开机自启
        self.autostart_action = QAction("开机自启", menu)
        self.autostart_action.setCheckable(True)
        self.autostart_action.setChecked(self.config.autostart)
        self.autostart_action.triggered.connect(self.toggle_autostart)
        menu.addAction(self.autostart_action)

        menu.addSeparator()

        # 升级专业版
        upgrade_action = QAction("升级专业版", menu)
        upgrade_action.triggered.connect(self.show_upgrade)
        menu.addAction(upgrade_action)

        # 关于
        about_action = QAction("关于", menu)
        about_action.triggered.connect(self.show_about)
        menu.addAction(about_action)

        menu.addSeparator()

        # 退出
        quit_action = QAction("退出", menu)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)

        self.setContextMenu(menu)

    def on_activated(self, reason):
        """点击托盘图标"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_main_window()

    def show_main_window(self):
        """显示主窗口"""
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()

    def toggle_autostart(self, checked):
        """切换开机自启"""
        self.config.autostart = checked
        self.config.save()

        # 实际设置开机自启
        # TODO: 实现 Windows 开机自启

    def show_upgrade(self):
        """显示升级页面"""
        import webbrowser
        # TODO: 替换为实际的 Gumroad 链接
        webbrowser.open("https://gumroad.com")

    def show_about(self):
        """显示关于"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.about(
            self.main_window,
            "关于",
            "AI模型API余额监控 v2.0\n\n"
            "一站式监控所有 AI API 余额\n\n"
            "支持 14+ 家厂商\n"
            "支持 Coding Plan / Token Plan / Agent Plan 监控\n\n"
            "© 2026"
        )

    def quit_app(self):
        """退出应用"""
        QApplication.quit()
