"""
█▀ █▄█ █▀▀ █░█ █▀▀ █░█
▄█ ░█░ █▄▄ █▀█ ██▄ ▀▄▀

Author: <Anton Sychev> (anton at sychev dot xyz) 
test.py (c) 2023 
Created:  2023-12-01 01:01:52 
Desc: Test file of funcionality
Docs: documentation
"""

import unittest
import os
import json
from pathlib import PurePath

from Rocketstore import Rocketstore, _FORMAT_JSON, _FORMAT_NATIVE, _FORMAT_XML, _ADD_AUTO_INC, _ORDER_DESC, _ADD_GUID

rs = Rocketstore(**{
    "data_storage_area": "./test/ddbb",
    "data_format": _FORMAT_JSON
})


record = {
    "id": 22756,
    "name": "Adam Smith",
    "title": "developer",
    "email": "adam@smith.com",
    "phone": "+95 555 12345",
    "zip": "DK4321",
    "country": "Distan",
    "address": "Elm tree road 555",
}

rs.delete()


class TestStorage(unittest.TestCase):
    def test_bad_data_format_option(self):
        with self.assertRaises(ValueError):
            rs.options(**{
                "data_storage_area": "./",
                "data_format": "a"
            })

    def test_set_options_on_main_object(self):
        rs.options(**{
            "data_storage_area": "./",
            "data_format": _FORMAT_NATIVE
        })

        self.assertEqual(rs.data_storage_area, "./")
        self.assertEqual(rs.data_format, _FORMAT_NATIVE)

    def test_set_options_to_unwritable_directory(self):
        with self.assertRaises(Exception):
            rs.options(**{
                "data_storage_area": "/rsdb/sdgdf",
                "data_format": _FORMAT_NATIVE
            })

    def test_records(self):
        # Post_a_record
        self.assertEqual(rs.post("person", f"{record['id']}-{record['name']}", record), {
            "key":  "22756-Adam Smith",
            "count": 1,
        })

        # Create_sequence
        self.assertEqual(rs.sequence("first"), 1)
        self.assertEqual(rs.sequence("first"), 2)

        # Reposet a record
        record["test"] = 27

        self.assertEqual(rs.post("person", f"{record['id']}-{record['name']}", record), {
            "key": "22756-Adam Smith",
            "count": 1,
        })

        self.assertEqual(rs.get("person", f"{record['id']}-{record['name']}"), {'count': 1, 'key': ['22756-Adam Smith'], 'result': [{'id': 22756, 'name': 'Adam Smith',
                         'title': 'developer', 'email': 'adam@smith.com', 'phone': '+95 555 12345', 'zip': 'DK4321', 'country': 'Distan', 'address': 'Elm tree road 555', 'test': 27}]})

        # Post_a_record_with_empty_key
        self.assertEqual(rs.post("person", "", record),
                         {'count': 1, 'key': '1'})
        self.assertEqual(rs.post("person", "key", record, _ADD_AUTO_INC), {
                         'count': 1, 'key': '2-key'})

        # Post_a_record_with_auto_incremented_key_only
        self.assertEqual(rs.post("person", "", record, _ADD_AUTO_INC), {
            "key": "3",
            "count": 1,
        })

        # Post_a_record_with_empty_collection
        with self.assertRaises(ValueError):
            rs.post("", "bad", record)

        # Post_a_record_with_collection_name_that_contains_illegal_chars
        with self.assertRaises(ValueError):
            rs.post("\x00./.\x00", "bad", record)

        # Post_a_record_with_GUID_added_to_key
        self.assertEqual(rs.post("person", "key-value", record, _ADD_AUTO_INC), {
            "key": "4-key-value",
            "count": 1,
        })

        # Post_a_record_with_GUID_key_only
        res = rs.post("person", "", record, _ADD_GUID)
        res = json.dumps(res)
        pattern = r'"key": "([^"]+)", "count": 1'
        self.assertRegex(res, pattern)

        # Post_invalid_collection:
        record["id"] += 1
        with self.assertRaises(ValueError):
            rs.post('person?<|>*":&~\x0a',
                    f"{record['id']}-{record['name']}", record)

        # Post_invalid_key
        record["id"] += 2

        if os.name == "nt":
            self.assertEqual(rs.post("person", f"x?<|>*\":\x0a{record['id']}-{record['name']}", record), {
                "key": "x22758-Adam Smith",
                "count": 1,
            })
        else:
            preffix = """x?<|>*\":&~\x0a"""
            self.assertEqual(
                rs.post(
                    "person", f"{preffix}{record['id']}-{record['name']}", record),
                {'key': 'x?<|>*":&~\n22759-Adam Smith', 'count': 1}
            )

        # get_with_exact_key
        self.assertEqual(rs.get(
            "person", f"22756-{record['name']}"), {'count': 1, 'key': ['22756-Adam Smith'], 'result': [{'id': 22756, 'name': 'Adam Smith', 'title': 'developer', 'email': 'adam@smith.com', 'phone': '+95 555 12345', 'zip': 'DK4321', 'country': 'Distan', 'address': 'Elm tree road 555', 'test': 27}]})

        # get_exact_key_no_hit
        self.assertEqual(rs.get("person", f"{record['id']}-{record['name']}X"), {
            "count": 0,
        })

        # get_wildcard_in_key_with_no_hit
        # print("-->", rs.get("person", f"*-{record['name']}"))
        self.assertEqual(rs.get("person", f"*-{record['name']}"), {'count': 2, 'key': ['22756-Adam Smith', 'x?<|>*":&~\n22759-Adam Smith'], 'result': [{'id': 22756, 'name': 'Adam Smith', 'title': 'developer', 'email': 'adam@smith.com', 'phone': '+95 555 12345', 'zip': 'DK4321',
                         'country': 'Distan', 'address': 'Elm tree road 555', 'test': 27}, {'id': 22759, 'name': 'Adam Smith', 'title': 'developer', 'email': 'adam@smith.com', 'phone': '+95 555 12345', 'zip': 'DK4321', 'country': 'Distan', 'address': 'Elm tree road 555', 'test': 27}]})

        # get_a_exact_key_no_hit
        self.assertEqual(rs.get("person", f"{record['id']}-{record['name']}X"), {
            "count": 0,
        })

        # get_wildcard_in_key_with_no_hit
        self.assertEqual(rs.get("person", f"*-{record['name']}X"), {
            "count": 0,
        })

        # get_a_list
        res = rs.get("person", "*")
        self.assertEqual(True if res["count"] == 7 else False, True)

        # get_a_list_of_collections_and_sequences
        self.assertEqual(rs.get(), {'count': 0})

        # get_a_list_of_collections_and_sequences_with_wildcard
        print("--->", rs.get("", "*_seq"))
        self.assertEqual(rs.get("", "*_seq"), {
            "count": 2,
        })


if __name__ == '__main__':
    unittest.main()
