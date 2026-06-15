"""
开机启动管理
Windows: 注册表
Mac: LaunchAgent plist
"""

import sys
import os
import json
from pathlib import Path

APP_NAME = "APIBalanceMonitor"


def _get_exe_path() -> str:
    """获取当前可执行文件路径"""
    if getattr(sys, 'frozen', False):
        return sys.executable
    return os.path.abspath(sys.argv[0])


def is_windows() -> bool:
    return sys.platform == "win32"


def is_mac() -> bool:
    return sys.platform == "darwin"


def enable_autostart():
    """启用开机启动"""
    exe_path = _get_exe_path()

    if is_windows():
        _windows_enable(exe_path)
    elif is_mac():
        _mac_enable(exe_path)


def disable_autostart():
    """禁用开机启动"""
    if is_windows():
        _windows_disable()
    elif is_mac():
        _mac_disable()


def is_autostart_enabled() -> bool:
    """检查是否已启用开机启动"""
    if is_windows():
        return _windows_is_enabled()
    elif is_mac():
        return _mac_is_enabled()
    return False


# ============ Windows ============

def _windows_enable(exe_path: str):
    import winreg
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0,
        winreg.KEY_SET_VALUE
    )
    winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{exe_path}"')
    winreg.CloseKey(key)


def _windows_disable():
    import winreg
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.DeleteValue(key, APP_NAME)
        winreg.CloseKey(key)
    except FileNotFoundError:
        pass


def _windows_is_enabled() -> bool:
    import winreg
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_READ
        )
        winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except (FileNotFoundError, OSError):
        return False


# ============ Mac ============

def _get_plist_path() -> Path:
    return Path.home() / "Library" / "LaunchAgents" / f"com.{APP_NAME.lower()}.plist"


def _mac_enable(exe_path: str):
    plist_path = _get_plist_path()
    plist_path.parent.mkdir(parents=True, exist_ok=True)

    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.{APP_NAME.lower()}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{exe_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>"""

    with open(plist_path, "w", encoding="utf-8") as f:
        f.write(plist_content)


def _mac_disable():
    plist_path = _get_plist_path()
    if plist_path.exists():
        plist_path.unlink()


def _mac_is_enabled() -> bool:
    return _get_plist_path().exists()
