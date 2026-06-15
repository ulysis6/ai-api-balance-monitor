"""
打包脚本 - 生成绿色便携版
Windows: python scripts/build.py --platform windows
Mac:     python scripts/build.py --platform mac
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"

ENTRY_POINT = PROJECT_ROOT / "src" / "main.py"

ICON_PATH = PROJECT_ROOT / "assets" / "icon.ico"


def build_windows():
    """打包 Windows 绿色便携版"""
    print("=" * 50)
    print("打包 Windows 绿色便携版...")
    print("=" * 50)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", "AI余额监控",
        "--distpath", str(DIST_DIR),
        "--workpath", str(BUILD_DIR),
        "--specpath", str(PROJECT_ROOT),
        "--add-data", f"src{os.pathsep}src",
        "--hidden-import", "PyQt5",
        "--hidden-import", "PyQt5.QtWidgets",
        "--hidden-import", "PyQt5.QtCore",
        "--hidden-import", "PyQt5.QtGui",
        "--hidden-import", "requests",
        "--hidden-import", "playwright",
        "--collect-all", "playwright",
        str(ENTRY_POINT),
    ]

    if ICON_PATH.exists():
        cmd.extend(["--icon", str(ICON_PATH)])

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))

    if result.returncode == 0:
        print("\n✅ Windows 打包成功！")
        print(f"输出目录: {DIST_DIR / 'AI余额监控'}")
        print("将整个文件夹压缩即可分发（绿色免安装）")
    else:
        print("\n❌ 打包失败")
        sys.exit(1)


def build_mac():
    """打包 Mac 绿色便携版"""
    print("=" * 50)
    print("打包 Mac 绿色便携版...")
    print("=" * 50)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", "AI余额监控",
        "--distpath", str(DIST_DIR),
        "--workpath", str(BUILD_DIR),
        "--specpath", str(PROJECT_ROOT),
        "--add-data", f"src{os.pathsep}src",
        "--hidden-import", "PyQt5",
        "--hidden-import", "PyQt5.QtWidgets",
        "--hidden-import", "PyQt5.QtCore",
        "--hidden-import", "PyQt5.QtGui",
        "--hidden-import", "requests",
        "--hidden-import", "playwright",
        "--collect-all", "playwright",
        str(ENTRY_POINT),
    ]

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))

    if result.returncode == 0:
        print("\n✅ Mac 打包成功！")
        print(f"输出目录: {DIST_DIR / 'AI余额监控.app'}")
        print("将 .app 文件夹压缩即可分发（绿色免安装）")
    else:
        print("\n❌ 打包失败")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="打包绿色便携版")
    parser.add_argument("--platform", choices=["windows", "mac"], required=True,
                        help="目标平台")
    args = parser.parse_args()

    DIST_DIR.mkdir(parents=True, exist_ok=True)

    if args.platform == "windows":
        build_windows()
    elif args.platform == "mac":
        build_mac()


if __name__ == "__main__":
    main()
