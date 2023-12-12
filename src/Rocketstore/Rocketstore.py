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
  | record           |  row          |  file content          |
  +------------------+---------------+------------------------+
"""

import os
import json
import re
import glob
import errno
import shutil

from utils.files import file_lock, file_unlock, identifier_name_test, file_name_wash

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

# TODO: new binary json format


class Rocketstore:

    def __init__(self, **set_option) -> None:
        # https://docs.python.org/es/dev/library/tempfile.html
        # TODO: use tempdir
        self.data_storage_area = os.path.join(os.path.sep, "tmp", "rsdb")

        self.data_format = _FORMAT_JSON
        self.lock_retry_interval = 13
        self.lock_files = True
        self.key_cache = {}

        if set_option:
            self.options(**set_option)

    def options(self, **options) -> None:
        '''
        inital setup of Rocketstore
        @Sample:
            from Rocketstore import Rocketstore, _FORMAT_JSON, _FORMAT_NATIVE
            rs.options(**{
                "data_storage_area": "./",
                "data_format": _FORMAT_NATIVE
            })
        '''

        if "data_format" in options:
            if options["data_format"] in [_FORMAT_JSON, _FORMAT_XML, _FORMAT_NATIVE]:
                self.data_format = options.get("data_format", _FORMAT_JSON)
            else:
                raise ValueError(
                    f"Unknown data format: '{options['data_format']}'")

        if "data_storage_area" in options:
            if isinstance(options.get("data_storage_area"), str):
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

        if "lock_retry_interval" in options and isinstance(options["lock_retry_interval"], int):
            self.lock_retry_interval = options.get("lock_retry_interval", 13)

        if "lock_files" in options and isinstance(options["lock_files"], bool):
            self.lock_files = options.get("lock_files", True)

    def post(self, collection, key, record, flags=0) -> any:
        '''
        Post a data record (Insert or overwrite)
        If keyCache exists for the given collection, entries are added.
        '''
        collection = str(collection) if collection else ""

        if len(collection) < 1 or not collection:
            raise ValueError("No valid collection name given")

        if identifier_name_test(collection) == False:
            raise ValueError(
                "Collection name contains illegal characters")

        # Remove wildcards (unix only)
        if isinstance(key, int):
            key = file_name_wash(
                str(key)+"").replace(r"[\*\?]", "") if key else ""

        flags = flags if isinstance(flags, int) else 0

        # Insert a sequence
        if len(key) < 1 or flags & _ADD_AUTO_INC:
            _sequence = self.sequence(collection)
            key = f"{_sequence}-{key}" if key else str(_sequence)

        # Insert a Globally Unique IDentifier
        if flags & _ADD_GUID:
            uid = hex(int(os.urandom(8).hex(), 16))[2:]
            guid = f"{uid[:8]}-{uid[8:12]}-4000-8{uid[12:15]}-{uid[15:]}"
            key = f"{guid}-{key}" if len(key) > 0 else guid

        # Write to file
        dir_to_write = os.path.join(self.data_storage_area, collection)
        file_name = os.path.join(dir_to_write, key)

        if self.data_format & _FORMAT_JSON:
            os.makedirs(dir_to_write, exist_ok=True)

            with open(file_name, "w") as file:
                json.dump(record, file)
        else:
            raise ValueError("Sorry, that data format is not supported")

        # Store key in cash
        if isinstance(self.key_cache.get(collection), list) and key not in self.key_cache[collection]:
            self.key_cache[collection].append(key)

        return {"key": key, "count": 1}

    def get(self, collection, key, flags=0, min_time=None, max_time=None) -> any:
        print("\n-->", collection, key, flags, min_time, max_time)

        '''
         * Get one or more records or list all collections (or delete it)

            Generate a list:
                get collection key => list of one key
                get collection key wildcard => read to cash, filter to list
                get collections => no collection + key wildcard => read (no cashing), filter to list.

            Cashing:
            Whenever readdir is called, keys are stores in keyCache, pr. collection.
            The keyCache is maintained whenever a record is deleted or added.
            One exception are searches in the root (list of collections etc.), which must be read each time.

            NB: Files may have been removed manually and should be removed from the cache
        '''
        keys = []
        uncache = []
        records = []
        count = 0

        collection = str("" + collection or "") if collection else ""

        if collection and len(collection) > 0 and identifier_name_test(collection) == False:
            raise ValueError("Collection name contains illegal characters")

        # Check key validity
        key = file_name_wash("" + str(key)).replace(r"[*]{2,}", "*")

        # Scan directory
        scan_dir = os.path.join(
            self.data_storage_area, collection or "")

        wildcard = not "*" in key or not "?" in key or not key

        if wildcard and not (flags & _DELETE and not key):
            list = []

            # Read directory into cache
            if not collection or not collection in self.key_cache:
                try:
                    # list = os.scandir(scan_dir)
                    list = os.listdir(scan_dir)
                    print("->", list, list)

                    # Update cahce
                    if collection and len(list) > 0:
                        self.key_cache[collection] = list
                except FileNotFoundError as f:
                    raise f
                except Exception as e:
                    raise e

            if collection and collection in self.key_cache:
                list = self.key_cache[collection]

            # Wildcard search
            if key and key != "*":
                haystack = self.key_cache[collection] if collection else list
                keys = [k for k in haystack if glob.fnmatch.fnmatch(k, key)]
            else:
                keys = list

            # Order by key value
            if flags & (_ORDER | _ORDER_DESC) and keys and len(keys) > 1 and not (flags & (_DELETE | (flags & _COUNT))):
                keys.sort()
                if flags & _ORDER_DESC:
                    keys.reverse()
        else:
            if collection and isinstance(self.key_cache.get(collection), list) and key not in self.key_cache[collection]:
                keys = []
            elif key:
                keys = [key]

        count = len(keys)

        if len(keys) > 0 and collection and not (flags & (_KEYS | _COUNT | _DELETE)):
            records = [None] * len(keys)

            for i in range(len(keys)):
                file_name = os.path.join(scan_dir, keys[i])

                # Read JSON record file
                if self.data_format & _FORMAT_JSON:
                    try:
                        with open(file_name, 'r') as file:
                            records[i] = json.load(file)
                    except FileNotFoundError:
                        uncache.append(keys[i])
                        records[i] = "*deleted*"
                        count -= 1
                    except json.JSONDecodeError:
                        records[i] = ""
                else:
                    raise ValueError(
                        "Sorry, that data format is not supported")

        elif flags & _DELETE:
            if not collection and not key or collection == "" and key == "":
                # Delete database
                try:
                    if os.path.exists(self.data_storage_area):
                        shutil.rmtree(self.data_storage_area)
                        self.key_cache = {}
                        count = 1
                except Exception as e:
                    print(f"Error deleting directory: {e}")
                    raise e
            elif collection and not key:
                # Delete collection and sequences
                fileName = os.path.join(self.data_storage_area, collection)
                count = 0

                if os.path.exists(fileName):
                    statCheck = os.stat(fileName)

                    if statCheck.is_dir():
                        # Delete collection folder
                        shutil.rmtree(fileName)
                        count += 1

                    # Delete single file
                    fileNameSeq = f"{fileName}_seq"
                    if os.path.exists(fileNameSeq):
                        os.remove(fileNameSeq)
                        count += 1

                del self.key_cache[collection]

            # Delete records and  ( collection and sequences found with wildcards )
            elif keys:
                for key in keys:
                    os.remove(os.path.join(scan_dir, key))
                    if collection:
                        uncache = [key]
                    else:
                        uncache.extend([key])

        # Clean up cache and keys
        if uncache:
            if collection in self.key_cache:
                self.key_cache[collection] = [
                    e for e in self.key_cache[collection] if e not in uncache]

            if keys != self.key_cache.get(collection):
                keys = [e for e in keys if e not in uncache]

            if records:
                records = [e for e in records if e != "*deleted*"]

        result = {'count': count}
        if result['count'] and keys and not (flags & (_COUNT | _DELETE)):
            result['key'] = keys
        if records:
            result['result'] = records

        return result

    def delete(self, collection="", key=""):
        '''
        Delete one or more records or collections
        '''
        return self.get(collection=collection, key=key, flags=_DELETE)

    def sequence(self, seq_name: str) -> int:
        '''
        Get and auto incremented sequence or create it
        '''
        if not seq_name:
            raise ValueError("Sequence name is invalid")

        sequence = -1

        name = file_name_wash(seq_name)
        name = seq_name.replace("*", "").replace("?", "")

        if len(name) < 1 or not isinstance(name, str):
            raise ValueError("Sequence name is invalid")

        name += "_seq"
        file_name = os.path.join(self.data_storage_area, name)

        if self.lock_files:
            file_lock(self.data_storage_area, name)

        try:
            with open(file_name, "r") as file:
                data = file.read()
            sequence = int(data) + 1

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

        if self.lock_files:
            file_unlock(self.data_storage_area, name)

        return sequence
