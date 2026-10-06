import getpass
import shlex
import socket
import tkinter as tk
from tkinter import scrolledtext


class ShellGUI:
    def __init__(self):
        self.root = tk.Tk()

        username = getpass.getuser()
        hostname = socket.gethostname()

        self.root.title(
            f"Эмулятор - [{username}@{hostname}]"
        )
        self.root.geometry("700x450")

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

    def parse_command(self, command):
        try:
            return shlex.split(command)
        except ValueError:
            self.write("Ошибка: неверные кавычки")
            return None

    def handle_input(self, event=None):
        command = self.entry.get()
        self.entry.delete(0, "end")

        self.write(f"$ {command}")

        parts = self.parse_command(command)

        if not parts:
            return

        self.execute(parts)

    def execute(self, parts):
        command = parts[0]
        args = parts[1:]

        if command == "exit":
            self.root.destroy()
        elif command == "ls":
            self.stub_command("ls", args)
        elif command == "cd":
            self.stub_command("cd", args)
        else:
            self.write(
                f"Ошибка: команда '{command}' не найдена"
            )

    def stub_command(self, command, args):
        if not args:
            self.write(
                f"Ошибка: команда {command} требует аргумент"
            )
            return

        self.write(f"{command}: {args}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ShellGUI()
    app.run()