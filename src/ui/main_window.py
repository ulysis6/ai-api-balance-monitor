"""
主窗口 UI
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGraphicsDropShadowEffect,
    QSystemTrayIcon, QFrame
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QColor

from src.providers import ALL_PROVIDERS, FREE_MAX_PROVIDERS
from src.providers.base import ProviderStatus, BalanceInfo
from src.utils.config import Config
from src.license.validator import check_license_valid

DEFAULT_VISIBLE_COUNT = 5


class RefreshThread(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, providers_config: dict, is_pro: bool):
        super().__init__()
        self.providers_config = providers_config
        self.is_pro = is_pro

    def run(self):
        results = {}
        enabled_count = 0

        for provider_cls in ALL_PROVIDERS:
            provider = provider_cls()
            config = self.providers_config.get(provider.name, {"enabled": False})

            if not config.get("enabled", False):
                continue

            status = ProviderStatus(
                name=provider.display_name,
                icon_color=provider.icon_color,
                auth_type=provider.auth_type,
                configured=provider.validate_config(config),
                enabled=True
            )

            if status.configured:
                if not self.is_pro:
                    enabled_count += 1
                    if enabled_count > FREE_MAX_PROVIDERS:
                        status.balance = BalanceInfo(error="需升级Pro")
                        results[provider.name] = status
                        continue

                status.balance = provider.get_balance(config)
                if provider.has_plans:
                    status.plans = provider.get_plans(config)
            else:
                status.balance = BalanceInfo(error="未配置")

            results[provider.name] = status

        self.finished.emit(results)


class BalanceCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(49, 50, 68, 0.6);
                border-radius: 10px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)

        self.name_label = QLabel("--")
        layout.addWidget(self.name_label)

        layout.addStretch()

        self.balance_label = QLabel("--")
        self.balance_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.balance_label)

    def update_status(self, status: ProviderStatus):
        self.name_label.setText(status.name)
        self.name_label.setStyleSheet(f"color: {status.icon_color}; font-weight: bold; font-size: 18px;")

        if status.balance:
            if status.balance.error:
                error = status.balance.error
                if error == "未配置":
                    self.balance_label.setText(error)
                    self.balance_label.setStyleSheet("color: #6c7086; font-size: 18px; font-weight: bold;")
                else:
                    self.balance_label.setText(error)
                    self.balance_label.setStyleSheet("color: #f38ba8; font-size: 16px; font-weight: bold;")
            elif status.balance.balance is not None:
                balance = status.balance.balance
                self.balance_label.setText(f"{balance:.2f}")
                color = "#a6e3a1" if balance > 10 else "#f9e2af" if balance > 1 else "#f38ba8"
                self.balance_label.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold;")


class MainWindow(QWidget):
    def __init__(self, config: Config, tray_icon: QSystemTrayIcon = None):
        super().__init__()
        self.config = config
        self.tray_icon = tray_icon
        self.cards = {}
        self.card_order = []
        self.visible_order = []
        self.expanded = False
        self.refresh_thread = None
        self.alerted_providers = set()
        self.version_label = None  # 版本标签引用

        self.init_ui()
        self.setup_timer()
        self.refresh_all()

    def init_ui(self):
        self.setWindowTitle("API 余额监控")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 检查窗口位置是否在可见屏幕内
        x, y = self.config.window_x, self.config.window_y
        from PyQt5.QtWidgets import QDesktopWidget
        desktop = QDesktopWidget()
        screen_rect = desktop.availableGeometry()
        if x < 0 or y < 0 or x > screen_rect.width() - 100 or y > screen_rect.height() - 100:
            x, y = 100, 100
        self.move(x, y)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.container = QWidget()
        self.container.setObjectName("container")
        self.container.setStyleSheet("""
            #container {
                background-color: rgba(30, 30, 46, 235);
                border-radius: 14px;
                border: 1px solid rgba(69, 71, 90, 0.8);
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)

        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(14)
        self.container_layout.setContentsMargins(20, 14, 20, 14)

        title_bar = self.create_title_bar()
        self.container_layout.addWidget(title_bar)

        self.cards_widget = QWidget()
        self.cards_widget.setStyleSheet("background-color: transparent;")
        self.cards_layout = QVBoxLayout(self.cards_widget)
        self.cards_layout.setSpacing(14)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)

        for provider_cls in ALL_PROVIDERS:
            provider = provider_cls()
            card = BalanceCard()
            self.cards[provider.name] = card
            self.card_order.append(provider.name)
            self.cards_layout.addWidget(card)
            card.hide()

        self.cards_layout.addStretch()
        self.container_layout.addWidget(self.cards_widget)

        self.toggle_btn = QPushButton("▼ 显示全部")
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(49, 50, 68, 0.6);
                color: #6c7086;
                border: none;
                border-radius: 4px;
                padding: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(69, 71, 90, 0.8);
                color: #cdd6f4;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_expand)
        self.toggle_btn.hide()
        self.container_layout.addWidget(self.toggle_btn)

        self.status_label = QLabel("等待更新...")
        self.status_label.setStyleSheet("color: #6c7086; font-size: 11px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.container_layout.addWidget(self.status_label)

        main_layout.addWidget(self.container)
        self.update_size()

    def create_title_bar(self):
        title_bar = QWidget()
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("API 余额监控")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #cdd6f4;")
        title_layout.addWidget(title)

        title_layout.addStretch()

        # 保存为实例变量，方便后续更新
        self.update_version_label()
        title_layout.addWidget(self.version_label)

        buttons = [
            ("⚙", self.show_settings, "#313244"),
            ("🔄", self.refresh_all, "#313244"),
            ("✕", self.close, "#f38ba8")
        ]

        for text, action, hover in buttons:
            btn = QPushButton(text)
            btn.setFixedSize(26, 26)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: #6c7086;
                    font-size: 15px;
                    border: none;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    background-color: {hover};
                    color: #cdd6f4;
                }}
            """)
            btn.clicked.connect(action)
            title_layout.addWidget(btn)

        return title_bar

    def update_version_label(self):
        """更新版本标签显示"""
        # 检查License状态
        is_valid, message, info = check_license_valid(self.config)
        
        if is_valid and info.get("type") == "pro":
            version = "Pro"
            # 金色背景 + 深灰色文字（反显效果）
            version_style = """
                background-color: #f9e2af;
                color: #1e1e2e;
                font-size: 9px;
                font-weight: bold;
                padding: 1px 5px;
                border-radius: 3px;
            """
        else:
            version = "Free"
            version_style = """
                background-color: rgba(49, 50, 68, 0.8);
                color: #6c7086;
                font-size: 9px;
                padding: 1px 5px;
                border-radius: 3px;
            """
        
        if self.version_label is None:
            self.version_label = QLabel(version)
        
        self.version_label.setText(version)
        self.version_label.setStyleSheet(version_style)

    def toggle_expand(self):
        self.expanded = not self.expanded
        if self.expanded:
            self.toggle_btn.setText("▲ 折叠")
        else:
            self.toggle_btn.setText("▼ 显示全部")
        self.update_visible_cards()
        self.update_size()

    def update_visible_cards(self):
        visible_list = self.visible_order if self.expanded else self.visible_order[:DEFAULT_VISIBLE_COUNT]
        
        for name in self.card_order:
            card = self.cards.get(name)
            if card:
                if name in visible_list:
                    card.show()
                else:
                    card.hide()

        if len(self.visible_order) > DEFAULT_VISIBLE_COUNT:
            self.toggle_btn.show()
        else:
            self.toggle_btn.hide()

    def update_size(self):
        if self.expanded:
            visible_count = len(self.visible_order)
        else:
            visible_count = min(len(self.visible_order), DEFAULT_VISIBLE_COUNT)
        
        base_height = 14 + 30 + 14
        card_height = 38 + 14
        bottom_height = 15 + 14
        
        min_count = max(visible_count, DEFAULT_VISIBLE_COUNT)
        height = base_height + min_count * card_height + bottom_height
        
        if len(self.visible_order) > DEFAULT_VISIBLE_COUNT:
            height += 28
        
        self.setFixedSize(320, height)

    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_all)
        self.timer.start(self.config.refresh_interval)

    def refresh_all(self):
        from datetime import datetime
        self.status_label.setText(f"正在更新... {datetime.now().strftime('%H:%M:%S')}")

        # 更新版本标签
        self.update_version_label()

        providers_config = {}
        self.visible_order = []

        for provider_cls in ALL_PROVIDERS:
            provider = provider_cls()
            config = self.config.get_provider_config(provider.name)
            providers_config[provider.name] = config

            if config.get("enabled", False):
                self.visible_order.append(provider.name)

        for name, card in self.cards.items():
            card.hide()

        for name in self.visible_order:
            card = self.cards.get(name)
            if card:
                provider = next((p for p in ALL_PROVIDERS if p.name == name), None)
                if provider:
                    card.update_status(ProviderStatus(
                        name=provider.display_name,
                        icon_color=provider.icon_color,
                        balance=BalanceInfo(error="加载中...")
                    ))

        self.update_visible_cards()
        self.update_size()

        self.refresh_thread = RefreshThread(providers_config, self.config.is_pro)
        self.refresh_thread.finished.connect(self.on_refresh_finished)
        self.refresh_thread.start()

    def on_refresh_finished(self, results: dict):
        from datetime import datetime

        alert_messages = []

        for name, status in results.items():
            card = self.cards.get(name)
            if card:
                card.update_status(status)

            if (status.balance and 
                status.balance.balance is not None and 
                status.balance.error is None):
                
                balance = status.balance.balance
                threshold = self.config.alert_threshold
                
                if balance < threshold and name not in self.alerted_providers:
                    alert_messages.append(f"{status.name}: {balance:.2f} 元")
                    self.alerted_providers.add(name)
                elif balance >= threshold:
                    self.alerted_providers.discard(name)

        self.status_label.setText(f"更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        if alert_messages and self.tray_icon:
            self.send_alert(alert_messages)

    def send_alert(self, messages: list):
        title = "⚠️ 余额不足提醒"
        text = "\n".join(messages)
        self.tray_icon.showMessage(title, text, 1, 5000)

    def show_settings(self):
        from .config_dialog import ConfigDialog
        dialog = ConfigDialog(self.config, self)
        dialog.exec_()
        # 无论是否点保存，都更新版本标签（激活License后需要）
        self.update_version_label()
        self.refresh_all()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_position'):
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.config.window_x = self.x()
            self.config.window_y = self.y()
            self.config.save()

    def closeEvent(self, event):
        self.config.window_x = self.x()
        self.config.window_y = self.y()
        self.config.save()
        event.accept()
