"""
厂商适配器注册
"""

from src.providers.deepseek import DeepSeekProvider
from src.providers.mimo import MiMoProvider
from src.providers.kimi import KimiProvider
from src.providers.siliconflow import SiliconFlowProvider
from src.providers.zhipu import ZhipuProvider
from src.providers.volcengine import VolcengineProvider
from src.providers.qianfan import QianfanProvider
from src.providers.dashscope import DashScopeProvider
from src.providers.tencent import TencentProvider
from src.providers.minimax import MiniMaxProvider
from src.providers.xunfei import XunfeiProvider
from src.providers.baichuan import BaichuanProvider
from src.providers.lingyi import LingYiProvider
from src.providers.jingdong import JingdongProvider

# 所有厂商列表（按优先级排序）
ALL_PROVIDERS = [
    DeepSeekProvider,
    MiMoProvider,
    KimiProvider,
    SiliconFlowProvider,
    ZhipuProvider,
    VolcengineProvider,
    QianfanProvider,
    DashScopeProvider,
    TencentProvider,
    MiniMaxProvider,
    XunfeiProvider,
    BaichuanProvider,
    LingYiProvider,
    JingdongProvider,
]

# Provider 名称到类的映射
PROVIDER_MAP = {p.name: p for p in ALL_PROVIDERS}

# 免费版最多启用的厂商数
FREE_MAX_PROVIDERS = 3


def get_provider(name: str):
    """获取 Provider 实例"""
    cls = PROVIDER_MAP.get(name)
    if cls:
        return cls()
    return None


def get_all_providers():
    """获取所有 Provider 实例"""
    return [cls() for cls in ALL_PROVIDERS]
