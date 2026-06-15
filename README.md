# AI模型API余额监控 v2.0

一站式监控所有 AI API 余额 + 套餐额度的 Windows 桌面小工具。

## 功能特点

- ✨ **14+ 家厂商支持**：DeepSeek、小米 MiMo、Kimi、字节豆包、智谱、百度千帆、阿里百炼、腾讯混元等
- 📊 **多维度监控**：按量付费余额 + Coding Plan / Token Plan / Agent Plan 额度
- 🎯 **桌面浮动窗口**：简约暗色风格，半透明毛玻璃效果
- ⏰ **自动刷新**：可配置刷新间隔
- 🔔 **余额提醒**：余额低于阈值时提醒
- 🚀 **开机自启**：支持开机自动启动
- 🎫 **License 验证**：免费版 + 专业版

## 版本对比

| 功能 | 免费版 | 专业版（¥29.9） |
|------|:------:|:---------------:|
| 监控厂商数 | 3 个 | 无限 |
| 按量付费余额监控 | ✅ | ✅ |
| Plan 额度监控 | ❌ | ✅ |
| 余额提醒 | ❌ | ✅ |
| 开机自启 | ❌ | ✅ |

## 支持的厂商

| 厂商 | 按量付费 | Coding Plan | Token Plan | Agent Plan |
|------|:--------:|:-----------:|:----------:|:----------:|
| DeepSeek | ✅ | ❌ | ❌ | ❌ |
| 小米 MiMo | ✅ | ❌ | ✅ | ❌ |
| Kimi | ✅ | ✅ | ❌ | ❌ |
| 字节豆包 | ✅ | ✅ | ❌ | ✅ |
| 智谱 GLM | ✅ | ✅ | ❌ | ❌ |
| 百度千帆 | ✅ | ✅ | ❌ | ❌ |
| 阿里百炼 | ✅ | ✅ | ✅ | ❌ |
| 腾讯混元 | ✅ | ❌ | ✅ | ❌ |
| 讯飞星火 | ✅ | ✅ | ❌ | ❌ |
| MiniMax | ✅ | ❌ | ✅ | ❌ |
| 硅基流动 | ✅ | ❌ | ❌ | ❌ |
| 百川智能 | ✅ | ❌ | ❌ | ❌ |
| 零一万物 | ✅ | ❌ | ❌ | ❌ |
| 京东云 | ✅ | ✅ | ❌ | ❌ |

## 使用方法

### 方式一：运行 exe（推荐）

1. 下载 `AI模型API余额监控.exe`
2. 双击运行
3. 点击 ⚙ 配置厂商

### 方式二：源码运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行
python -m src.main
```

## 配置说明

### API Key 认证
适用于：DeepSeek、Kimi、硅基流动、百川智能、零一万物

获取方式：访问厂商官网的 API Keys 页面

### Cookie 认证
适用于：小米 MiMo、字节豆包、智谱、百度千帆、阿里百炼、腾讯混元、讯飞星火、MiniMax、京东云

获取方式：
1. 打开厂商官网并登录
2. 按 F12 打开开发者工具
3. 切换到 Network 面板
4. 刷新页面，点击任意请求
5. 复制请求头中的 Cookie 值

## 打包 exe

```bash
python scripts/build.py
```

输出：`dist/AI模型API余额监控.exe`

## License Key

- 免费版：无需 License，最多启用 3 个厂商
- 专业版：输入 License Key 解锁全部功能

## 配置文件位置

```
%USERPROFILE%\.api_balance_monitor\config.json
```

## 技术栈

- Python 3.11+
- PyQt5
- requests
- PyInstaller

## 项目结构

```
ai-api-balance-monitor/
├── src/
│   ├── main.py              # 入口
│   ├── providers/           # 厂商适配器
│   │   ├── base.py          # 基类
│   │   ├── deepseek.py
│   │   ├── mimo.py
│   │   ├── kimi.py
│   │   └── ...
│   ├── ui/                  # 界面
│   │   ├── main_window.py   # 主窗口
│   │   ├── config_dialog.py # 配置对话框
│   │   └── tray_icon.py     # 系统托盘
│   ├── license/             # License 验证
│   │   └── validator.py
│   └── utils/               # 工具
│       └── config.py        # 配置管理
├── scripts/
│   └── build.py             # 打包脚本
├── assets/                  # 资源文件
├── requirements.txt
└── README.md
```

## 更新日志

### v2.0 (2026-06-14)
- 重构代码架构
- 支持 14+ 家厂商
- 支持 Plan 额度监控
- 新增系统托盘
- 新增 License 验证
- 新增余额提醒
- 新增开机自启

## License

MIT
