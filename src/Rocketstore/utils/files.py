"""
█▀ █▄█ █▀▀ █░█ █▀▀ █░█
▄█ ░█░ █▄▄ █▀█ ██▄ ▀▄▀

Author: <Anton Sychev> (anton at sychev dot xyz) 
files.py (c) 2023 
Created:  2023-10-31 21:02:10 
Desc: Rocket Store (Python) - files tools lock and umlock, validator and file name corrections
Docs: documentation
License: 
    * MIT: (c) Paragi 2017, Simon Riget.
"""

import os
import re
import time

# TODO: rebuild / thing about locking files, no use folder lockfile
# https://stackoverflow.com/questions/489861/locking-a-file-in-python
# https://py-filelock.readthedocs.io/en/latest/
# from filelock import Timeout, FileLock


def file_lock(path_folder, file, lock_retry_interval=13):
    # print("fileLock", path_folder, file)
    while True:
        try:
            source_path = os.path.join(path_folder, file)
            target_path = os.path.join(path_folder, "lockfile", file)

            if not os.path.exists(os.path.join(path_folder, "lockfile")):
                os.makedirs(os.path.join(path_folder, "lockfile"))

            if not os.path.exists(target_path):
                os.symlink(source_path, target_path)
                break
            else:
                time.sleep(lock_retry_interval)
        except Exception as err:
            print("[390] -> filelock -> ", err)
            break


def file_unlock(path_folder, file):
    # print("fileUnlock", path_folder, file)
    file_lock_name = os.path.join(path_folder, "lockfile", file)
    if not os.path.exists(file_lock_name):
        return

    try:
        os.unlink(file_lock_name)
    except Exception as err:
        print("[410] file unlock ->", err)


def identifier_name_test(name: any) -> bool:
    '''
    check match name with regex
    its search for any non-ascii symbols and reserved words in javascript or combinations of them
    '''

    pattern = r"^(?!(?:do|if|in|for|let|new|try|var|case|else|enum|eval|null|this|true|void|with|await|break|catch|class|const|false|super|throw|while|yield|delete|export|import|public|return|static|switch|typeof|default|extends|finally|package|private|continue|debugger|function|arguments|interface|protected|implements|instanceof)\b)[^\x20-\x7E]|[^[:ascii:]]"

    check = re.search(pattern, name, re.MULTILINE | re.IGNORECASE)

    return bool(check)


def file_name_wash(name, preserve_wildcards=False) -> str:
    '''
    Internal functions File name washer
    '''
    if os.name == 'nt':
        n1 = name.replace(r'\*\?', '') if preserve_wildcards == False else name

        n2 = re.sub(r'[\/<>\\:\|"]', '', n1)
        n2 = re.sub(r'[\x00-\x1f\x80-\x9f]', '', n2)
        n2 = re.sub(r'^\.+$', '', n2)
        n2 = re.sub(
            r'^(con|prn|aux|nul|com[0-9]|lpt[0-9])(\..*)?$', '', n2, flags=re.IGNORECASE)
        n2 = re.sub(r'[\. ]+$', '', n2)

        return n2[:255]
    else:
        # remove / \ ~ zero and double
        return name.replace(r'[\/\\\x00~]', '').replace(r'[.]{2,}', '')
