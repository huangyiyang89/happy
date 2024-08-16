import os
import glob
import sys
import logging
from typing import List
from nicegui import ui, native
from happy import Cg, Script

logging.basicConfig(
    filename="unhappy.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="UTF-8",
)

scripts_directory = os.path.join(os.path.dirname(sys.argv[0]), "scripts\\")
py_files = glob.glob(os.path.join(scripts_directory, "*.py"))
script_file_names = [os.path.splitext(os.path.basename(file))[0] for file in py_files]

cg_list: List[Cg] = []

def timer_handler():
    """定时器处理函数"""
    game = Cg.open()
    if game:
        update_ui()

def exception_handler(exception=""):
    """处理异常函数

    Args:
        exception (str): 异常描述
    """
    logging.error(exception)
    print(exception)

def close_notify():
    """关闭通知处理函数"""
    Cg.close_handles()
    ui.notify('Done')

def update_ui():
    """更新UI元素"""
    ui_container.clear()  # 清空容器
    with ui_container:
        for game in Cg.opened_cg_list:
            if not game.is_closed:
                with ui.card():
                    ui.label("Player Name").bind_text_from(game.player, "name")
                    ui.label("Account").bind_text_from(game, "account")
                    for script in game._scripts:
                        ui.switch(text=script.name).bind_value(script, "enable")
    ui.update(ui_container)

with ui.row():
    ui.button("解除多开限制", on_click=close_notify)
    ui.button("刷新", on_click=update_ui)

ui_container = ui.row()  # 用于动态生成卡片的容器

with ui.row():
    ui.label("Some message")

ui.timer(1, timer_handler)

ui.run(reload=False)
