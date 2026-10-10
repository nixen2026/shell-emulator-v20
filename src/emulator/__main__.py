"""Точка входа эмулятора: ``python -m emulator``."""

import sys

from emulator.shell import Shell


def main():
    """Запустить эмулятор в интерактивном режиме и вернуть код выхода."""
    shell = Shell()
    return shell.repl()


if __name__ == "__main__":
    sys.exit(main())
