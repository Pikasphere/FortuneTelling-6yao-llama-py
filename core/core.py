# core/core.py
import json
import os
from datetime import datetime

from .gua64 import find_by_binary
from .models import Hexagram, CastResult


# ============================================================
# 1. 加载 64 卦数据
# ============================================================

_DATA_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "data", "yijing.json",
)

with open(_DATA_PATH, "r", encoding="utf-8") as f:
    _RAW = json.load(f)


# 卦名 -> 原始 hexagram dict
_HEX_INDEX = {}
for _item in _RAW.get("hexagrams", []):
    _name = _item.get("image") or _item.get("name")
    if _name:
        _HEX_INDEX[_name] = _item


def _find_line(hex_item: dict, index: int) -> dict:
    """按 0-based 下标找某爻的完整解读"""
    for ln in hex_item.get("lines", []):
        if ln.get("index") == index:
            return ln
    return {}


# ============================================================
# 2. 极简 / 中等取数
# ============================================================

def get_brief(gua_name: str, moving_index=None) -> dict:
    """
    极简版：给 SummaryCard 显示
    {
        "gua_ci": 卦辞原文,
        "translation": 卦辞白话,
        "duanyi": 断易,
        "yao_original": 动爻原文,
    }
    """
    item = _HEX_INDEX.get(gua_name, {})
    ov = item.get("overview", {})

    brief = {
        "gua_ci": "",
        "translation": "",
        "duanyi": "",
        "yao_original": "",
    }

    orig = ov.get("original", {}).get("text", [])
    brief["gua_ci"] = orig[0] if orig else ""

    trans = ov.get("translation", {}).get("text", [])
    brief["translation"] = trans[0] if trans else ""

    dy = ov.get("duanyi", [])
    brief["duanyi"] = dy[0] if dy else ""

    if moving_index is not None:
        ln = _find_line(item, moving_index)
        yao_orig = ln.get("original", {}).get("text", [])
        brief["yao_original"] = yao_orig[0] if yao_orig else ""

    return brief


def get_medium(gua_name: str, moving_index=None) -> dict:
    """
    中等版：喂 AI
    {
        "gua": {"原文","白话","断易","邵雍"},
        "yao": {"原文","白话","邵雍"} 或 {},
    }
    """
    item = _HEX_INDEX.get(gua_name, {})
    ov = item.get("overview", {})

    gua = {
        "原文": (ov.get("original", {}).get("text") or [""])[0],
        "白话": (ov.get("translation", {}).get("text") or [""])[0],
        "断易": (ov.get("duanyi") or [""])[0],
        "邵雍": (ov.get("shaoyong") or [""])[0],
    }

    yao = {}
    if moving_index is not None:
        ln = _find_line(item, moving_index)
        if ln:
            yao = {
                "原文": (ln.get("original", {}).get("text") or [""])[0],
                "白话": (ln.get("translation", {}).get("text") or [""])[0],
                "邵雍": (ln.get("shaoyong") or [""])[0],
            }

    return {"gua": gua, "yao": yao}


def build_ai_prompt(question: str, result: CastResult) -> str:
    """把中等版解读拼成一段文字，直接喂给 AI"""
    orig = result.original
    changed = result.changed

    lines = [f"【所问】{question}", ""]

    # 本卦
    moving_idx = orig.moving_indexes[0] if orig.moving_indexes else None
    g = get_medium(orig.name, moving_idx)
    lines.append(f"【本卦】{orig.name}")
    for k, v in g["gua"].items():
        if v:
            lines.append(f"  {k}：{v}")

    # 动爻
    if g["yao"]:
        lines.append("")
        lines.append("【动爻】")
        for k, v in g["yao"].items():
            if v:
                lines.append(f"  {k}：{v}")

    # 变卦
    if changed:
        lines.append("")
        lines.append(f"【变卦】{changed.name}")
        cg = get_medium(changed.name)
        for k, v in cg["gua"].items():
            if v:
                lines.append(f"  {k}：{v}")

    return "\n".join(lines)


# ============================================================
# 3. 先天八卦数 / 二进制映射
# ============================================================

NUM_TO_BAGUA = {
    1: "乾", 2: "兑", 3: "离", 4: "震",
    5: "巽", 6: "坎", 7: "艮", 8: "坤",
}

BAGUA_TO_BIN = {
    "坤": "000", "艮": "001", "坎": "010", "巽": "011",
    "震": "100", "离": "101", "兑": "110", "乾": "111",
}

YAO_NAMES = ["初", "二", "三", "四", "五", "上"]


# ============================================================
# 4. 工具函数
# ============================================================

def num_to_bagua(n: int) -> str:
    """数字取余 → 八卦名（先天数：乾1 兑2 离3 震4 巽5 坎6 艮7 坤8）"""
    r = n % 8
    if r == 0:
        r = 8
    return NUM_TO_BAGUA[r]


def num_to_moving(n: int) -> int:
    """数字取余 → 0-based 动爻下标：0=初爻，5=上爻"""
    r = n % 6
    if r == 0:
        r = 6
    return r - 1


def bin_to_yaos(bin_str: str) -> list:
    """'000111' → ['阴','阴','阴','阳','阳','阳']"""
    return ["阳" if c == "1" else "阴" for c in bin_str]


def yaos_to_binary(yaos: list) -> str:
    """['阴','阴','阴','阳','阳','阳'] → '000111'"""
    return "".join("1" if y == "阳" else "0" for y in yaos)


def yaos_to_hexagram(yaos: list, moving_indexes=None) -> Hexagram:
    """六爻阴阳 + 动爻 → Hexagram 对象"""
    bin_str = yaos_to_binary(yaos)
    g = find_by_binary(bin_str)
    if g is None:
        raise ValueError(f"未找到对应卦: {bin_str}")

    return Hexagram(
        name=g["name"],
        binary=g["binary"],
        upper=g["upper"],
        lower=g["lower"],
        yaos=yaos,
        moving_indexes=list(moving_indexes or []),
        meaning=g.get("meaning", ""),
        text="",
        yao_ci=[],
    )


def flip_yaos(yaos: list, moving_indexes: list) -> list:
    """动爻阴阳反转，得到变卦的六爻"""
    new_yaos = yaos[:]
    for i in moving_indexes:
        new_yaos[i] = "阴" if new_yaos[i] == "阳" else "阳"
    return new_yaos


# ============================================================
# 5. 服务
# ============================================================

class DivinationService:
    @staticmethod
    def methods():
        return ["数字起卦"]

    def cast(self, question: str, manual_values: list) -> CastResult:
        """
        manual_values: [n1, n2, n3]
            n1 → 上卦
            n2 → 下卦
            n3 → 动爻
        """
        n1, n2, n3 = manual_values

        upper = num_to_bagua(n1)
        lower = num_to_bagua(n2)
        moving_indexes = [num_to_moving(n3)]

        # 下卦在前（初二三爻），上卦在后（四五六爻）
        bin_str = BAGUA_TO_BIN[lower] + BAGUA_TO_BIN[upper]
        yaos = bin_to_yaos(bin_str)

        original = yaos_to_hexagram(yaos, moving_indexes)

        changed = None
        if moving_indexes:
            changed_yaos = flip_yaos(yaos, moving_indexes)
            changed = yaos_to_hexagram(changed_yaos)

        # 断语：只报卦名 + 动爻，不做多余分析
        parts = [original.name]
        if changed:
            parts.append(f"之 {changed.name}")
        if moving_indexes:
            idx = moving_indexes[0]
            parts.append(f"{YAO_NAMES[idx]}爻动")
        interpretation = "，".join(parts)

        return CastResult(
            question=question,
            time=datetime.now().strftime("%Y-%m-%d %H:%M"),
            original=original,
            changed=changed,
            interpretation=interpretation,
        )