"""
MiniMax 余额查询
"""

from src.providers.base import BaseProvider, BalanceInfo, PlanInfo
from typing import List


class MiniMaxProvider(BaseProvider):
    name = "minimax"
    display_name = "MiniMax"
    icon_color = "#f5c2e7"
    auth_type = "cookie"
    has_plans = True

    def get_balance(self, config: dict) -> BalanceInfo:
        cookie = config.get("cookie", "").strip()
        if not cookie:
            return BalanceInfo(error="未配置Cookie")

        headers = {
            "Cookie": cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }

        result = self._get(
            "https://platform.minimaxi.com/api/balance",
            headers=headers
        )

        if result.get("error"):
            return BalanceInfo(error=result["error"])

        if result["status_code"] == 200:
            data = result["data"]
            try:
                balance = data.get("balance", data.get("data", {}).get("balance", 0))
                return BalanceInfo(balance=float(balance))
            except Exception:
                return BalanceInfo(error="解析失败")
        elif result["status_code"] == 401:
            return BalanceInfo(error="Cookie过期")
        else:
            return BalanceInfo(error=f"HTTP {result['status_code']}")

    def get_plans(self, config: dict) -> List[PlanInfo]:
        cookie = config.get("cookie", "").strip()
        if not cookie:
            return []

        headers = {
            "Cookie": cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }

        result = self._get(
            "https://platform.minimaxi.com/api/token-plan/usage",
            headers=headers
        )

        if result.get("error") or result["status_code"] != 200:
            return []

        try:
            data = result["data"].get("data", result["data"])
            used = float(data.get("used", 0))
            total = float(data.get("total", 1))
            return [PlanInfo(
                name="Token Plan",
                plan_type="token_plan",
                percent=used / total * 100 if total > 0 else 0
            )]
        except Exception:
            return []

    def get_cookie_login_url(self) -> str:
        return "https://platform.minimaxi.com"
