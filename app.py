"""app"""

import os
import sys
import glob
import logging
import customtkinter
import happy.core
import happy.script

logging.basicConfig(
    filename="unhappy.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="UTF-8",
)


class App(customtkinter.CTk):
    """_summary_

    Args:
        customtkinter (_type_): _description_
    """

    def on_button_click(self):
        """_summary_"""
        happy.Cg.close_handles()

    def __init__(self):
        super().__init__()
        self.title("HappyCG")
        self.geometry("1400x600")
        self.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self.grid_rowconfigure(0, weight=0, pad=20)
        self.grid_rowconfigure(1, weight=1)

        for i in range(6):
            label = customtkinter.CTkLabel(self, text="", width=200, height=0)
            label.grid(row=0, column=i, sticky="nsew")

        button0 = customtkinter.CTkButton(
            self, text="解除多开限制", command=self.on_button_click
        )
        button0.grid(row=0, column=0, sticky="w")

        self.cgframes: list[Cgframe] = []
        self.refresh()

    def refresh(self):
        """_summary_"""

        cg = happy.core.Cg.open()

        if cg:
            self.remove_destroyed_frames()
            new_frame = Cgframe(self, cg)
            self.cgframes.append(new_frame)
            self.grid_all_frames()
            self.refresh()
        else:
            self.after(3000, self.refresh)

    def remove_destroyed_frames(self):
        """_summary_"""
        count = len(self.cgframes)
        for i in range(count - 1, 0, -1):
            if not self.cgframes[i].winfo_exists():
                self.cgframes.pop(i)

    def grid_all_frames(self):
        """_summary_"""
        count = len(self.cgframes)
        for i in range(0, count):
            if self.cgframes[i].winfo_exists():

                padx = 10
                if i == 0:
                    padx = (20, 10)
                if i == count - 1:
                    padx = (10, 20)
                self.cgframes[i].grid(
                    row=1,
                    column=i,
                    stick="nsew",
                    padx=padx,
                    pady=(10, 20),
                )


class Cgframe(customtkinter.CTkFrame):
    """_summary_

    Args:
        customtkinter (_type_): _description_
    """

    def __init__(self, master, cg: happy.core.Cg):
        super().__init__(master, width=200, height=200)
        self.cg = cg

        # lable control
        self.player_name_label = customtkinter.CTkLabel(self, text="")
        self.player_name_label.pack()

        # lable control
        self.account_label = customtkinter.CTkLabel(self, text="")
        self.account_label.pack()

        # lable control
        self.info_label = customtkinter.CTkLabel(self, text="")
        self.info_label.pack()

        # load scripts
        self.scripts_directory = get_scripts_directory()
        self.load_script_names = get_all_py_files(self.scripts_directory)
        self.load_scripts = []
        for script_name in self.load_script_names:
            if "config" in script_name:
                continue
            self.load_scripts.append(
                cg.load_script(self.scripts_directory, script_name, "Script")
            )

        self.switches = []

        for script in self.load_scripts:
            switch_var = customtkinter.BooleanVar(value=False)
            switch = customtkinter.CTkSwitch(
                self,
                text=script.name,
                command=lambda switch_var=switch_var, script=script: self.switch_event(
                    switch_var, script
                ),
                variable=switch_var,
                onvalue=True,
                offvalue=False,
                switch_width=50,
            )
            switch.pack()
            self.switches.append(switch)

        self.cg.start_loop()
        self.update_ui()

    def update_ui(self):
        """_summary_

        Args:
            cg (_type_): _description_
        """
        if self.cg.is_closed:
            self.destroy()
            return
        self.player_name_label.configure(text=self.cg.player.name)
        self.account_label.configure(text=self.cg.account)
        eff = self.cg.get_script("里洞魔石")
        if eff:
            self.info_label.configure(text=eff.efficiency)

        self.after(3000, self.update_ui)

    def switch_event(self, switch_var: customtkinter.BooleanVar, script: happy.Script):
        """_summary_"""
        
        if switch_var.get():
            script.start()
        else:
            script.stop()


def get_all_py_files(scripts_directory):
    """_summary_

    Args:
        directory (_type_): _description_

    Returns:
        _type_: _description_
    """
    # 获取目录中的所有 .py 文件
    py_files = glob.glob(os.path.join(scripts_directory, "*.py"))
    # 提取文件名（不包含扩展名）
    file_names = [os.path.splitext(os.path.basename(file))[0] for file in py_files]
    return file_names


def get_scripts_directory(directory="scripts\\"):
    """_summary_

    Args:
        directory (str, optional): _description_. Defaults to "scripts\".

    Returns:
        _type_: _description_
    """
    scripts_directory = os.path.join(os.path.dirname(sys.argv[0]), directory)
    return scripts_directory


app = App()
app.mainloop()

for frame in app.cgframes:
    frame.cg.close()
