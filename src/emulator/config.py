"""Параметры командной строки эмулятора."""

import argparse
from dataclasses import dataclass
from typing import Optional

NOT_SET = "<not set>"


@dataclass
class Config:
    """Настройки эмулятора, заданные пользователем при запуске."""

    vfs_path: Optional[str] = None
    script_path: Optional[str] = None

    def items(self):
        """Вернуть список пар (ключ, значение) всех параметров."""
        return [("vfs", self.vfs_path), ("script", self.script_path)]

    def dump(self):
        """Вернуть строки вида ``ключ=значение`` для всех параметров."""
        return [f"{key}={value if value is not None else NOT_SET}"
                for key, value in self.items()]


def build_arg_parser():
    """Создать разборщик аргументов командной строки эмулятора."""
    parser = argparse.ArgumentParser(
        prog="emulator",
        description="Эмулятор командной оболочки UNIX-подобной ОС.")
    parser.add_argument(
        "--vfs", dest="vfs_path", metavar="PATH",
        help="путь к физическому расположению VFS")
    parser.add_argument(
        "--script", dest="script_path", metavar="PATH",
        help="путь к стартовому скрипту эмулятора")
    return parser


def parse_args(argv=None):
    """Разобрать аргументы командной строки и вернуть :class:`Config`.

    При неверных аргументах argparse печатает сообщение об ошибке
    и завершает процесс с кодом 2.
    """
    args = build_arg_parser().parse_args(argv)
    return Config(vfs_path=args.vfs_path, script_path=args.script_path)
