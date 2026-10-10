"""Разбор строки ввода на команду и аргументы, разбор опций команд."""

from emulator.errors import ShellError

BYTE_ORDER_MARK = "﻿"
COMMENT_CHAR = "#"
OPTION_PREFIX = "-"


def strip_comment(line):
    """Удалить комментарий: всё от символа ``#`` до конца строки.

    Синтаксис комментариев совпадает с синтаксисом языка Python.
    """
    return line.split(COMMENT_CHAR, 1)[0]


def parse_line(line):
    """Разделить строку на команду и аргументы по пробелам.

    Возвращает список слов: первый элемент — имя команды,
    остальные — её аргументы. Пустая строка и строка, состоящая
    только из комментария, дают пустой список. Метка порядка байтов
    (BOM), которую добавляют некоторые терминалы при передаче ввода
    через конвейер, отбрасывается.
    """
    return strip_comment(line.replace(BYTE_ORDER_MARK, "")).split()


def parse_options(command, args, allowed):
    """Разобрать короткие опции вида ``-a``, ``-ab`` у команды.

    ``allowed`` — строка допустимых букв опций. Возвращает пару
    (множество опций, список остальных аргументов-операндов).
    Аргумент ``-`` считается операндом. Недопустимая опция — ошибка.
    """
    options, operands = set(), []
    for arg in args:
        if not arg.startswith(OPTION_PREFIX) or arg == OPTION_PREFIX:
            operands.append(arg)
            continue
        for letter in arg[len(OPTION_PREFIX):]:
            if letter not in allowed:
                raise ShellError(
                    f"{command}: invalid option -- '{letter}'")
            options.add(letter)
    return options, operands
