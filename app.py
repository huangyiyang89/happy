"""app"""
import os
import sys
import glob
import customtkinter
import happy.core
import happy.script


class App(customtkinter.CTk):
    """_summary_

    Args:
        customtkinter (_type_): _description_
    """

    def __init__(self):
        super().__init__()
        self.geometry("600x400")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.cgframes: list[Cgframe] = []
        self.title("HappyCG")
        self.refresh()

    def refresh(self):
        """_summary_"""

        for frame in self.cgframes:
            if frame.cg.is_closed:
                frame.destroy()

        cg = happy.core.Cg.open()
        if cg:
            new_frame = Cgframe(self, cg)
            self.cgframes.append(new_frame)
            count = len(self.cgframes)
            for i in range(count):
                self.cgframes[i].grid(
                    row=0,
                    column=i,
                    padx=(30 - 15 * i, 0 + 15 * i),
                    pady=20,
                    sticky="nsew",
                )
        self.after(1000, self.refresh)


class Cgframe(customtkinter.CTkFrame):
    """_summary_

    Args:
        customtkinter (_type_): _description_
    """

    def __init__(self, master, cg: happy.core.Cg):
        super().__init__(master)
        self.cg = cg
        # config grid
        self.grid_rowconfigure([0, 1, 2, 3, 4, 5], weight=1)
        self.grid_columnconfigure(0, weight=1)

        # lable control
        self.player_name_label = customtkinter.CTkLabel(self, text="")
        self.player_name_label.grid(row=0, column=0)

        # load scripts
        self.load_script_names = get_all_py_files()
        self.load_scripts = []
        for script_name in self.load_script_names:
            self.load_scripts.append(cg.load_script("scripts." + script_name, "Script"))

        self.switches = []

        for index,script in enumerate(self.load_scripts):
            switch = customtkinter.CTkSwitch(
                self,
                text=script.name,
                command=lambda script=script: self.switch_script_enable(script),
            )
            self.switches.append(switch)
            switch.grid(row=index+1, column=0)
        self.refresh()

    def refresh(self):
        """_summary_"""

        self.cg.update()
        self.player_name_label.configure(text=self.cg.player.name)
        # 间隔1秒执行一次
        self.after(100, self.refresh)


    def switch_script_enable(self, script):
        """_summary_"""
        script.enable = not script.enable


def get_all_py_files(directory="scripts"):
    """_summary_

    Args:
        directory (_type_): _description_

    Returns:
        _type_: _description_
    """
    # 构建目标目录路径
    scripts_directory = os.path.join(
        os.path.dirname(sys.argv[0]), directory
    )
    print(scripts_directory)
    # 获取目录中的所有 .py 文件
    py_files = glob.glob(os.path.join(scripts_directory, "*.py"))
    # 提取文件名（不包含扩展名）
    file_names = [os.path.splitext(os.path.basename(file))[0] for file in py_files]
    return file_names


app = App()
app.mainloop()