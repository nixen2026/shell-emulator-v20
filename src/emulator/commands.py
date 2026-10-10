"""Встроенные команды эмулятора.

Каждая команда — функция вида ``command(shell, args)``, где ``shell`` —
экземпляр :class:`emulator.shell.Shell`, а ``args`` — список аргументов.
Об ошибке команда сообщает исключением :class:`ShellError`.
"""

from emulator.errors import ExitRequest, ShellError

MAX_EXIT_ARGS = 1


def require_no_args(name, args):
    """Сообщить об ошибке, если команде переданы аргументы."""
    if args:
        raise ShellError(f"{name}: too many arguments")


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


def cmd_conf_dump(shell, args):
    """Служебная команда: вывести параметры эмулятора (ключ=значение)."""
    require_no_args("conf-dump", args)
    for line in shell.config.dump():
        shell.write(line)


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
    "conf-dump": cmd_conf_dump,
}
