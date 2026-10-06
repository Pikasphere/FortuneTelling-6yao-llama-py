# ============================================================
# main.py —— 主程序（只负责拼装）
# ============================================================

import flet as ft

from views.theme import C, S
from core.core import DivinationService, build_ai_prompt, get_brief
from views.views import HeaderView, InputView, ResultView, HistoryView
from llama.qwen import (
    AI_description, load_model,
    list_models, current_model, is_model_loaded,
)


def _setup_page(page: ft.Page) -> None:
    page.title = "六爻占卜"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = C.BG
    page.padding = S.PAGE_PAD
    page.scroll = ft.ScrollMode.AUTO


def main(page: ft.Page):
    _setup_page(page)

    service = DivinationService()

    header_view = HeaderView()
    result_view = ResultView()
    history_view = HistoryView()

    # ---------------------------------------------------------
    # 加载模型（后台线程）
    # ---------------------------------------------------------
    def do_load_model(filename: str):
        try:
            load_model(filename)
            input_view.set_model_status(f"已加载：{filename}", ok=True)
        except Exception as ex:
            input_view.set_model_status(f"加载失败：{ex}", ok=False)
        page.update()

    def handle_load_model(filename: str):
        page.run_thread(do_load_model, filename)

    # ---------------------------------------------------------
    # AI 推理（后台线程）
    # ---------------------------------------------------------
    def run_ai(prompt: str):
        ai = result_view.ai_view

        if not is_model_loaded():
            ai.show_no_model()
            page.update()
            return

        ai.show_generating()
        page.update()

        try:
            text = AI_description(prompt)
            ai.show_result(str(text), prompt)
        except Exception as ex:
            ai.show_error(str(ex), prompt)

        page.update()

    def handle_ai_retry(prompt: str):
        page.run_thread(run_ai, prompt)

    # ---------------------------------------------------------
    # 起卦
    # ---------------------------------------------------------
    def handle_cast(question: str, manual_values):
        result = service.cast(question, manual_values)

        moving_idx = (result.original.moving_indexes[0]
                      if result.original.moving_indexes else None)
        brief = get_brief(result.original.name, moving_idx)

        result_view.show(result, brief)
        history_view.add(result)

        ai_prompt = build_ai_prompt(question, result)
        page.run_thread(run_ai, ai_prompt)

        page.update()

    def handle_clear():
        result_view.clear()
        page.update()

    # ---------------------------------------------------------
    # 视图
    # ---------------------------------------------------------
    input_view = InputView(
        on_cast=handle_cast,
        on_clear=handle_clear,
        on_load_model=handle_load_model,
    )
    result_view.ai_view.set_retry_callback(handle_ai_retry)

    # ---------------------------------------------------------
    # 页面拼装
    # ---------------------------------------------------------
    page.add(
        ft.Column(
            controls=[
                header_view.control,
                ft.Divider(color=C.BORDER),

                input_view.control,

                result_view.control,

                ft.Divider(color=C.BORDER),
                history_view.control,
            ],
            spacing=S.GAP,
        )
    )


if __name__ == "__main__":
    ft.run(main)