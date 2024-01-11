"""
█▀ █▄█ █▀▀ █░█ █▀▀ █░█
▄█ ░█░ █▄▄ █▀█ ██▄ ▀▄▀

Author: <Anton Sychev> (anton at sychev dot xyz) 
main.py (c) 2023 
Created:  2023-10-31 21:03:32 
Desc: Rocket Store (Python) - main module code ported from Node.js version (https://github.com/paragi/rocket-store-node)
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

from .utils.files import file_lock, file_unlock, identifier_name_test, file_name_wash
import os
import json
import re
import glob
import errno
import shutil
import time

import logging

logging.basicConfig(
    format="%(levelname)s: %(message)s",
)


# TODO: new binary json format
# _FORMAT_BSON = 0x09 #https://en.wikipedia.org/wiki/BSON
# _FORMAT_PROTOBUF = 0x10 #https://protobuf.dev/
# https://en.wikipedia.org/wiki/Protocol_Buffers

# TODO: checker last modified file time if exist lockfile and is to much longuer (to unlock it)


class Rocketstore:
    # Constants
    _ORDER = 0x01  # Sort ASC
    _ORDER_DESC = 0x02  # Sort DESC
    _ORDERBY_TIME = 0x04  # Sort by time not implemented
    _LOCK = 0x08  # Lock file
    _DELETE = 0x10  # Delete file / collection / database
    _KEYS = 0x20  # Return keys only
    _COUNT = 0x40  # Return count only
    _ADD_AUTO_INC = 0x01  # Add auto incrementing sequence to key
    _ADD_GUID = 0x02  # Add Globally Unique IDentifier to key (RFC 4122)
    _FORMAT_JSON = 0x01  # Store data in JSON format
    _FORMAT_NATIVE = 0x02  # Store data in native format (JSON)
    _FORMAT_XML = 0x04  # Store data in XML format
    _FORMAT_PHP = 0x08  # Store data in PHP format

    data_storage_area: str = os.path.join(os.path.sep, "tmp", "rsdb")

    def __init__(self, **set_option) -> None:
        # https://docs.python.org/es/dev/library/tempfile.html
        # TODO: use tempdir
        self.data_format = self._FORMAT_JSON
        self.lock_retry_interval = 13
        self.lock_files = True
        self.key_cache = {}

        if set_option:
            self.options(**set_option)

    def options(self, **options) -> None:
        """
        inital setup of Rocketstore
        @Sample:
            from Rocketstore import Rocketstore
            rs.options(**{
                "data_storage_area": "./",
                "data_format": Rocketstore._FORMAT_NATIVE
            })
        """

        if "debug" in options and isinstance(options["debug"], bool):
            if options["debug"] == True:
                logging.getLogger().setLevel(logging.DEBUG)
            else:
                logging.getLogger().setLevel(logging.ERROR)

        if "data_format" in options:
            if options["data_format"] in [
                self._FORMAT_JSON,
                self._FORMAT_XML,
                self._FORMAT_NATIVE,
            ]:
                self.data_format = options.get(
                    "data_format", self._FORMAT_JSON)
            else:
                raise ValueError(
                    f"Unknown data format: '{options['data_format']}'")

        if "data_storage_area" in options:
            if isinstance(options.get("data_storage_area"), str):
                self.data_storage_area = options["data_storage_area"]
                try:
                    os.makedirs(
                        os.path.abspath(self.data_storage_area),
                        mode=0o775,
                        exist_ok=True,
                    )
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise Exception(
                            f"Unable to create data storage directory '{self.data_storage_area}': {e}"
                        )
            else:
                raise ValueError("Data storage area must be a directory path")

        if "lock_retry_interval" in options and isinstance(
            options["lock_retry_interval"], int
        ):
            self.lock_retry_interval = options.get("lock_retry_interval", 13)

        if "lock_files" in options and isinstance(options["lock_files"], bool):
            self.lock_files = options.get("lock_files", True)

    def post(self, collection=None, key=None, record=None, flags=0) -> any:
        """
        Post a data record (Insert or overwrite)
        If keyCache exists for the given collection, entries are added.
        @collection: collection name
        @key: key name
        @record: data to store
        @flags: flags
        @return: dict
            _ADD_AUTO_INC: add auto incrementing sequence to key
                {'key': '6-test-1', 'count': 1}
            _ADD_GUID: add Globally Unique IDentifier to key
                {'key': '5e675199-7680-4000-856b--test-1', 'count': 1}
        """
        collection = str(collection or "") if collection else ""

        if len(collection) < 1 or not collection or collection == "":
            raise ValueError("No valid collection name given")

        # True = is have illegal characters
        if identifier_name_test(collection) == True:
            raise ValueError("Collection name contains illegal characters")

        # Remove wildcards (unix only)
        if isinstance(key, int):
            key = file_name_wash(
                str(key) + "").replace(r"[\*\?]", "") if key else ""

        flags = flags if isinstance(flags, int) else 0

        if key == None:
            key = ""

        # Insert a sequence
        if len(key) < 1 or flags & self._ADD_AUTO_INC:
            _sequence = self.sequence(collection)
            key = f"{_sequence}-{key}" if key else str(_sequence)

        # Insert a Globally Unique IDentifier
        if flags & self._ADD_GUID:
            uid = hex(int(os.urandom(8).hex(), 16))[2:]
            guid = f"{uid[:8]}-{uid[8:12]}-4000-8{uid[12:15]}-{uid[15:]}"
            key = f"{guid}-{key}" if len(key) > 0 else guid

        # Write to file
        dir_to_write = os.path.abspath(
            os.path.join(self.data_storage_area, collection))
        file_name = os.path.join(dir_to_write, key)

        if self.data_format & self._FORMAT_JSON:
            os.makedirs(dir_to_write, mode=0o775, exist_ok=True)

            with open(file_name, "w") as file:
                json.dump(record, file)
        else:
            raise ValueError("Sorry, that data format is not supported")

        # Store key in cash
        if (
            isinstance(self.key_cache.get(collection), list)
            and key not in self.key_cache[collection]
        ):
            self.key_cache[collection].append(key)

        return {"key": key, "count": 1}

    def get(
        self, collection=None, key=None, flags=0, min_time=None, max_time=None
    ) -> any:
        """
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
        """
        keys = []
        uncache = []
        records = []
        count = 0

        collection = str(collection or "") if collection else ""

        # identifier_name_test - True = is have illegal characters
        if (
            collection
            and len(collection) > 0
            and identifier_name_test(collection) == True
        ):
            raise ValueError("Collection name contains illegal characters")

        # Check key validity
        if key == None:
            key = ""
        else:
            key = file_name_wash(str(key)).replace(r"[*]{2,}", "*")

        scan_dir = os.path.abspath(os.path.join(
            self.data_storage_area, collection))

        wildcard = not "*" in key or not "?" in key or key == "" or not key

        if wildcard and not (flags & self._DELETE and (not key or key == "")):
            _list = []

            # Read directory into cache
            if collection and not collection in self.key_cache:
                # Scan directory
                try:
                    _list = os.listdir(scan_dir)

                    # Remove .DS_Store files
                    _list = [
                        e for e in _list if not e.lower().endswith(".ds_store")]

                    # Update cache
                    if collection and len(_list) > 0:
                        self.key_cache[collection] = _list
                except FileNotFoundError as f:
                    # raise f
                    return {"count": 0}
                except Exception as e:
                    raise e

            if collection and collection in self.key_cache:
                _list = self.key_cache[collection]

            # Wildcard search
            if key and key != "*":
                haystack = (
                    self.key_cache[collection]
                    if collection in self.key_cache
                    else _list
                )
                keys = [k for k in haystack if glob.fnmatch.fnmatch(k, key)]
            else:
                keys = _list

            # Order by key value
            if (
                flags & (self._ORDER | self._ORDER_DESC)
                and keys
                and len(keys) > 1
                and not (flags & (self._DELETE | (flags & self._COUNT)))
            ):
                keys.sort()
                if flags & self._ORDER_DESC:
                    keys.reverse()
        else:
            if (
                collection
                and isinstance(self.key_cache.get(collection), list)
                and key not in self.key_cache[collection]
            ):
                keys = []
            elif key:
                keys = [key]

        count = len(keys)

        if (
            len(keys) > 0
            and collection
            and not (flags & (self._KEYS | self._COUNT | self._DELETE))
        ):
            records = [None] * len(keys)

            for i in range(len(keys)):
                file_name = os.path.join(scan_dir, keys[i])

                # Read JSON record file
                if self.data_format & self._FORMAT_JSON:
                    try:
                        with open(file_name, "r") as file:
                            logging.info(f">[269] File open {file_name}")
                            records[i] = json.load(file)
                    except FileNotFoundError:
                        uncache.append(keys[i])
                        records[i] = "*deleted*"
                        count -= 1
                        logging.warning(f">[269] File not found{file_name}")
                    except json.JSONDecodeError:
                        records[i] = "*format*"
                        logging.warning(f">[272] Not JSON format {file_name}")
                else:
                    raise ValueError(
                        "Sorry, that data format is not supported")

        elif flags & self._DELETE:
            # DELETE RECORDS
            logging.info(f"276 DELETE: c({collection}) k({key})")

            if (
                not collection
                and not key
                or collection == ""
                and not key
                or collection == ""
                and key == ""
            ):
                logging.info(
                    "# Delete database (all collections) return count 1")
                try:
                    if os.path.exists(self.data_storage_area):
                        shutil.rmtree(self.data_storage_area)
                        self.key_cache = {}
                        count = 1
                except Exception as e:
                    logging.info(f"Error deleting directory: {e}")
                    raise e

            elif (
                collection
                and not key
                or collection == ""
                and not key
                or collection
                and key == ""
            ):
                logging.info("# Delete complete collection")
                fileName = os.path.join(self.data_storage_area, collection)
                fileNameSeq = os.path.join(
                    self.data_storage_area, f"{collection}_seq")
                count = 0

                # Delete single file
                if os.path.exists(fileName):
                    if os.path.isfile(fileName):
                        os.remove(fileName)

                    if os.path.isdir(fileName):
                        shutil.rmtree(fileName)

                    count += 1

                # Delete single file sequence
                if os.path.exists(fileNameSeq):
                    os.remove(fileNameSeq)
                    count += 1

                if collection in self.key_cache:
                    del self.key_cache[collection]

            # Delete records and  ( collection and sequences found with wildcards )
            elif keys:
                logging.info("delete wildcat")
                for key in keys:
                    # Remove files with regexp
                    if "*" in key or "?" in key:
                        loc = glob.glob(os.path.join(scan_dir, key))
                        for file in loc:
                            if os.path.exists(file):
                                shutil.rmtree(file)
                                count += len(loc) - count
                    else:
                        # Delete single file
                        os.remove(os.path.join(scan_dir, key))

                    if collection:
                        uncache = [key]
                    else:
                        uncache.extend([key])

            elif re.search(r"[\*\?]", key):
                logging.info("WILD con caracteres especiales")
                fileNamesWild = glob.glob(os.path.join(scan_dir, key))
                for file in fileNamesWild:
                    os.remove(file)
                    count += 1

        # Clean up cache and keys
        if uncache:
            if collection in self.key_cache:
                self.key_cache[collection] = [
                    e for e in self.key_cache[collection] if e not in uncache
                ]

            if keys != self.key_cache.get(collection):
                keys = [e for e in keys if e not in uncache]

            if records:
                records = [e for e in records if e !=
                           "*deleted*" or e != "*format*"]

        result = {"count": count}
        if result["count"] and keys and not (flags & (self._COUNT | self._DELETE)):
            result["key"] = keys
        if records:
            result["result"] = records

        return result

    def delete(self, collection=None, key=None):
        """
        Delete one or more records or collections
        """
        return self.get(collection=collection, key=key, flags=self._DELETE)

    def sequence(self, seq_name: str) -> int:
        """
        Get and auto incremented sequence or create it
        """
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
            file_lock(os.path.realpath(self.data_storage_area), name)

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
                logging.warning(f"Error creating file: {e}")
                raise e
        except Exception as e:
            logging.warning(f"Error reading/writing file: {e}")
            raise e

        if self.lock_files:
            file_unlock(os.path.realpath(self.data_storage_area), name)

        return sequence
