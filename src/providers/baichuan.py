"""
百川智能 余额查询
"""

from src.providers.base import BaseProvider, BalanceInfo


class BaichuanProvider(BaseProvider):
    name = "baichuan"
    display_name = "百川智能"
    icon_color = "#a6e3a1"
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
            "https://platform.baichuan-ai.com/api/balance",
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
        return "https://platform.baichuan-ai.com"
