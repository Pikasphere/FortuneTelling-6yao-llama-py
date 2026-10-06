# views.py
import random
import flet as ft

from .theme import C, S
from .components import ResultCard, HistoryItem, SummaryCard, AIView
from llama.qwen import list_models, get_model_path


class HeaderView:
    """顶部标题区"""

    def __init__(self):
        self.control = ft.Column(
            [
                ft.Text(
                    "六爻占卜",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=C.PRIMARY,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "静心默念所问之事",
                    size=12,
                    italic=True,
                    color=C.TEXT_MUTED,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        )


class InputView:
    """输入区：所问之事 + 三个数字 + 模型选择 + 按钮"""

    def __init__(self, on_cast, on_clear, on_load_model):
        self.on_cast = on_cast
        self.on_clear = on_clear
        self.on_load_model = on_load_model

        # ---------- 1. 所问之事 ----------
        self.question = ft.TextField(
            label="所问之事",
            hint_text="例如：近期事业运势如何？",
            multiline=True,
            min_lines=2,
            max_lines=3,
            border=ft.OutlineInputBorder(
                side=ft.BorderSide(color=C.ACCENT)
            ),
        )

        # ---------- 2. 三个数字输入框 ----------
        self.num_inputs = []
        for label in ["上卦数", "下卦数", "动爻数"]:
            self.num_inputs.append(
                ft.TextField(
                    label=label,
                    width=110,
                    keyboard_type=ft.KeyboardType.NUMBER,
                    border=ft.OutlineInputBorder(
                        side=ft.BorderSide(color=C.ACCENT)
                    ),
                )
            )

        self.manual_area = ft.Column(
            [
                ft.Text(
                    "输入三个正整数，分别定上卦 / 下卦 / 动爻",
                    size=12,
                    color=C.TEXT_MUTED,
                ),
                ft.Row(self.num_inputs, wrap=True, spacing=8),
            ],
            spacing=6,
        )

        # ---------- 3. 模型选择 ----------
        models = list_models()

        self.model_dropdown = ft.Dropdown(
            label="选择模型",
            value=models[0] if models else None,
            options=[ft.dropdown.Option(m) for m in models],
            border=ft.OutlineInputBorder(
                side=ft.BorderSide(color=C.ACCENT)
            ),
            width=320,
        )

        self.load_btn = ft.Button(
            "加载模型",
            on_click=self._on_load_click,
            style=ft.ButtonStyle(bgcolor=C.SURFACE_ALT),
        )

        self.model_status = ft.Text(
            "未加载",
            size=11,
            color=C.TEXT_MUTED,
        )

        if not models:
            self.model_status.value = "gguf 目录下没有 .gguf 文件"

        self.model_area = ft.Column(
            [
                ft.Text("模型", size=12, color=C.TEXT_MUTED),
                ft.Row(
                    [self.model_dropdown, self.load_btn],
                    spacing=8,
                    wrap=True,
                ),
                self.model_status,
            ],
            spacing=6,
        )

        # ---------- 4. 按钮行 ----------
        self.buttons = ft.Row(
            [
                ft.Button(
                    "起卦",
                    on_click=self._on_cast,
                    style=ft.ButtonStyle(bgcolor=C.ACCENT),
                ),
                ft.Button(
                    "随机三数",
                    on_click=self._on_random,
                    style=ft.ButtonStyle(bgcolor=C.SURFACE_ALT),
                ),
                ft.Button(
                    "清空",
                    on_click=lambda e: self.on_clear(),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
        )

        # ---------- 5. 组装（所有子控件都已存在） ----------
        self.control = ft.Column(
            [
                self.question,
                self.manual_area,
                self.model_area,
                self.buttons,
            ],
            spacing=S.GAP,
        )

    # ---------- 事件 ----------
    def _on_random(self, e):
        for t in self.num_inputs:
            t.value = str(random.randint(1, 99))
        self.question.error_text = ""
        self.control.update()

    def _on_cast(self, e):
        question = self.question.value.strip() or "（未填写问题）"

        try:
            manual_values = [int(t.value) for t in self.num_inputs]
        except (ValueError, TypeError):
            self.question.error_text = "请在三个数字框里都填入整数"
            self.control.update()
            return

        self.question.error_text = ""
        self.on_cast(question, manual_values)

    def _on_load_click(self, e):
        filename = self.model_dropdown.value
        if not filename:
            self.model_status.value = "请先选择模型"
            self.model_status.color = C.DANGER
            self.control.update()
            return

        self.model_status.value = f"正在加载 {filename}…"
        self.model_status.color = C.TEXT_MUTED
        self.control.update()

        self.on_load_model(filename)

    def set_model_status(self, text: str, ok: bool = True):
        self.model_status.value = text
        self.model_status.color = C.SUCCESS if ok else C.DANGER
        try:
            self.control.update()
        except Exception:
            pass


class ResultView:
    """结果展示区：所问 + 本卦 + 变卦 + 卦象说明 + AI 解读"""

    def __init__(self):
        # 上半部分：卦象
        self.container = ft.Column(spacing=S.GAP)

        # AI 解读区
        self.ai_view = AIView()

        # 整体拼装
        self.control = ft.Column(
            [self.container, self.ai_view],
            spacing=S.GAP,
        )

    def show(self, result, brief: dict):
        """
        result: CastResult
        brief:  get_brief() 返回的极简解读
        """
        self.container.controls.clear()

        # ---------- 所问 ----------
        self.container.controls.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("所问", size=12, color=C.TEXT_MUTED),
                        ft.Text(
                            result.question,
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=C.TEXT,
                        ),
                    ],
                    spacing=4,
                ),
                padding=S.CARD_PAD,
                border_radius=S.RADIUS,
                bgcolor=C.SURFACE_ALT,
            )
        )

        # ---------- 本卦 ----------
        self.container.controls.append(
            ResultCard("本卦", result.original, show_moving=True)
        )

        # ---------- 变卦 ----------
        if result.changed:
            self.container.controls.append(
                ResultCard("变卦", result.changed, show_moving=False)
            )

        # ---------- 卦象说明（极简） ----------
        self.container.controls.append(
            SummaryCard(result, brief)
        )

        # ---------- AI 区：先隐藏，等 run_ai 显示 ----------
        self.ai_view.visible = False

    def clear(self):
        self.container.controls.clear()
        self.ai_view.visible = False


class HistoryView:
    """历史记录区"""

    def __init__(self):
        self.list_view = ft.Column(spacing=6)
        self.history = []
        self.control = ft.Column(
            [
                ft.Text(
                    "历史记录",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=C.PRIMARY,
                ),
                self.list_view,
            ],
            spacing=8,
        )

    def add(self, result):
        self.history.append(result)
        self._refresh()

    def _refresh(self):
        self.list_view.controls.clear()

        if not self.history:
            self.list_view.controls.append(
                ft.Text(
                    "暂无记录",
                    size=12,
                    italic=True,
                    color=C.TEXT_MUTED,
                )
            )
        else:
            for r in reversed(self.history[-10:]):
                self.list_view.controls.append(HistoryItem(r))