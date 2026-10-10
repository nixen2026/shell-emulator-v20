"""Встроенные команды эмулятора и их реестр.

Каждая команда — функция вида ``command(shell, args)``, где ``shell`` —
экземпляр :class:`emulator.shell.Shell`, а ``args`` — список аргументов.
Об ошибке команда сообщает исключением :class:`ShellError` или
возвращает ненулевой код завершения.
"""

import platform

from emulator.errors import ExitRequest, ShellError
from emulator.fs_commands import cmd_cd, cmd_ls
from emulator.parser import parse_options
from emulator.terminal import clear_screen

MAX_EXIT_ARGS = 1
UNAME_ALL = "a"
UNAME_DEFAULT = "s"
UNAME_FIELDS = (
    ("s", "system"),
    ("n", "node"),
    ("r", "release"),
    ("v", "version"),
    ("m", "machine"),
)


def require_no_args(name, args):
    """Сообщить об ошибке, если команде переданы аргументы."""
    if args:
        raise ShellError(f"{name}: too many arguments")


def cmd_exit(shell, args):
    """Завершить работу эмулятора: ``exit [код]``.

    Без аргумента используется код последней выполненной команды.
    """
    if len(args) > MAX_EXIT_ARGS:
        raise ShellError("exit: too many arguments")
    if not args:
        raise ExitRequest(shell.status)
    try:
        code = int(args[0])
    except ValueError:
        raise ShellError(
            f"exit: {args[0]}: numeric argument required") from None
    raise ExitRequest(code)


def cmd_conf_dump(shell, args):
    """Служебная команда: вывести параметры эмулятора (ключ=значение)."""
    require_no_args("conf-dump", args)
    for line in shell.config.dump():
        shell.write(line)


def cmd_vfs_info(shell, args):
    """Служебная команда: вывести имя VFS и хеш SHA-256 её данных."""
    require_no_args("vfs-info", args)
    if not shell.vfs.loaded:
        raise ShellError("vfs-info: VFS is not loaded")
    shell.write(f"name: {shell.vfs.name}")
    shell.write(f"sha256: {shell.vfs.sha256}")


def cmd_clear(shell, args):
    """``clear`` — очистить экран терминала."""
    require_no_args("clear", args)
    clear_screen(shell.out)


def cmd_uname(shell, args):
    """``uname [-asnrvm]`` — вывести сведения о реальной ОС.

    Опции: ``-s`` имя ядра (по умолчанию), ``-n`` имя узла сети,
    ``-r`` выпуск, ``-v`` версия, ``-m`` архитектура, ``-a`` всё сразу.
    """
    letters = "".join(letter for letter, _ in UNAME_FIELDS) + UNAME_ALL
    options, operands = parse_options("uname", args, letters)
    if operands:
        raise ShellError(f"uname: extra operand '{operands[0]}'")
    if UNAME_ALL in options:
        options = set(letters)
    if not options:
        options = {UNAME_DEFAULT}
    info = platform.uname()
    values = [getattr(info, field) for letter, field in UNAME_FIELDS
              if letter in options]
    shell.write(" ".join(values))


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
    "conf-dump": cmd_conf_dump,
    "vfs-info": cmd_vfs_info,
    "clear": cmd_clear,
    "uname": cmd_uname,
}
