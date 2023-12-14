# Rocket-Store Python

[![MIT license](http://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT)
[![Issues](http://img.shields.io/github/issues/klich3/rocket-store-python.svg)]( https://github.com/klich3/rocket-store-python/issues )
[![GitHub pull-requests](https://img.shields.io/github/issues-pr/paragi/rocket-store.svg)](https://github.com/klich3/rocket-store-python/pull/)

***Using the filesystem as a searchable database.***

Rocket-Store is a high performance solution to simple data storage and retrieval. It's taking advantage of modern file system's exceptionally advanced cashing mechanisms.

***ORIGINAL / NODE VERSION:*** https://github.com/Paragi/rocket-store/

---

# Basic terminology

Rocket-Store was made to replace a more complex database, in a setting that required a low footprint and high performance.

Rocket-Store is intended to store and retrieve records/documents, organized in collections, using a key.

Terms used:
* __Collection__: name of a collections of records. (Like an SQL table)
* __Record__: the data store. (Like an SQL row)
* __Data storage area__: area/directory where collections are stored. (Like SQL data base)
* __Key__: every record has exactly one unique key, which is the same as a file name (same restrictions) and the same wildcards used in searches.

Compare Rocket-Store, SQL and file system terms:

| Rocket-Store | SQL| File system |
|---|---|---
| __storage area__     |  database     |  data directory root   |
| __collection__       |  table        |  directory             |
| __key__              |  key          |  file name             |
| __record__           |  row          |  file                  |


### Post

```python
sample
```

Stores a record in a collection identified by a unique key

__Collection__ name to contain the records.

__Key__ uniquely identifying the record

No path separators or wildcards etc. are allowed in collection names and keys.
Illigal charakters are silently striped off.

__Options__
  * _ADD_AUTO_INC:  Add an auto incremented sequence to the beginning of the key
  * _ADD_GUID: Add a Globally Unique IDentifier to the key

__Returns__ an associative array containing the result of the operation:
* count : number of records affected (1 on succes)
* key:   string containing the actual key used


If the key already exists, the record will be replaced.

If no key is given, an auto-incremented sequence is used as key.

If the function fails for any reason, an error is thrown.

### Get

Find and retrieve records, in a collection.

```python
sample
```

__Collection__ to search. If no collection name is given, get will return a list of data base assets: collections and sequences etc.

__Key__ to search for. Can be mixed with wildcards '\*' and '?'. An undefined or empty key is the equivalent of '*'

__Options__:
  * _ORDER       : Results returned are ordered alphabetically ascending.
  * _ORDER_DESC  : Results returned are ordered alphabetically descending.
  * _KEYS        : Return keys only (no records)
  * _COUNT       : Return record count only

__Return__ an array of
* count   : number of records affected
* key     : array of keys
* result  : array of records

NB: wildcards are very expensive on large datasets with most filesystems.
(on a regular PC with +10^7 records in the collection, it might take up to a second to retreive one record, whereas one might retrieve up to 100.000 records with an exact key match)

### Delete
Delete one or more records, whos key match.

```python
smmple
```

__Collection__ to search. If no collection is given, **THE WHOLE DATA BASE IS DELETED!**

__Key__ to search for. Can be mixed with wildcards '\*' and '?'. If no key is given, **THE ENTIRE COLLECTION INCLUDING SEQUENCES IS DELETED!**

__Return__ an array of
* count : number of records or collections affected

### Options


|index name|values|
|---|---|
|data_storage_area | The directory where the database resides. The default is to use a subdirectory to the temporary directory provided by the operating system. If that doesn't work, the DOCUMENT_ROOT directory is used. |
|data_format       | Specify which format the records are stored in. Values are: _FORMAT_NATIVE - default. and RS_FORMAT_JSON - Use JSON data format.|


#### Inserting with Globally Unique IDentifier key
Another option is to add a GUID to the key.
The GUID is a combination of a timestamp and a random sequence, formatet in accordance to  RFC 4122 (Valid but slightly less random)

If ID's are generated more than 1 millisecond apart, they are 100% unique.
If two ID's are generated at shorter intervals, the likelyhod of collission is up to 1 of 10^15.

---


# TODO
[x] CITAITON
[x] LICENSE
[x] Test
[x] lock files
[ ] https://github.com/pkaminski/sample/blob/master/setup.cfg
[ ] Publish to pypi
[ ] Update readme

### Docs:
* https://packaging.python.org/en/latest/tutorials/packaging-projects/
* https://realpython.com/pypi-publish-python-package/