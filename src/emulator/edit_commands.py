"""Команды, изменяющие VFS: rm и mv.

Все изменения выполняются только в памяти; файл-источник VFS
на диске не изменяется.
"""

from emulator.errors import EXIT_FAILURE, EXIT_SUCCESS, ShellError
from emulator.parser import parse_options
from emulator.vfs import NO_SUCH_FILE, SEPARATOR, is_prefix, replace_prefix

RECURSIVE_OPTION = "r"
FORCE_OPTION = "f"
MIN_MV_OPERANDS = 2
SINGLE_SOURCE = 1


def apply_to_each(shell, items, action):
    """Применить ``action`` к каждому элементу, сообщая об ошибках.

    Ошибка одного элемента не прерывает обработку остальных.
    Возвращает код завершения команды.
    """
    status = EXIT_SUCCESS
    for item in items:
        try:
            action(item)
        except ShellError as exc:
            shell.error(str(exc))
            status = EXIT_FAILURE
    return status


def remove_path(shell, path, options):
    """Удалить из VFS один путь команды rm с учётом опций."""
    parts = shell.resolve(path)
    if not parts:
        raise ShellError(f"rm: refusing to remove root directory '{path}'")
    node = shell.vfs.find(parts)
    if node is None:
        if FORCE_OPTION in options:
            return
        raise ShellError(f"rm: cannot remove '{path}': {NO_SUCH_FILE}")
    if node.is_dir and RECURSIVE_OPTION not in options:
        raise ShellError(f"rm: cannot remove '{path}': Is a directory")
    if is_prefix(parts, shell.cwd):
        raise ShellError(f"rm: cannot remove '{path}': "
                         f"current directory is inside it")
    shell.vfs.detach(parts)


def cmd_rm(shell, args):
    """``rm [-r] [-f] путь...`` — удалить файлы и каталоги из VFS.

    Каталог удаляется только с опцией ``-r`` (вместе с содержимым).
    Опция ``-f`` подавляет ошибку для несуществующих путей.
    """
    options, paths = parse_options(
        "rm", args, RECURSIVE_OPTION + FORCE_OPTION)
    if not paths:
        if FORCE_OPTION in options:
            return EXIT_SUCCESS
        raise ShellError("rm: missing operand")
    return apply_to_each(
        shell, paths, lambda path: remove_path(shell, path, options))


def check_move(shell, names, src, dst, node):
    """Проверить, что перемещение ``src`` в ``dst`` допустимо.

    ``names`` — пара (исходный путь, путь назначения) для сообщений.
    """
    source, shown = names
    if src == dst:
        raise ShellError(f"mv: '{source}' and '{shown}' are the same file")
    if is_prefix(src, dst):
        raise ShellError(f"mv: cannot move '{source}' to a subdirectory "
                         f"of itself, '{shown}'")
    existing = shell.vfs.find(dst)
    if existing is None:
        parent = shell.vfs.find(dst[:-1])
        if parent is None or not parent.is_dir:
            raise ShellError(f"mv: cannot move '{source}' to '{shown}': "
                             f"{NO_SUCH_FILE}")
    elif existing.is_dir:
        raise ShellError(f"mv: cannot overwrite directory '{shown}'")
    elif node.is_dir:
        raise ShellError(f"mv: cannot overwrite non-directory '{shown}' "
                         f"with directory '{source}'")


def move_path(shell, source, target, into_dir):
    """Переместить (переименовать) один путь команды mv.

    Если ``into_dir`` истинно, ``target`` — существующий каталог,
    и источник перемещается в него под своим именем.
    """
    src = shell.resolve(source)
    node = shell.vfs.find(src)
    if node is None:
        raise ShellError(f"mv: cannot stat '{source}': {NO_SUCH_FILE}")
    if not src:
        raise ShellError(f"mv: cannot move root directory '{source}'")
    dst = shell.resolve(target)
    shown = target
    if into_dir:
        dst = dst + [src[-1]]
        shown = target.rstrip(SEPARATOR) + SEPARATOR + src[-1]
    check_move(shell, (source, shown), src, dst, node)
    shell.vfs.detach(src)
    shell.vfs.attach(dst, node)
    shell.cwd = replace_prefix(shell.cwd, src, dst)
    shell.old_cwd = replace_prefix(shell.old_cwd, src, dst)


def cmd_mv(shell, args):
    """``mv источник... назначение`` — переместить или переименовать.

    Если назначение — существующий каталог, источники перемещаются
    в него. Иначе единственный источник переименовывается; существующий
    файл назначения заменяется.
    """
    _, operands = parse_options("mv", args, "")
    if not operands:
        raise ShellError("mv: missing file operand")
    if len(operands) < MIN_MV_OPERANDS:
        raise ShellError(
            f"mv: missing destination file operand after '{operands[0]}'")
    *sources, target = operands
    target_node = shell.vfs.find(shell.resolve(target))
    into_dir = target_node is not None and target_node.is_dir
    if len(sources) > SINGLE_SOURCE and not into_dir:
        raise ShellError(f"mv: target '{target}' is not a directory")
    return apply_to_each(
        shell, sources,
        lambda source: move_path(shell, source, target, into_dir))
