"""
DeepSeek 余额查询
"""

from src.providers.base import BaseProvider, BalanceInfo


class DeepSeekProvider(BaseProvider):
    name = "deepseek"
    display_name = "DeepSeek"
    icon_color = "#89b4fa"
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

        result = self._get("https://api.deepseek.com/user/balance", headers=headers)

        if result.get("error"):
            return BalanceInfo(error=result["error"])

        if result["status_code"] == 200:
            data = result["data"]
            if data.get("is_available"):
                balance_info = data.get("balance_infos", [{}])[0]
                total = balance_info.get("total_balance", "0")
                return BalanceInfo(balance=float(total))
            else:
                return BalanceInfo(balance=0, error="余额不足")
        elif result["status_code"] == 401:
            return BalanceInfo(error="API Key无效")
        else:
            return BalanceInfo(error=f"HTTP {result['status_code']}")

    def get_auth_url(self) -> str:
        return "https://platform.deepseek.com/api_keys"
