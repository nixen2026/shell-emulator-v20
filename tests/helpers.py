"""Вспомогательные средства для тестов эмулятора."""

import io

from emulator.shell import Shell


def make_shell(**kwargs):
    """Создать эмулятор, пишущий вывод и ошибки в буферы StringIO."""
    return Shell(out=io.StringIO(), err=io.StringIO(), **kwargs)


def run_lines(shell, *lines):
    """Выполнить строки и вернуть накопленные (вывод, ошибки)."""
    for line in lines:
        shell.execute(line)
    return shell.out.getvalue(), shell.err.getvalue()
