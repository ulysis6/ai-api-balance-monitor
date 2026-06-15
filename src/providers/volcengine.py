"""
字节豆包（火山引擎）余额查询
"""

from src.providers.base import BaseProvider, BalanceInfo, PlanInfo
from typing import List


class VolcengineProvider(BaseProvider):
    name = "volcengine"
    display_name = "字节豆包"
    icon_color = "#fab387"
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
            "https://console.volcengine.com/ark/api/balance",
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

        plans = []

        # 查询 Coding Plan
        result = self._get(
            "https://console.volcengine.com/ark/api/coding-plan/usage",
            headers=headers
        )

        if result["status_code"] == 200:
            try:
                data = result["data"].get("data", result["data"])
                used = float(data.get("used", 0))
                total = float(data.get("total", 1))
                plans.append(PlanInfo(
                    name="Coding Plan",
                    plan_type="coding_plan",
                    percent=used / total * 100 if total > 0 else 0
                ))
            except Exception:
                pass

        # 查询 Agent Plan
        result = self._get(
            "https://console.volcengine.com/ark/api/agent-plan/usage",
            headers=headers
        )

        if result["status_code"] == 200:
            try:
                data = result["data"].get("data", result["data"])
                used = float(data.get("used", 0))
                total = float(data.get("total", 1))
                plans.append(PlanInfo(
                    name="Agent Plan",
                    plan_type="agent_plan",
                    percent=used / total * 100 if total > 0 else 0
                ))
            except Exception:
                pass

        return plans

    def get_cookie_login_url(self) -> str:
        return "https://console.volcengine.com/ark"
