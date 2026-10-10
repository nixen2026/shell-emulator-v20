"""Точка входа эмулятора: ``python -m emulator [параметры]``."""

import sys

from emulator.config import parse_args
from emulator.shell import EXIT_FAILURE, Shell


def main(argv=None):
    """Запустить эмулятор и вернуть код завершения процесса.

    Сначала выводятся заданные параметры, затем выполняется стартовый
    скрипт (если указан), после чего запускается интерактивный режим,
    если скрипт не завершил работу командой exit.
    """
    config = parse_args(argv)
    shell = Shell(config)
    shell.print_debug_config()
    if config.script_path and not shell.run_script(config.script_path):
        return EXIT_FAILURE
    if not shell.running:
        return shell.exit_code
    return shell.repl()


if __name__ == "__main__":
    sys.exit(main())
