"""
小米 MiMo 余额查询
"""

from src.providers.base import BaseProvider, BalanceInfo, PlanInfo
from typing import List


class MiMoProvider(BaseProvider):
    name = "mimo"
    display_name = "小米 MiMo"
    icon_color = "#f38ba8"
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
            "https://platform.xiaomimimo.com/api/v1/balance",
            headers=headers
        )

        if result.get("error"):
            return BalanceInfo(error=result["error"])

        if result["status_code"] == 200:
            data = result["data"]
            try:
                if isinstance(data, dict):
                    d = data.get("data", data)
                    for key in ["totalBalance", "total_balance", "balance",
                                "cashBalance", "cash_balance"]:
                        if key in d:
                            val = float(d[key])
                            if val > 1000:
                                val = val / 100
                            return BalanceInfo(balance=val)
                return BalanceInfo(error="格式异常")
            except Exception as e:
                return BalanceInfo(error=f"解析失败")
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
            "https://platform.xiaomimimo.com/api/v1/tokenPlan/usage",
            headers=headers
        )

        if result.get("error") or result["status_code"] != 200:
            return []

        try:
            data = result["data"]
            d = data.get("data", data)
            used = float(d.get("usedCredits", d.get("used_credits", 0)))
            total = float(d.get("totalCredits", d.get("total_credits", 0)))
            if total > 0:
                return [PlanInfo(
                    name="Token Plan",
                    plan_type="token_plan",
                    used=used / 10000,
                    total=total / 10000,
                    unit="万Credits",
                    percent=used / total * 100 if total > 0 else 0
                )]
        except Exception:
            pass
        return []

    def get_cookie_login_url(self) -> str:
        return "https://platform.xiaomimimo.com/console/balance"
