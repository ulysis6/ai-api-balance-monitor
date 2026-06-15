"""
智谱 AI (GLM) 余额查询
"""

from src.providers.base import BaseProvider, BalanceInfo, PlanInfo
from typing import List


class ZhipuProvider(BaseProvider):
    name = "zhipu"
    display_name = "智谱 GLM"
    icon_color = "#89dceb"
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
            "https://open.bigmodel.cn/api/user/balance",
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
            "https://open.bigmodel.cn/api/user/coding-plan",
            headers=headers
        )

        if result.get("error") or result["status_code"] != 200:
            return []

        try:
            data = result["data"]
            plans = data.get("data", data)
            if isinstance(plans, list):
                for p in plans:
                    used = float(p.get("used", 0))
                    total = float(p.get("total", 1))
                    return [PlanInfo(
                        name=f"Coding Plan ({p.get('name', 'GLM')})",
                        plan_type="coding_plan",
                        percent=used / total * 100 if total > 0 else 0
                    )]
        except Exception:
            pass
        return []

    def get_cookie_login_url(self) -> str:
        return "https://open.bigmodel.cn/usercenter"
