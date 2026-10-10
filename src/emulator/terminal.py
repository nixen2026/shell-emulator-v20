"""Работа с терминалом: очистка экрана ANSI-последовательностями."""

import ctypes
import os

CLEAR_SEQUENCE = "\033[2J\033[3J\033[H"
WINDOWS_OS_NAME = "nt"
STD_OUTPUT_HANDLE = -11
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004


def enable_ansi():
    """Включить обработку ANSI-последовательностей в консоли Windows.

    В других ОС терминалы поддерживают их по умолчанию.
    """
    if os.name != WINDOWS_OS_NAME:
        return
    try:
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(
                handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)
    except (AttributeError, OSError):
        return


def clear_screen(out):
    """Очистить экран терминала и переместить курсор в начало."""
    enable_ansi()
    out.write(CLEAR_SEQUENCE)
    out.flush()
