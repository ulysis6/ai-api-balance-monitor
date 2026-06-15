"""
配置对话框
"""

import webbrowser
from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QCheckBox, QScrollArea,
    QWidget, QFrame, QMessageBox, QSpinBox, QDoubleSpinBox,
    QTabWidget
)
from PyQt5.QtCore import Qt

from src.providers import ALL_PROVIDERS, FREE_MAX_PROVIDERS
from src.utils.config import Config
from src.utils.autostart import enable_autostart, disable_autostart, is_autostart_enabled
from src.license.validator import validate_license_key, check_license_valid, format_expire_info


class ProviderConfigWidget(QFrame):
    def __init__(self, provider, config: Config, parent=None):
        super().__init__(parent)
        self.provider = provider
        self.config = config
        self.provider_config = config.get_provider_config(provider.name)

        self.init_ui()
        self.load_config()

    def init_ui(self):
        self.setObjectName("providerConfig")
        self.setStyleSheet(f"""
            #providerConfig {{
                background-color: rgba(49, 50, 68, 0.6);
                border-radius: 6px;
                border-left: 3px solid {self.provider.icon_color};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(10, 8, 10, 8)

        header = QHBoxLayout()

        self.enable_check = QCheckBox()
        self.enable_check.setFixedSize(20, 20)
        self.enable_check.setStyleSheet("""
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #6c7086;
                border-radius: 3px;
                background-color: transparent;
            }
            QCheckBox::indicator:checked {
                background-color: #89b4fa;
                border-color: #89b4fa;
            }
            QCheckBox::indicator:hover {
                border-color: #89b4fa;
            }
        """)
        header.addWidget(self.enable_check)

        name_label = QLabel(self.provider.display_name)
        name_label.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {self.provider.icon_color};")
        header.addWidget(name_label)

        header.addStretch()

        if self.provider.get_auth_url():
            link_btn = QPushButton("🔑 Key")
            link_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #89b4fa;
                    font-size: 11px;
                    border: none;
                }
                QPushButton:hover {
                    text-decoration: underline;
                }
            """)
            link_btn.clicked.connect(lambda: webbrowser.open(self.provider.get_auth_url()))
            header.addWidget(link_btn)

        if self.provider.get_cookie_login_url():
            cookie_btn = QPushButton("🌐 登录")
            cookie_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #a6e3a1;
                    font-size: 11px;
                    border: none;
                }
                QPushButton:hover {
                    text-decoration: underline;
                }
            """)
            cookie_btn.clicked.connect(lambda: webbrowser.open(self.provider.get_cookie_login_url()))
            header.addWidget(cookie_btn)

        layout.addLayout(header)

        self.input = QLineEdit()
        if self.provider.auth_type == "api_key":
            self.input.setPlaceholderText(f"输入 {self.provider.display_name} API Key...")
        else:
            self.input.setPlaceholderText(f"输入 {self.provider.display_name} Cookie...")
        self.input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input)

    def load_config(self):
        self.enable_check.setChecked(self.provider_config.get("enabled", False))
        if self.provider.auth_type == "api_key":
            self.input.setText(self.provider_config.get("api_key", ""))
        else:
            self.input.setText(self.provider_config.get("cookie", ""))

    def save_config(self):
        cfg = {"enabled": self.enable_check.isChecked()}
        if self.provider.auth_type == "api_key":
            cfg["api_key"] = self.input.text().strip()
        else:
            cfg["cookie"] = self.input.text().strip()
        self.config.set_provider_config(self.provider.name, cfg)


class ConfigDialog(QDialog):
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.provider_widgets = []

        self.setWindowTitle("AI模型API余额监控 - 配置")
        self.setFixedSize(500, 550)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QLabel {
                color: #cdd6f4;
            }
            QLineEdit {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 6px;
                color: #cdd6f4;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #89b4fa;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #74c7ec;
            }
            QTabWidget::pane {
                border: 1px solid #45475a;
                border-radius: 4px;
                background-color: #1e1e2e;
            }
            QTabBar::tab {
                background-color: #313244;
                color: #cdd6f4;
                padding: 8px 16px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background-color: #1e1e2e;
                border-bottom: 2px solid #89b4fa;
            }
            QSpinBox, QDoubleSpinBox {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 6px;
                color: #cdd6f4;
                font-size: 13px;
            }
        """)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        tabs = QTabWidget()

        # 厂商配置标签页
        providers_tab = QWidget()
        providers_layout = QVBoxLayout(providers_tab)
        providers_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: rgba(49, 50, 68, 0.3);
                width: 5px;
                border-radius: 2px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(108, 112, 134, 0.5);
                border-radius: 2px;
            }
        """)

        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: transparent;")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(8)

        if not self.config.is_pro:
            tip = QLabel(f"💡 免费版最多启用 {FREE_MAX_PROVIDERS} 个厂商，升级专业版解锁全部")
            tip.setStyleSheet("color: #f9e2af; font-size: 12px;")
            tip.setWordWrap(True)
            scroll_layout.addWidget(tip)

        for provider_cls in ALL_PROVIDERS:
            provider = provider_cls()
            widget = ProviderConfigWidget(provider, self.config)
            self.provider_widgets.append(widget)
            scroll_layout.addWidget(widget)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        providers_layout.addWidget(scroll)

        tabs.addTab(providers_tab, "厂商配置")

        # 设置标签页
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        settings_layout.setSpacing(15)

        interval_layout = QHBoxLayout()
        interval_label = QLabel("刷新间隔:")
        interval_label.setStyleSheet("color: #cdd6f4; font-size: 13px;")
        interval_layout.addWidget(interval_label)
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setValue(self.config.refresh_interval // 60000)
        self.interval_spin.setSuffix(" 分钟")
        interval_layout.addWidget(self.interval_spin)
        interval_layout.addStretch()
        settings_layout.addLayout(interval_layout)

        alert_layout = QHBoxLayout()
        self.alert_check = QCheckBox("余额低于阈值时提醒")
        self.alert_check.setChecked(True)
        self.alert_check.setStyleSheet("""
            QCheckBox {
                color: #cdd6f4;
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #6c7086;
                border-radius: 3px;
                background-color: transparent;
            }
            QCheckBox::indicator:checked {
                background-color: #89b4fa;
                border-color: #89b4fa;
            }
        """)
        alert_layout.addWidget(self.alert_check)
        self.alert_spin = QDoubleSpinBox()
        self.alert_spin.setRange(0, 1000)
        self.alert_spin.setValue(self.config.alert_threshold)
        self.alert_spin.setSuffix(" 元")
        alert_layout.addWidget(self.alert_spin)
        alert_layout.addStretch()
        settings_layout.addLayout(alert_layout)

        # 开机启动
        autostart_layout = QHBoxLayout()
        self.autostart_check = QCheckBox("开机自动启动")
        self.autostart_check.setChecked(is_autostart_enabled())
        self.autostart_check.setStyleSheet("""
            QCheckBox {
                color: #cdd6f4;
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #6c7086;
                border-radius: 3px;
                background-color: transparent;
            }
            QCheckBox::indicator:checked {
                background-color: #89b4fa;
                border-color: #89b4fa;
            }
        """)
        autostart_layout.addWidget(self.autostart_check)
        autostart_layout.addStretch()
        settings_layout.addLayout(autostart_layout)

        settings_layout.addStretch()
        tabs.addTab(settings_tab, "设置")

        # License 标签页
        license_tab = QWidget()
        license_layout = QVBoxLayout(license_tab)
        license_layout.setSpacing(12)

        # 当前状态
        self.license_status = QLabel()
        self.update_license_status()
        license_layout.addWidget(self.license_status)

        # License Key 输入
        license_label = QLabel("输入新的 License Key:")
        license_label.setStyleSheet("color: #cdd6f4; font-size: 13px;")
        license_layout.addWidget(license_label)

        self.license_input = QLineEdit()
        self.license_input.setPlaceholderText("AIM-XXXX-XXXX-XXXX-XXXX")
        self.license_input.setText(self.config.license_key)
        license_layout.addWidget(self.license_input)

        activate_btn = QPushButton("激活")
        activate_btn.clicked.connect(self.activate_license)
        license_layout.addWidget(activate_btn)

        license_layout.addStretch()
        tabs.addTab(license_tab, "License")

        layout.addWidget(tabs)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #45475a;
                color: #cdd6f4;
            }
            QPushButton:hover {
                background-color: #585b70;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_and_accept)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def update_license_status(self):
        """更新 License 状态显示"""
        is_valid, message, info = check_license_valid(self.config)
        
        if is_valid:
            self.license_status.setText(f"✅ {message}")
            self.license_status.setStyleSheet("color: #a6e3a1; font-size: 13px;")
        else:
            self.license_status.setText(f"❌ {message}")
            self.license_status.setStyleSheet("color: #f38ba8; font-size: 13px;")

    def save_and_accept(self):
        for widget in self.provider_widgets:
            widget.save_config()
        self.config.refresh_interval = self.interval_spin.value() * 60000
        self.config.alert_threshold = self.alert_spin.value()

        # 开机启动
        if self.autostart_check.isChecked():
            enable_autostart()
            self.config.autostart = True
        else:
            disable_autostart()
            self.config.autostart = False

        self.config.save()
        self.accept()

    def activate_license(self):
        key = self.license_input.text().strip()
        if not key:
            QMessageBox.warning(self, "提示", "请输入 License Key")
            return

        is_valid, license_type, info = validate_license_key(key)
        
        if is_valid:
            # 保存 License Key
            self.config.license_key = key
            self.config.license_type = license_type
            
            # 记录激活时间（用于计算过期）
            expire_days = info.get("expire_days")
            if expire_days is not None:
                self.config.license_activated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.config.save()
            
            # 显示激活成功信息
            if expire_days:
                msg = f"已激活 {license_type.upper()} 版本\n\n有效期: {expire_days} 天（从今天开始）"
            else:
                msg = f"已激活 {license_type.upper()} 版本\n\n有效期: 永久"
            
            QMessageBox.information(self, "成功", msg)
            
            # 更新状态显示
            self.update_license_status()
        else:
            QMessageBox.warning(self, "失败", "License Key 无效")
