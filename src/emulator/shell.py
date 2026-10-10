"""Ядро эмулятора: приглашение к вводу, выполнение команд и REPL."""

import getpass
import socket
import sys

from emulator.commands import COMMANDS
from emulator.config import Config
from emulator.errors import (EXIT_FAILURE, EXIT_NOT_FOUND, EXIT_SUCCESS,
                             ExitRequest, ShellError)
from emulator.parser import parse_line
from emulator.vfs import Vfs, display_path, resolve_parts

DEFAULT_USERNAME = "user"


def get_username():
    """Вернуть имя текущего пользователя реальной ОС."""
    try:
        return getpass.getuser()
    except (KeyError, OSError):
        return DEFAULT_USERNAME


class Shell:
    """Состояние и цикл работы эмулятора оболочки."""

    def __init__(self, config=None, vfs=None, out=None, err=None):
        """Создать эмулятор с настройками ``config`` и VFS ``vfs``.

        Вывод пишется в поток ``out``, ошибки — в поток ``err``.
        """
        self.config = config or Config()
        self.vfs = vfs or Vfs()
        self.out = out or sys.stdout
        self.err = err or sys.stderr
        self.username = get_username()
        self.hostname = socket.gethostname()
        self.status = EXIT_SUCCESS
        self.running = True
        self.exit_code = EXIT_SUCCESS
        self.cwd = []
        self.old_cwd = []

    def prompt(self):
        """Сформировать приглашение вида ``username@hostname:~/путь$``.

        Домашний каталог ``~`` соответствует корню VFS.
        """
        return f"{self.username}@{self.hostname}:{display_path(self.cwd)}$ "

    def resolve(self, path):
        """Вернуть абсолютный путь VFS (список имён) для ``path``."""
        return resolve_parts(self.cwd, path)

    def lookup(self, path):
        """Вернуть узел VFS по пути ``path`` или выбросить VfsError."""
        return self.vfs.get_node(self.resolve(path))

    def write(self, text):
        """Вывести строку в стандартный поток вывода."""
        self.out.write(text + "\n")
        self.out.flush()

    def error(self, text):
        """Вывести сообщение об ошибке в поток ошибок."""
        self.err.write(text + "\n")
        self.err.flush()

    def execute(self, line):
        """Выполнить одну строку ввода и вернуть код завершения."""
        words = parse_line(line)
        if not words:
            return self.status
        name, args = words[0], words[1:]
        command = COMMANDS.get(name)
        if command is None:
            self.error(f"{name}: command not found")
            self.status = EXIT_NOT_FOUND
            return self.status
        try:
            self.status = command(self, args) or EXIT_SUCCESS
        except ShellError as exc:
            self.error(str(exc))
            self.status = EXIT_FAILURE
        except ExitRequest as request:
            self.running = False
            self.exit_code = request.code
        return self.status

    def run_script(self, path):
        """Выполнить стартовый скрипт, имитируя диалог с пользователем.

        Перед выполнением каждой команды выводится приглашение и сама
        команда. Строки-комментарии и пустые строки пропускаются.
        Возвращает False, если файл скрипта не удалось прочитать.
        """
        try:
            with open(path, encoding="utf-8-sig") as file:
                lines = file.read().splitlines()
        except OSError as exc:
            self.error(f"script: cannot read '{path}': {exc.strerror}")
            return False
        for number, line in enumerate(lines, start=1):
            if not self.running:
                break
            self.run_script_line(path, number, line)
        return True

    def run_script_line(self, path, number, line):
        """Выполнить строку скрипта и сообщить об ошибке с её номером."""
        if not parse_line(line):
            return
        self.write(self.prompt() + line)
        status = self.execute(line)
        if self.running and status != EXIT_SUCCESS:
            self.error(f"{path}:{number}: error: "
                       f"command exited with status {status}")

    def repl(self):
        """Интерактивный цикл «чтение — выполнение — вывод».

        Возвращает код завершения эмулятора.
        """
        while self.running:
            try:
                line = input(self.prompt())
            except EOFError:
                self.write("")
                break
            except KeyboardInterrupt:
                self.write("")
                continue
            self.execute(line)
        return self.exit_code
