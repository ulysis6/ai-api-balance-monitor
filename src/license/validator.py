import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, Tuple

# Secret key parts
_K1 = "AIM"
_K2 = "SECRET"
_K3 = "KEY"
_K4 = "2026"
LICENSE_SECRET=_K1 + "-" + _K2 + "-" + _K3 + "-" + _K4


def validate_license_key(key: str) -> Tuple[bool, Optional[str], Optional[dict]]:
    if not key:
        return False, None, None
    if key == "FREE":
        return True, "free", {"expire_days": None}
    if not key.startswith("AIM-"):
        return False, None, None
    try:
        parts = key.split("-")
        if len(parts) != 3:
            return False, None, None
        days_str = parts[1]
        sig = parts[2]
        if days_str == "PERM":
            expire_days = None
        else:
            try:
                expire_days = int(days_str)
            except ValueError:
                return False, None, None
        if len(sig) == 16:
            return True, "pro", {"expire_days": expire_days}
        return False, None, None
    except Exception:
        return False, None, None


def check_license_valid(config) -> Tuple[bool, str, dict]:
    license_key = config.license_key
    if not license_key or license_key == "FREE":
        return True, "免费版", {"type": "free"}
    is_valid, license_type, info = validate_license_key(license_key)
    if not is_valid:
        return False, "License Key 无效", {"type": "free"}
    expire_days = info.get("expire_days")
    if expire_days is None:
        return True, "永久有效", {"type": license_type, "expire_date": None, "days_left": None}
    activated_at = config.license_activated_at
    if not activated_at:
        config.license_activated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        config.save()
        activated_at = config.license_activated_at
    activate_date = datetime.strptime(activated_at, "%Y-%m-%d %H:%M:%S")
    expire_date = activate_date + timedelta(days=expire_days)
    now = datetime.now()
    if now > expire_date:
        return False, "License 已过期", {"type": license_type, "expire_date": expire_date.strftime("%Y-%m-%d"), "days_left": 0}
    return True, f"到期: {expire_date.strftime('%Y-%m-%d')}", {"type": license_type, "expire_date": expire_date.strftime("%Y-%m-%d"), "days_left": (expire_date - now).days}


def format_expire_info(info: dict) -> str:
    if not info:
        return ""
    if info.get("type") == "free":
        return "免费版"
    if info.get("expire_date") is None:
        return "永久有效"
    days_left = info.get("days_left", 0)
    if days_left <= 0:
        return "已过期"
    return f"到期: {info['expire_date']}"