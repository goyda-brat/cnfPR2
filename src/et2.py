import argparse
import getpass
import shlex
import socket
import tkinter as tk
from pathlib import Path
from tkinter import scrolledtext


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Эмулятор UNIX-подобной оболочки"
    )

    parser.add_argument(
        "--vfs",
        default="",
        help="Путь к VFS"
    )

    parser.add_argument(
        "--script",
        default="",
        help="Путь к стартовому скрипту"
    )

    return parser.parse_args()


class ShellGUI:
    def __init__(self, vfs_path, script_path):
        self.vfs_path = vfs_path
        self.script_path = script_path

        self.root = tk.Tk()

        username = getpass.getuser()
        hostname = socket.gethostname()

        self.root.title(
            f"Эмулятор - [{username}@{hostname}]"
        )
        self.root.geometry("700x450")

        self.create_interface()
        self.show_config()

        if self.script_path:
            self.root.after(100, self.run_script)

    def create_interface(self):
        self.output = scrolledtext.ScrolledText(
            self.root,
            state="disabled"
        )
        self.output.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.entry = tk.Entry(self.root)
        self.entry.pack(
            fill="x",
            padx=10,
            pady=(0, 10)
        )

        self.entry.bind("<Return>", self.handle_input)
        self.entry.focus()

    def write(self, text):
        self.output.config(state="normal")
        self.output.insert("end", text + "\n")
        self.output.see("end")
        self.output.config(state="disabled")

    def show_config(self):
        self.write("=== CONFIG ===")
        self.write(f"vfs = {self.vfs_path}")
        self.write(f"script = {self.script_path}")
        self.write("==============")

    def parse_command(self, command):
        try:
            return shlex.split(command)
        except ValueError:
            self.write("Ошибка: неверные кавычки")
            return None

    def handle_input(self, event=None):
        command = self.entry.get()
        self.entry.delete(0, "end")
        self.run_command(command)

    def run_command(self, command):
        self.write(f"$ {command}")

        parts = self.parse_command(command)

        if not parts:
            return False

        return self.execute(parts)

    def execute(self, parts):
        command = parts[0]
        args = parts[1:]

        if command == "exit":
            self.root.destroy()
            return True

        if command == "ls":
            return self.stub_command("ls", args)

        if command == "cd":
            return self.stub_command("cd", args)

        self.write(
            f"Ошибка: команда '{command}' не найдена"
        )
        return False

    def stub_command(self, command, args):
        if not args:
            self.write(
                f"Ошибка: команда {command} требует аргумент"
            )
            return False

        self.write(f"{command}: {args}")
        return True

    def run_script(self):
        path = Path(self.script_path)

        if not path.is_file():
            self.write(
                "Ошибка: стартовый скрипт не найден"
            )
            return

        try:
            lines = path.read_text(
                encoding="utf-8"
            ).splitlines()
        except OSError as error:
            self.write(
                f"Ошибка стартового скрипта: {error}"
            )
            return

        for line in lines:
            command = line.strip()

            if not command:
                continue

            self.run_command(command)

    def run(self):
        self.root.mainloop()


def main():
    args = parse_arguments()

    app = ShellGUI(
        args.vfs,
        args.script
    )

    app.run()


if __name__ == "__main__":
    main()