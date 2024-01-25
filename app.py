"""app"""
import os
import sys
import glob
import traceback
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
        self.title("HappyCG")
        self.geometry("700x350")
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        for i in range(3):
            label = customtkinter.CTkLabel(self, text="", width=200, height=0)
            label.grid(row=0, column=i, sticky="nsew")

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
        """_summary_
        """
        count = len(self.cgframes)
        for i in range(count-1,0,-1):
            if not self.cgframes[i].winfo_exists():
                self.cgframes.pop(i)

    def grid_all_frames(self):
        """_summary_
        """
        count = len(self.cgframes)
        for i in range(0, count):
            if self.cgframes[i].winfo_exists():
                self.cgframes[i].grid(
                    row=1,
                    column=i,
                    stick="nsew",
                    padx=(30 - i * 15 + 10, i * 15 + 10),
                    pady=(0, 20),
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
            switch = customtkinter.CTkSwitch(
                self,
                text=script.name,
                command=lambda script=script: self.switch_script_enable(script),
                switch_width=50,
            )
            switch.pack()
            self.switches.append(switch)

        self.refresh()

    def refresh(self):
        """_summary_"""
        try:
            self.cg.update()
            self.player_name_label.configure(text=self.cg.player.name)
            self.after(100, self.refresh)
        except Exception as e:  # pylint: disable=broad-except
            if "Could not read memory" in str(e):
                self.destroy()
                print(e, "Destroy This Frame")
            else :
                print(e)
                traceback.print_exc()

    def switch_script_enable(self, script):
        """_summary_"""
        script.enable = not script.enable


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
