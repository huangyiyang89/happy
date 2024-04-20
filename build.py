"""build app.exe"""
import os
import subprocess
from pathlib import Path
import nicegui

cmd = [
    'python',
    '-m', 'PyInstaller',
    'app.py', # your main file with ui.run()
    '--name', 'happy', # name of your app
    '--onefile',
    #'--windowed', # prevent console appearing, only use with ui.run(native=True, ...)
    '--add-data', f'{Path(nicegui.__file__).parent}{os.pathsep}nicegui'
]
subprocess.call(cmd)
