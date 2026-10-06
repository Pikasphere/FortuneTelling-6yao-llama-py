# theme.py
import flet as ft

class C:
    """颜色常量"""
    BG = "#0f0a1a"              # 页面背景
    SURFACE = "#1a1030"         # 卡片背景
    SURFACE_ALT = "#241740"     # 次级卡片
    BORDER = ft.Colors.PURPLE_800
    PRIMARY = ft.Colors.AMBER_200
    ACCENT = ft.Colors.PURPLE_400
    TEXT = ft.Colors.WHITE
    TEXT_MUTED = ft.Colors.GREY_400
    DANGER = ft.Colors.RED_300
    SUCCESS = ft.Colors.GREEN_300

class S:
    """尺寸常量"""
    PAGE_PAD = 20
    GAP = 12
    CARD_PAD = 14
    RADIUS = 12
    YAO_WIDTH = 80
    YAO_HEIGHT = 6