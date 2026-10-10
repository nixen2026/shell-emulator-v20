"""Команды для работы с виртуальной файловой системой: ls и cd."""

from emulator.errors import EXIT_FAILURE, EXIT_SUCCESS, ShellError
from emulator.parser import parse_options
from emulator.vfs import (CURRENT_DIR, HOME, NOT_A_DIRECTORY, VfsError,
                          display_path)

MAX_CD_ARGS = 1
SINGLE_PATH = 1
PREVIOUS_DIR = "-"
LONG_OPTION = "l"
SIZE_WIDTH = 8
DIR_TYPE = "d"
FILE_TYPE = "-"


def format_entry(name, node, long_format):
    """Отформатировать элемент для вывода ls.

    В длинном формате выводятся тип (``d`` — каталог, ``-`` — файл),
    размер (байты для файла, число элементов для каталога) и имя.
    """
    if not long_format:
        return name
    kind = DIR_TYPE if node.is_dir else FILE_TYPE
    return f"{kind} {node.size:>{SIZE_WIDTH}} {name}"


def print_entries(shell, entries, long_format):
    """Вывести список пар (имя, узел) в кратком или длинном формате."""
    lines = [format_entry(name, node, long_format)
             for name, node in sorted(entries, key=lambda item: item[0])]
    if long_format:
        for line in lines:
            shell.write(line)
    elif lines:
        shell.write("  ".join(lines))


def collect_targets(shell, paths):
    """Найти узлы для путей ls; вернуть (найденные пары, код ошибки)."""
    targets, status = [], EXIT_SUCCESS
    for path in paths:
        try:
            targets.append((path, shell.lookup(path)))
        except VfsError as exc:
            shell.error(f"ls: cannot access '{path}': {exc}")
            status = EXIT_FAILURE
    return targets, status


def cmd_ls(shell, args):
    """``ls [-l] [путь...]`` — вывести содержимое каталогов VFS.

    Без путей выводится текущий каталог. Для файла выводится его имя.
    При нескольких путях сначала выводятся файлы, затем каждый
    каталог с заголовком ``путь:``.
    """
    options, paths = parse_options("ls", args, LONG_OPTION)
    long_format = LONG_OPTION in options
    targets, status = collect_targets(shell, paths or [CURRENT_DIR])
    files = [item for item in targets if not item[1].is_dir]
    dirs = [item for item in targets if item[1].is_dir]
    print_entries(shell, files, long_format)
    with_headers = len(paths) > SINGLE_PATH
    for index, (path, node) in enumerate(dirs):
        if with_headers:
            if files or index:
                shell.write("")
            shell.write(f"{path}:")
        print_entries(shell, node.children.items(), long_format)
    return status


def cmd_cd(shell, args):
    """``cd [путь]`` — сменить текущий каталог VFS.

    Без аргумента и для ``~`` — переход в домашний каталог (корень VFS),
    ``cd -`` — возврат в предыдущий каталог с выводом его пути.
    """
    if len(args) > MAX_CD_ARGS:
        raise ShellError("cd: too many arguments")
    target = args[0] if args else HOME
    if target == PREVIOUS_DIR:
        parts = list(shell.old_cwd)
        shell.write(display_path(parts))
    else:
        parts = shell.resolve(target)
    try:
        node = shell.vfs.get_node(parts)
    except VfsError as exc:
        raise ShellError(f"cd: {target}: {exc}") from None
    if not node.is_dir:
        raise ShellError(f"cd: {target}: {NOT_A_DIRECTORY}")
    shell.old_cwd, shell.cwd = shell.cwd, parts
