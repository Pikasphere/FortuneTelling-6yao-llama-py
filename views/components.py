# components.py
import flet as ft
from .theme import C, S


def yao_line(yin_yang: str, moving: bool = False) -> ft.Control:
    """
    一爻的图形。
    yin_yang: "阳" 或 "阴"
    moving: 是否为动爻
    """
    color = C.DANGER if moving else C.TEXT
    if yin_yang == "阳":
        bar = ft.Container(width=S.YAO_WIDTH, height=S.YAO_HEIGHT,
                           bgcolor=color, border_radius=3)
        row = ft.Row([bar], alignment=ft.MainAxisAlignment.CENTER)
    else:
        left = ft.Container(width=34, height=S.YAO_HEIGHT,
                            bgcolor=color, border_radius=3)
        right = ft.Container(width=34, height=S.YAO_HEIGHT,
                             bgcolor=color, border_radius=3)
        row = ft.Row([left, ft.Container(width=12), right],
                     alignment=ft.MainAxisAlignment.CENTER)

    if moving:
        return ft.Row(
            [row, ft.Text("○", color=C.DANGER, size=12)],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=4,
        )
    return row


class HexagramView(ft.Column):
    """
    显示一个六爻卦。
    yaos: ["阳", "阴", ...] 从初爻到上爻
    moving_indexes: 动爻下标集合，如 {0, 3}
    """
    def __init__(self, yaos: list, moving_indexes: set = None):
        moving_indexes = moving_indexes or set()
        controls = []
        for i, y in enumerate(yaos):
            controls.append(yao_line(y, moving=(i in moving_indexes)))
        # 反转，让上爻显示在最上面
        super().__init__(controls[::-1], spacing=6,
                         horizontal_alignment=ft.CrossAxisAlignment.CENTER)


class ResultCard(ft.Container):
    def __init__(self, title: str, hexagram, show_moving: bool = True):
        items = [
            ft.Text(title, size=13, color=C.PRIMARY, weight=ft.FontWeight.BOLD),
            ft.Text(hexagram.name, size=20, weight=ft.FontWeight.BOLD, color=C.TEXT),
            HexagramView(hexagram.yaos, hexagram.moving_indexes),
        ]

        # 卦辞
        if hexagram.text:
            items.append(
                ft.Text(hexagram.text, size=13, color=C.TEXT_MUTED)
            )

        # 动爻爻辞
        if show_moving:
            for idx in hexagram.moving_indexes:
                if 0 <= idx < len(hexagram.yao_ci):
                    items.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Text("动爻", size=11, color=C.DANGER,
                                        weight=ft.FontWeight.BOLD),
                                ft.Text(hexagram.yao_ci[idx], size=13, color=C.TEXT),
                            ], spacing=2),
                            padding=8,
                            border_radius=8,
                            bgcolor=C.SURFACE_ALT,
                        )
                    )

        super().__init__(
            content=ft.Column(items, spacing=8),
            padding=S.CARD_PAD,
            border_radius=S.RADIUS,
            bgcolor=C.SURFACE,
            border=ft.Border.all(1, C.BORDER),
        )


class HistoryItem(ft.Container):
    """一条历史记录"""
    def __init__(self, result):
        super().__init__(
            content=ft.Column([
                ft.Text(f"{result.time}",
                        size=11, color=C.TEXT_MUTED),
                ft.Text(result.question, size=13, color=C.TEXT,
                        max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Text(
                    f"{result.original.name} → "
                    f"{result.changed.name if result.changed else '无变卦'}",
                    size=11, color=C.ACCENT,
                ),
            ], spacing=2),
            padding=8,
            border_radius=8,
            bgcolor=C.SURFACE_ALT,
        )

class SummaryCard(ft.Container):
    def __init__(self, result, brief: dict):
        items = [
            ft.Text("卦象说明", size=15, weight=ft.FontWeight.BOLD,
                    color=C.PRIMARY),
        ]

        # 本卦
        items.append(
            ft.Text(f"本卦 · {result.original.name}", size=13,
                    weight=ft.FontWeight.BOLD, color=C.TEXT)
        )
        if brief.get("gua_ci"):
            items.append(ft.Text(f"原文：{brief['gua_ci']}",
                                 size=12, color=C.TEXT_MUTED))
        if brief.get("translation"):
            items.append(ft.Text(f"白话：{brief['translation']}",
                                 size=12, color=C.TEXT))
        if brief.get("duanyi"):
            items.append(ft.Text(f"断易：{brief['duanyi']}",
                                 size=12, color=C.TEXT_MUTED))

        # 动爻
        if brief.get("yao_original"):
            items.append(ft.Divider(color=C.BORDER, height=1))
            items.append(
                ft.Text(f"动爻 · {brief['yao_original']}",
                        size=12, color=C.DANGER)
            )

        # 变卦
        if result.changed:
            items.append(ft.Divider(color=C.BORDER, height=1))
            items.append(
                ft.Text(f"变卦 · {result.changed.name}", size=13,
                        weight=ft.FontWeight.BOLD, color=C.TEXT)
            )

        # 断语
        if result.interpretation:
            items.append(ft.Text(f"断语：{result.interpretation}",
                                 size=12, color=C.PRIMARY))

        super().__init__(
            content=ft.Column(items, spacing=6),
            padding=S.CARD_PAD,
            border_radius=S.RADIUS,
            bgcolor=C.SURFACE_ALT,
            border=ft.Border.all(1, C.PRIMARY),
        )

class AIView(ft.Container):
    """AI 解读区：加载模型 / 解读中 / 完成 / 失败"""

    def __init__(self):
        self.status = ft.Text("", size=12, color=C.TEXT_MUTED)
        self.body = ft.Markdown(
            "",
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            code_theme="atom-one-dark",
        )
        self.retry_btn = ft.TextButton(
            "重试",
            on_click=self._on_retry,
            visible=False,
        )

        super().__init__(
            content=ft.Column([
                ft.Text("AI 解读", size=15, weight=ft.FontWeight.BOLD,
                        color=C.PRIMARY),
                self.status,
                self.body,
                self.retry_btn,
            ], spacing=8),
            padding=S.CARD_PAD,
            border_radius=S.RADIUS,
            bgcolor=C.SURFACE,
            border=ft.Border.all(1, C.ACCENT),
            visible=False,
        )

        self._prompt = ""
        self._on_retry_cb = None

    def set_retry_callback(self, cb):
        self._on_retry_cb = cb

    def show_loading_model(self):
        self.visible = True
        self.status.value = "正在加载模型…（首次较慢，请稍等）"
        self.status.color = C.TEXT_MUTED
        self.body.value = ""
        self.retry_btn.visible = False

    def show_generating(self):
        self.visible = True
        self.status.value = "正在解读…"
        self.status.color = C.TEXT_MUTED
        self.body.value = ""
        self.retry_btn.visible = False

    def show_result(self, text: str, prompt: str = ""):
        self._prompt = prompt or self._prompt
        self.status.value = "解读完成"
        self.status.color = C.SUCCESS
        self.body.value = text
        self.retry_btn.visible = True

    def show_error(self, msg: str, prompt: str = ""):
        self._prompt = prompt or self._prompt
        self.status.value = f"解读失败：{msg}"
        self.status.color = C.DANGER
        self.body.value = ""
        self.retry_btn.visible = True

    def _on_retry(self, e):
        if self._on_retry_cb and self._prompt:
            self._on_retry_cb(self._prompt)

    def show_no_model(self):
        self.visible = True
        self.status.value = "请先选择并加载模型"
        self.status.color = C.TEXT_MUTED
        self.body.value = ""
        self.retry_btn.visible = False