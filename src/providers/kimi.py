"""
Kimi / 月之暗面 余额查询
"""

from src.providers.base import BaseProvider, BalanceInfo, PlanInfo
from typing import List


class KimiProvider(BaseProvider):
    name = "kimi"
    display_name = "Kimi"
    icon_color = "#a6e3a1"
    auth_type = "api_key"
    has_plans = True

    def get_balance(self, config: dict) -> BalanceInfo:
        api_key = config.get("api_key", "").strip()
        if not api_key:
            return BalanceInfo(error="未配置API Key")

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        # 国内接口
        result = self._get(
            "https://api.moonshot.cn/v1/users/me/balance",
            headers=headers
        )

        if result.get("error"):
            return BalanceInfo(error=result["error"])

        if result["status_code"] == 200:
            data = result["data"]
            balance = data.get("available_balance", 0)
            return BalanceInfo(balance=float(balance))
        elif result["status_code"] == 401:
            return BalanceInfo(error="API Key无效")
        else:
            return BalanceInfo(error=f"HTTP {result['status_code']}")

    def get_plans(self, config: dict) -> List[PlanInfo]:
        # Kimi Coding Plan 需要 Cookie 查询
        cookie = config.get("cookie", "").strip()
        if not cookie:
            return []

        # 尝试查询 Coding Plan 状态
        headers = {
            "Cookie": cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }

        result = self._get(
            "https://api.moonshot.cn/v1/users/me/subscription",
            headers=headers
        )

        if result.get("error") or result["status_code"] != 200:
            return []

        try:
            data = result["data"]
            if data.get("plan"):
                plan_name = data["plan"].get("name", "Coding Plan")
                usage = data.get("usage", {})
                used = float(usage.get("used", 0))
                total = float(usage.get("total", 1))
                return [PlanInfo(
                    name=f"Coding Plan ({plan_name})",
                    plan_type="coding_plan",
                    percent=used / total * 100 if total > 0 else 0
                )]
        except Exception:
            pass
        return []

    def get_auth_url(self) -> str:
        return "https://platform.moonshot.cn/console/api-keys"

    def get_cookie_login_url(self) -> str:
        return "https://platform.moonshot.cn"
