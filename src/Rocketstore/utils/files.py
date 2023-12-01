"""
█▀ █▄█ █▀▀ █░█ █▀▀ █░█
▄█ ░█░ █▄▄ █▀█ ██▄ ▀▄▀

Author: <Anton Sychev> (anton at sychev dot xyz) 
files.py (c) 2023 
Created:  2023-10-31 21:02:10 
Desc: Rocket Store (Python) - files tools lock and umlock
Docs: documentation
"""

import os
import time


def file_lock(path_folder, file, lock_retry_interval=13):
    print("fileLock", path_folder, file)
    while True:
        try:
            source_path = os.path.join(path_folder, file)
            target_path = os.path.join(path_folder, "lockfile", file)

            if not os.path.exists(os.path.join(path_folder, "lockfile")):
                os.makedirs(os.path.join(path_folder, "lockfile"))

            os.symlink(source_path, target_path)
            return
        except FileExistsError:
            time.sleep(lock_retry_interval)


def file_unlock(path_folder, file):
    print("fileUnlock", path_folder, file)
    file_lock_name = os.path.join(path_folder, "lockfile", file)
    if os.path.exists(file_lock_name):
        os.unlink(file_lock_name)


def identifier_name_test(name):
    reserved_keywords = set([
        "do", "if", "in", "for", "let", "new", "try", "var", "case", "else", "enum",
        "eval", "null", "this", "true", "void", "with", "await", "break", "catch",
        "class", "const", "false", "super", "throw", "while", "yield", "delete",
        "export", "import", "public", "return", "static", "switch", "typeof",
        "default", "extends", "finally", "package", "private", "continue",
        "debugger", "function", "arguments", "interface", "protected", "implements",
        "instanceof"
    ])
    if name not in reserved_keywords and name.isidentifier():
        return True
    return False
