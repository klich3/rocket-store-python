"""
█▀ █▄█ █▀▀ █░█ █▀▀ █░█
▄█ ░█░ █▄▄ █▀█ ██▄ ▀▄▀

Author: <Anton Sychev> (anton at sychev dot xyz) 
main.py (c) 2023 
Created:  2023-10-31 21:03:32 
Desc: Rocket Store (Python) - main module code
Docs: documentation
License: 
    * MIT: (c) Paragi 2017, Simon Riget.
Terminology:
  Rocketstore was made to replace a more complex database, in a setting that didn't quite need that level of functionality.
  Rocketstore is intended to store and retrieve records/documents, organized in collections, using a key.

  to translate between rocketstore sql and file system terms:
  +------------------+---------------+------------------------+
  | storage area     |  database     |  data directory root   |
  +------------------+---------------+------------------------+
  | collection       |  table        |  directory             |
  +------------------+---------------+------------------------+
  | key              |  key          |  file name             |
  +------------------+---------------+------------------------+
  | record           |  row          |  file                  |
  +------------------+---------------+------------------------+
"""

import os
import json
import re
import glob
import errno
import shutil

# import files

# Constants
_ORDER = 0x01
_ORDER_DESC = 0x02
_ORDERBY_TIME = 0x04
_LOCK = 0x08
_DELETE = 0x10
_KEYS = 0x20
_COUNT = 0x40
_ADD_AUTO_INC = 0x01
_ADD_GUID = 0x02
_FORMAT_JSON = 0x01
_FORMAT_NATIVE = 0x02
_FORMAT_XML = 0x04
_FORMAT_PHP = 0x08


class Rocketstore:
    def __init__(self, set_option=None):
        self.data_storage_area = os.path.join(os.path.sep, "tmp", "rsdb")
        self.data_format = FORMAT_JSON
        self.lock_retry_interval = 13
        self.lock_files = True
        self.key_cache = {}

        if set_option:
            self.options(set_option)

    async def options(self, options):
        if "data_format" in options:
            if options["data_format"] & (FORMAT_JSON | FORMAT_XML | FORMAT_NATIVE):
                self.data_format = options["data_format"]
            else:
                raise ValueError(
                    f"Unknown data format: '{options['data_format']}'")

        if "data_storage_area" in options:
            if isinstance(options["data_storage_area"], (str, int)):
                self.data_storage_area = os.path.abspath(
                    options["data_storage_area"])
                try:
                    os.makedirs(self.data_storage_area,
                                mode=0o775, exist_ok=True)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise Exception(
                            f"Unable to create data storage directory '{self.data_storage_area}': {e}")

            else:
                raise ValueError("Data storage area must be a directory path")

        if "lock_retry_interval" in options:
            if isinstance(options["lock_retry_interval"], int):
                self.lock_retry_interval = options["lock_retry_interval"]

        if "lock_files" in options:
            if isinstance(options["lock_files"], bool):
                self.lock_files = options["lock_files"]

    async def post(self, collection, key, record, flags=0):
        collection = str(collection)
        if len(collection) < 1:
            raise ValueError("No valid collection name given")

        if not self._is_valid_identifier(collection):
            raise ValueError(
                "Collection name contains illegal characters (For a JavaScript identifier)")

        # Remove wildcards (unix only)
        key = str(key).replace("*", "").replace("?", "")

        if not isinstance(flags, int):
            flags = 0

        if len(key) < 1 or flags & ADD_AUTO_INC:
            sequence = await self.sequence(collection)
            key = f"{sequence}-{key}" if len(key) > 0 else str(sequence)

        if flags & ADD_GUID:
            uid = hex(int(os.urandom(8).hex(), 16))[2:]
            guid = f"{uid[:8]}-{uid[8:12]}-4000-8{uid[12:15]}-{uid[15:]}"
            key = f"{guid}-{key}" if len(key) > 0 else guid

        file_name = os.path.join(self.data_storage_area, collection, key)

        if self.data_format & FORMAT_JSON:
            if not os.path.exists(file_name):
                os.makedirs(os.path.dirname(file_name), exist_ok=True)
            with open(file_name, "w") as file:
                json.dump(record, file)
        else:
            raise ValueError("Sorry, that data format is not supported")

        if collection not in self.key_cache:
            self.key_cache[collection] = []
        if key not in self.key_cache[collection]:
            self.key_cache[collection].append(key)

        return {"key": key, "count": 1}

    async def get(self, collection, key, flags=0, min_time=None, max_time=None):
        keys = []
        uncache = []
        records = []
        count = 0

        collection = str(collection) if collection else ""
        if collection and not self._is_valid_identifier(collection):
            raise ValueError(
                "Collection name contains illegal characters (For a JavaScript identifier)")

        key = self._clean_key(str(key)) if key else ""

        scan_dir = os.path.join(
            self.data_storage_area, collection) if collection else self.data_storage_area
        wildcard = "*" in key or "?" in key or not key

        if wildcard and not (flags & DELETE and not key):
            try:
                if collection and self.key_cache.get(collection):
                    keys = self.key_cache[collection]
                else:
                    keys = os.listdir(scan_dir)
                    if collection:
                        self.key_cache[collection] = keys

                if key and key != "*":
                    regex = re.compile(
                        "^" + re.escape(key).replace("\\*",
                                                     ".*").replace("\\?", ".") + "$"
                    )
                    keys = [k for k in keys if regex.match(k)]
            except FileNotFoundError:
                keys = []
        else:
            if collection and self.key_cache.get(collection) and key in self.key_cache[collection]:
                keys = [key]
            elif key:
                keys = [key]

        count = len(keys)

        if keys and collection and not (flags & (KEYS | COUNT | DELETE)):
            for k in keys:
                file_name = os.path.join(scan_dir, k)
                if self.data_format & FORMAT_JSON:
                    try:
                        with open(file_name, "r") as file:
                            records.append(json.load(file))
                    except FileNotFoundError:
                        uncache.append(k)
                        records.append("*deleted*")
                        count -= 1
                else:
                    raise ValueError(
                        "Sorry, that data format is not supported")

        elif flags & DELETE:
            if not collection and not key:
                if os.path.exists(self.data_storage_area):
                    shutil.rmtree(self.data_storage_area)
                    self.key_cache = {}
                    count = 1
            elif collection and not key:
                collection_dir = os.path.join(
                    self.data_storage_area, collection)
                if os.path.exists(collection_dir):
                    shutil.rmtree(collection_dir)
                    self.key_cache.pop(collection, None)
                    count = 1
            elif keys:
                for k in keys:
                    file_name = os.path.join(scan_dir, k)
                    os.remove(file_name)
                    uncache.append(k)

        if uncache:
            if collection and self.key_cache.get(collection):
                self.key_cache[collection] = [
                    k for k in self.key_cache[collection] if k not in uncache]
            keys = [k for k in keys if k not in uncache]
            records = [r for r in records if r != "*deleted*"]

        result = {"count": count}
        if count and keys and not (flags & (KEYS | COUNT | DELETE)):
            result["key"] = keys
        if records:
            result["result"] = records

        return result

    async def delete(self, collection, key):
        return await self.get(collection, key, DELETE)

    async def sequence(self, seq_name):
        if not seq_name:
            raise ValueError("Sequence name is invalid")

        name = self._clean_key(seq_name)
        if not name:
            raise ValueError("Sequence name is invalid")

        name += "_seq"
        file_name = os.path.join(self.data_storage_area, name)

        if self.lock_files:
            self._file_lock(file_name)

        try:
            with open(file_name, "r") as file:
                sequence = int(file.read()) + 1
            with open(file_name, "w") as file:
                file.write(str(sequence))
        except FileNotFoundError:
            try:
                os.makedirs(os.path.dirname(file_name), exist_ok=True)
                with open(file_name, "w") as file:
                    file.write("1")
                sequence = 1
            except Exception as e:
                print(f"Error creating file: {e}")
                raise e
        except Exception as e:
            print(f"Error reading/writing file: {e}")
            raise e
        finally:
            if self.lock_files:
                self._file_unlock(file_name)

        return sequence

    def _clean_key(self, key):
        return key.replace("*", "").replace("?", "")

    def _is_valid_identifier(self, identifier):
        return re.match("^[a-zA-Z_][a-zA-Z0-9_]*$", identifier) is not None

    def _file_lock(self, file_name):
        # Implement file locking logic here
        pass

    def _file_unlock(self, file_name):
        # Implement file unlocking logic here
        pass
