"""Встроенные команды эмулятора.

Каждая команда — функция вида ``command(shell, args)``, где ``shell`` —
экземпляр :class:`emulator.shell.Shell`, а ``args`` — список аргументов.
Об ошибке команда сообщает исключением :class:`ShellError`.
"""

from emulator.errors import ExitRequest, ShellError

MAX_EXIT_ARGS = 1


def format_stub(name, args):
    """Сформировать вывод команды-заглушки: имя и список аргументов."""
    return f"{name}: args={args!r}"


def cmd_ls(shell, args):
    """Заглушка ls: вывести имя команды и аргументы."""
    shell.write(format_stub("ls", args))


def cmd_cd(shell, args):
    """Заглушка cd: вывести имя команды и аргументы."""
    shell.write(format_stub("cd", args))


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


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}
