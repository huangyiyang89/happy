"""a"""

import glob
import os
import sys
import logging
from typing import List, Tuple
from nicegui import ui, app
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

pairs: List[Tuple[Cg, ui.card]] = []

def timer_handler():
    """_summary_"""
    game = Cg.open()
    if game:
        with ui.card() as card:
            pairs.append((game,card))
            ui.label("Player Name").bind_text_from(game.player, "name")
            ui.label("Efficiency").bind_text_from(game.get_script("里洞魔石"),"efficiency")
            for script_file_name in script_file_names:
                script: Script = game.load_script(
                    scripts_directory, script_file_name, "Script"
                )
                if script:
                    ui.switch(text=script.name).bind_value_to(script, "enable")
            game.start_loop()
    to_remove = []
    for game,card in pairs:
        if game.is_closed:
            card.clear()
            card.delete()
            card.set_visibility(False)
            to_remove.append((game,card))
    for item in to_remove:
        pairs.remove(item)



def exception_handler(exception=""):
    """_summary_

    Args:
        exception (_type_): _description_
    """
    print(exception)


app.on_exception(exception_handler)
with ui.row():
    ui.button("解除多开限制",on_click=Cg.close_handles)
with ui.row():
    ui.timer(3, timer_handler)
with ui.row():
    ui.label("Some message")
ui.run()
