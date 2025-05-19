import os
import time
import datetime
import sys
import winreg
import threading
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
from win10toast import ToastNotifier
import tkinter as tk
from tkinter import filedialog
import json

CONFIG_FILE = os.path.join(get_base_dir(), "config.json")

APP_NAME = "PhpStormWatcher"
SEEN_FOLDERS = set()
ATIME_TRACKER = {}
notifier = ToastNotifier()

def load_or_choose_watch_path():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get("watch_path")

    # GUI-выбор папки
    root = tk.Tk()
    root.withdraw()
    selected_path = filedialog.askdirectory(title="Выберите папку с проектами PhpStorm")

    if not selected_path:
        print("❌ Папка не выбрана. Выход.")
        exit(1)

    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump({"watch_path": selected_path}, f, ensure_ascii=False, indent=4)

    return selected_path


WATCH_PATH = load_or_choose_watch_path() # ← Укажи нужный путь
def create_icon():
    # Простая иконка: серая круглая точка
    image = Image.new('RGB', (64, 64), color=(100, 100, 100))
    draw = ImageDraw.Draw(image)
    draw.ellipse((16, 16, 48, 48), fill='blue')
    return image


def on_exit(icon, item):
    print("🛑 Выход по меню трея.")
    icon.stop()
    os._exit(0)


def run_tray():
    icon = Icon(APP_NAME)
    icon.icon = create_icon()
    icon.menu = Menu(MenuItem('Выход', on_exit))
    icon.run()

def get_prefix():
    weekday = datetime.datetime.now().weekday()
    return "Делал в пятницу\n" if weekday == 4 else "Делал сегодня\n"


def get_base_dir():
    # Путь рядом с .exe или .py
    return os.path.dirname(os.path.abspath(sys.argv[0]))


def get_log_file_path():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    log_dir = os.path.join(get_base_dir(), "logs")
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, f"{today}_log.txt")


def write_to_log(folder_path):
    folder_name = os.path.basename(folder_path.rstrip("\\/"))
    log_path = get_log_file_path()

    if not os.path.exists(log_path):
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(get_prefix())

    with open(log_path, 'r', encoding='utf-8') as f:
        if folder_name in f.read():
            return

    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"{folder_name}\n")

    print(f"[LOGGED] {folder_name}")
    notifier.show_toast("PhpStorm открыт", folder_name, duration=4, threaded=True)


def init_tracker():
    """Запоминаем текущее время доступа к workspace.xml"""
    for root in os.listdir(WATCH_PATH):
        full_path = os.path.join(WATCH_PATH, root)
        idea_file = os.path.join(full_path, ".idea", "workspace.xml")

        if os.path.isfile(idea_file):
            try:
                atime = os.path.getatime(idea_file)
                ATIME_TRACKER[full_path] = atime
            except Exception:
                continue


def scan_folders():
    for root in os.listdir(WATCH_PATH):
        full_path = os.path.join(WATCH_PATH, root)
        idea_file = os.path.join(full_path, ".idea", "workspace.xml")

        if os.path.isfile(idea_file):
            try:
                atime = os.path.getatime(idea_file)
                last_known = ATIME_TRACKER.get(full_path)

                if last_known is not None and atime != last_known:
                    if full_path not in SEEN_FOLDERS:
                        write_to_log(full_path)
                        SEEN_FOLDERS.add(full_path)

                ATIME_TRACKER[full_path] = atime
            except Exception:
                continue


def add_to_autostart():
    exe_path = os.path.abspath(sys.argv[0])
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
        print("✅ Добавлено в автозапуск.")
    except Exception as e:
        print("⚠️ Не удалось добавить в автозапуск:", e)


# Запуск меню трея в фоне
threading.Thread(target=run_tray, daemon=True).start()

if __name__ == "__main__":
    print(f"👁 Следим за открытиями PhpStorm в: {WATCH_PATH}")
    add_to_autostart()
    init_tracker()

    try:
        while True:
            scan_folders()
            time.sleep(3)
    except KeyboardInterrupt:
        print("🛑 Остановлено.")
