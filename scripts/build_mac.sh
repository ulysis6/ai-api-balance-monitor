#!/bin/bash
# AI余额监控 - Mac 本地打包脚本
# 用法: bash scripts/build_mac.sh

set -e

echo "🔨 开始打包 AI余额监控..."
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 python3，请先安装 Python"
    exit 1
fi

# 检查并安装依赖
echo "📦 检查依赖..."
pip3 install --quiet pyinstaller PyQt5 requests 2>/dev/null || pip install --quiet pyinstaller PyQt5 requests

# 清理旧构建
echo "🧹 清理旧构建..."
rm -rf build dist

# PyInstaller 打包
echo "📦 PyInstaller 打包中..."
python3 -m PyInstaller \
    --noconfirm \
    --onedir \
    --windowed \
    --osx-bundle-identifier "com.ulysis.aimonitor" \
    --name "AI余额监控" \
    --add-data "src:src" \
    --hidden-import PyQt5 \
    --hidden-import PyQt5.QtWidgets \
    --hidden-import PyQt5.QtCore \
    --hidden-import PyQt5.QtGui \
    --hidden-import requests \
    run.py

# 重命名
cd dist
if [ -d "run" ]; then mv "run" "AI余额监控"; fi
if [ -f "run.app" ]; then mv "run.app" "AI余额监控.app"; elif [ -d "run.app" ]; then mv "run.app" "AI余额监控.app"; fi

# Ad-hoc 签名（移除隔离属性）
echo "🔏 签名中..."
codesign --force --deep --sign - "AI余额监控.app"
xattr -cr "AI余额监控.app"

# 创建 DMG
echo "💿 创建 DMG..."
if command -v create-dmg &> /dev/null; then
    create-dmg \
        --volname "AI余额监控" \
        --window-pos 200 120 \
        --window-size 600 400 \
        --icon-size 100 \
        --icon "AI余额监控.app" 175 190 \
        --hide-extension "AI余额监控.app" \
        --app-drop-link 425 190 \
        "AI余额监控.dmg" \
        "AI余额监控.app" 2>/dev/null || \
    zip -r "AI余额监控-mac.zip" "AI余额监控.app"
else
    echo "   create-dmg 未安装，改用 zip 打包"
    zip -r "AI余额监控-mac.zip" "AI余额监控.app"
fi

echo ""
echo "✅ 打包完成！"
echo ""
ls -lh *.dmg *.zip 2>/dev/null
echo ""
echo "文件位置: $(pwd)"
echo ""
echo "首次打开请右键 → 打开，或运行: xattr -cr /Applications/AI余额监控.app"
