# models.py
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class Hexagram:
    """一个完整的六爻卦"""
    name: str                    # 卦名，如 "山地剥"
    binary: str                  # 六位二进制，初爻在最高位
    upper: str                   # 上卦名
    lower: str                   # 下卦名
    yaos: List[str]              # ["阳","阴",...] 从初爻到上爻
    moving_indexes: List[int] = field(default_factory=list)
    meaning: str = ""            # 简要含义
    text: str = ""               # 卦辞或断语（可选）
    yao_ci: List[str] = field(default_factory=list)


@dataclass
class CastResult:
    """一次完整的占卜结果"""
    question: str
    time: str
    original: Hexagram                       # 本卦
    changed: Optional[Hexagram] = None       # 变卦
    interpretation: str = ""                 # 断语
    yao_details: List[dict] = field(default_factory=list)
    # yao_details 每项如：
    # {"pos": 1, "yin_yang": "阳", "moving": False,
    #  "liuqin": "父母", "najia": "子水", "liushen": "青龙"}