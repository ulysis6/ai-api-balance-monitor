# License Key 生成和使用指南

## 生成 License Key

### 生成永久 Key
```bash
python scripts/generate_license.py --type pro --count 10
```

### 生成限时 Key（30天）
```bash
python scripts/generate_license.py --type pro --expire 30 --count 5
```

### 生成指定日期过期的 Key
```bash
python scripts/generate_license.py --type pro --expire 2026-12-31 --count 1
```

### 参数说明
| 参数 | 说明 | 示例 |
|------|------|------|
| `--type` | License 类型 | `pro` |
| `--count` | 生成数量 | `10` |
| `--expire` | 过期时间 | `30`（天）或 `2026-12-31`（日期） |
| `--output` | 输出文件名 | `my_keys.txt` |

## License Key 类型

| 类型 | 功能 | 适用场景 |
|------|------|----------|
| **Free** | 3个厂商限制 | 默认免费版 |
| **Pro** | 全部功能 | Gumroad 购买 / 手动分发 |

## 分发方式

### 1. Gumroad 自动发送
- 用户购买后，Gumroad 自动发送 License Key
- 需要在 Gumroad 产品设置中配置

### 2. 手动分发
- 生成 Key 后，手动发送给用户
- 适用于测试用户、朋友、促销活动

### 3. 批量生成
- 一次生成多个 Key，用于促销或分发
- 输出文件包含所有 Key 和过期信息

## 用户使用方法

1. 打开软件，点击 ⚙ 设置
2. 切换到 "License" 标签页
3. 输入 License Key
4. 点击 "激活" 按钮

## Key 格式

```
AIM-XXXX-XXXX-XXXX-XXXX
```

- `AIM-`：固定前缀
- `XXXX`：8位 payload 编码
- `XXXX-XXXX-XXXX-XXXX`：16位签名

## 过期时间

- **永久 Key**：没有过期时间，永久有效
- **限时 Key**：指定天数或日期，过期后无法使用
- **过期提醒**：剩余7天时会显示提醒

## 安全说明

- License Key 使用 HMAC-SHA256 签名
- 密钥硬编码在程序中
- 防止伪造和篡改
- 支持离线验证
