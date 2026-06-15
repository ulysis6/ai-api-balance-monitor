"""
零一万物 余额查询
"""

from src.providers.base import BaseProvider, BalanceInfo


class LingYiProvider(BaseProvider):
    name = "lingyi"
    display_name = "零一万物"
    icon_color = "#f9e2af"
    auth_type = "api_key"
    has_plans = False

    def get_balance(self, config: dict) -> BalanceInfo:
        api_key = config.get("api_key", "").strip()
        if not api_key:
            return BalanceInfo(error="未配置API Key")

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        result = self._get(
            "https://api.lingyiwanwu.com/v1/user/balance",
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
        elif result["status_code"] in [401, 403]:
            return BalanceInfo(error="API Key无效")
        else:
            return BalanceInfo(error=f"HTTP {result['status_code']}")

    def get_auth_url(self) -> str:
        return "https://platform.lingyiwanwu.com"
