"""
Provider 基类和数据结构定义
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List
import requests


@dataclass
class BalanceInfo:
    """按量付费余额信息"""
    balance: Optional[float] = None  # 余额（元）
    currency: str = "CNY"            # 货币
    error: Optional[str] = None      # 错误信息


@dataclass
class PlanInfo:
    """套餐额度信息"""
    name: str                        # 套餐名称
    plan_type: str                   # coding_plan / token_plan / agent_plan
    used: Optional[float] = None     # 已用量
    total: Optional[float] = None    # 总量
    unit: str = ""                   # 单位
    percent: Optional[float] = None  # 使用百分比
    expire_date: Optional[str] = None
    error: Optional[str] = None


@dataclass
class ProviderStatus:
    """厂商完整状态"""
    name: str
    icon_color: str = "#888888"
    auth_type: str = "api_key"       # api_key / cookie
    balance: Optional[BalanceInfo] = None
    plans: List[PlanInfo] = field(default_factory=list)
    configured: bool = False
    enabled: bool = False


class BaseProvider(ABC):
    """厂商适配器基类"""

    name: str = ""
    display_name: str = ""
    icon_color: str = "#888888"
    auth_type: str = "api_key"
    has_plans: bool = False

    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 10

    @abstractmethod
    def get_balance(self, config: dict) -> BalanceInfo:
        """查询按量付费余额"""
        pass

    def get_plans(self, config: dict) -> List[PlanInfo]:
        """查询套餐额度（可选）"""
        return []

    def get_status(self, config: dict) -> ProviderStatus:
        """获取完整状态"""
        status = ProviderStatus(
            name=self.display_name,
            icon_color=self.icon_color,
            auth_type=self.auth_type,
            configured=self.validate_config(config),
            enabled=config.get("enabled", False)
        )

        if status.configured and status.enabled:
            status.balance = self.get_balance(config)
            if self.has_plans:
                status.plans = self.get_plans(config)

        return status

    def get_auth_url(self) -> str:
        """返回获取 API Key 的网页地址"""
        return ""

    def get_cookie_login_url(self) -> str:
        """返回需要登录的网页（用于自动获取Cookie）"""
        return ""

    def validate_config(self, config: dict) -> bool:
        """验证配置是否有效"""
        if self.auth_type == "api_key":
            return bool(config.get("api_key", "").strip())
        elif self.auth_type == "cookie":
            return bool(config.get("cookie", "").strip())
        return False

    def _get(self, url: str, headers: dict = None, params: dict = None) -> dict:
        """GET 请求封装"""
        try:
            resp = self.session.get(url, headers=headers, params=params)
            return {"status_code": resp.status_code, "data": resp.json()}
        except requests.exceptions.Timeout:
            return {"status_code": 0, "error": "请求超时"}
        except requests.exceptions.ConnectionError:
            return {"status_code": 0, "error": "连接失败"}
        except Exception as e:
            return {"status_code": 0, "error": str(e)[:30]}
