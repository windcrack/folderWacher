from cx_Freeze import setup, Executable
import os

# Путь к иконке
icon_path = "icon.ico"  # если используешь

base = None

executables = [
    Executable(
        script="storm_watcher.py",
        base=base,
        target_name="PhpStormWatcher.exe",
        icon=icon_path  # Убери если не используешь
    )
]

build_options = {
    "include_files": ["icon.ico"],  # иконка + другие файлы если нужны
    "packages": ["tkinter", "winreg", "pystray", "PIL", "win10toast"],
    "excludes": []
}

setup(
    name="PhpStormWatcher",
    version="1.1",
    description="Отслеживание открытия проектов PhpStorm",
    options={"build_exe": build_options},
    executables=executables
)
