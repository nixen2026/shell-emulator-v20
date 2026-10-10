"""Точка входа эмулятора: ``python -m emulator [параметры]``."""

import sys

from emulator.config import parse_args
from emulator.errors import EXIT_FAILURE
from emulator.shell import Shell
from emulator.vfs import Vfs, VfsError, load_vfs


def open_vfs(path):
    """Загрузить VFS по пути ``path`` или вернуть пустую VFS без пути.

    При ошибке загрузки выводит сообщение и возвращает None.
    """
    if path is None:
        return Vfs()
    try:
        return load_vfs(path)
    except VfsError as exc:
        sys.stderr.write(f"{exc}\n")
        return None


def main(argv=None):
    """Запустить эмулятор и вернуть код завершения процесса.

    Сначала выводятся заданные параметры и загружается VFS, затем
    выполняется стартовый скрипт (если указан), после чего запускается
    интерактивный режим, если скрипт не завершил работу командой exit.
    """
    config = parse_args(argv)
    for line in config.dump():
        print(f"[debug] {line}", flush=True)
    vfs = open_vfs(config.vfs_path)
    if vfs is None:
        return EXIT_FAILURE
    shell = Shell(config, vfs)
    if config.script_path and not shell.run_script(config.script_path):
        return EXIT_FAILURE
    if not shell.running:
        return shell.exit_code
    return shell.repl()


if __name__ == "__main__":
    sys.exit(main())
