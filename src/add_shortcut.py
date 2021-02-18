from os import system, environ
import win32con
from win32gui import SendMessage
import sys
from winreg import (
    CloseKey, OpenKey, QueryValueEx, SetValueEx,
    HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE,
    KEY_ALL_ACCESS, KEY_READ, REG_EXPAND_SZ, REG_SZ
)
import os

# Test Git


def env_keys(user=True):
    if user:
        root = HKEY_CURRENT_USER
        subkey = 'Environment'
    else:
        root = HKEY_LOCAL_MACHINE
        subkey = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
    return root, subkey


def get_env(name, user=True):
    root, subkey = env_keys(user)
    key = OpenKey(root, subkey, 0, KEY_READ)
    try:
        value, _ = QueryValueEx(key, name)
    except WindowsError:
        return ''
    return value


def set_env(name, value):
    key = OpenKey(HKEY_CURRENT_USER, 'Environment', 0, KEY_ALL_ACCESS)
    SetValueEx(key, name, 0, REG_EXPAND_SZ, value)
    CloseKey(key)
    SendMessage(
        win32con.HWND_BROADCAST, win32con.WM_SETTINGCHANGE, 0, 'Environment')


def remove(paths, value):
    while value in paths:
        paths.remove(value)


def unique(paths):
    unique = []
    for value in paths:
        if value not in unique:
            unique.append(value)
    return unique


def prepend_env(name, values):
    for value in values:
        paths = get_env(name).split(';')
        remove(paths, '')
        paths = unique(paths)
        remove(paths, value)
        paths.insert(0, value)
        set_env(name, ';'.join(paths))


def prepend_env_pathext(values):
    prepend_env('PathExt_User', values)
    pathext = ';'.join([
        get_env('PathExt_User'),
        get_env('PathExt', user=False)
    ])
    set_env('PathExt', pathext)


if __name__ == '__main__':
    prepend_env('Path', [
        os.path.dirname(os.path.abspath(__file__))
    ])

    # allow running of these filetypes without having to type the extension
    prepend_env_pathext(['.bat'])
