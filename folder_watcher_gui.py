import os
import time
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class FolderOpenHandler(FileSystemEventHandler):
    def __init__(self, base_path, log_directory):
        super().__init__()
        self.base_path = os.path.abspath(base_path)
        self.log_directory = log_directory
        self.seen = set()
        self.write_header_if_needed()

    def get_log_file_path(self):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.log_directory, f"{today}_log.txt")

    def get_prefix(self):
        weekday = datetime.datetime.now().weekday()
        return "Делал в пятницу\n" if weekday == 4 else "Делал сегодня\n"

    def write_header_if_needed(self):
        log_path = self.get_log_file_path()
        if not os.path.exists(log_path):
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(self.get_prefix())

    def on_modified(self, event):
        self.process_event(event)

    def on_created(self, event):
        self.process_event(event)

    def process_event(self, event):
        full_path = os.path.abspath(event.src_path)

        # Проверка: верхний уровень в отслеживаемой папке
        if os.path.isdir(full_path):
            rel = os.path.relpath(full_path, self.base_path)
            if os.path.sep not in rel:  # Это верхняя папка, не подпапка
                folder_name = os.path.basename(full_path)
                if folder_name not in self.seen:
                    self.seen.add(folder_name)
                    with open(self.get_log_file_path(), 'a', encoding='utf-8') as f:
                        f.write(f"{folder_name}\n")
                    print(f"[LOGGED] {folder_name}")


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Отслеживание папок")
        self.folder_path = tk.StringVar()
        self.observer = None

        self.build_ui()

    def build_ui(self):
        tk.Label(self.root, text="Выберите папку для отслеживания:").pack(pady=5)
        tk.Entry(self.root, textvariable=self.folder_path, width=60).pack(padx=10)
        tk.Button(self.root, text="Выбрать...", command=self.select_folder).pack(pady=5)
        tk.Button(self.root, text="Старт", command=self.start_watching).pack(pady=10)
        self.status_label = tk.Label(self.root, text="", fg="green")
        self.status_label.pack(pady=5)

    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_path.set(path)

    def start_watching(self):
        path = self.folder_path.get()
        if not os.path.exists(path):
            messagebox.showerror("Ошибка", "Указанная папка не существует.")
            return

        log_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(log_dir, exist_ok=True)

        handler = FolderOpenHandler(path, log_dir)
        self.observer = Observer()
        self.observer.schedule(handler, path=path, recursive=False)
        self.observer.start()

        self.status_label.config(text="Отслеживание запущено.")
        print(f"[INFO] Отслеживание папки: {path}")

    def on_close(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
