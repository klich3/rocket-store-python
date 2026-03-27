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

from Rocketstore import Rocketstore

rs = Rocketstore(**{
    "data_storage_area": "./tests/ddbb",
    "data_format": Rocketstore._FORMAT_JSON
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


class TestStorage(unittest.TestCase):
    def test_bad_data_format_option(self):
        with self.assertRaises(ValueError):
            rs.options(**{
                "data_storage_area": "./",
                "data_format": "a"
            })

        # set_options_on_main_object
        rs.options(**{
            "data_storage_area": "./",
            "data_format": Rocketstore._FORMAT_NATIVE
        })

        self.assertEqual(rs.data_storage_area, "./")
        self.assertEqual(rs.data_format, Rocketstore._FORMAT_NATIVE)

        # set_options_to_unwritable_directory
        with self.assertRaises(Exception):
            rs.options(**{
                "data_storage_area": "/rsdb/sdgdf",
                "data_format": Rocketstore._FORMAT_NATIVE
            })

        rs.delete()
        print("[62] test preparation")

    def test_records(self):
        rs.options(**{
            "data_storage_area": "./tests/ddbb",
            "data_format": Rocketstore._FORMAT_JSON
        })

        rs.delete()

        # Post_a_record
        self.assertEqual(rs.post("person", f"{record['id']}-{record['name']}", record), {
            "key":  "22756-Adam Smith",
            "count": 1,
        })

        # Create_sequence
        self.assertEqual(rs.sequence("first"), 1)
        self.assertEqual(rs.sequence("first"), 2)

        print("[82] test add in secuence")

        # Reposet a record
        record["test"] = 27

        self.assertEqual(rs.post("person", f"{record['id']}-{record['name']}", record), {
            "key": "22756-Adam Smith",
            "count": 1,
        })

        print("[92] test add person item")

        self.assertEqual(rs.get("person", f"{record['id']}-{record['name']}"), {'count': 1, 'key': ['22756-Adam Smith'], 'result': [{'id': 22756, 'name': 'Adam Smith',
                         'title': 'developer', 'email': 'adam@smith.com', 'phone': '+95 555 12345', 'zip': 'DK4321', 'country': 'Distan', 'address': 'Elm tree road 555', 'test': 27}]})

        print("[97] test get person item")

        # Post_a_record_with_empty_key
        self.assertEqual(rs.post("person", "", record),
                         {'count': 1, 'key': '1'})
        self.assertEqual(rs.post("person", "key", record, Rocketstore._ADD_AUTO_INC), {
                         'count': 1, 'key': '2-key'})

        print("[105] test add secuence items Post_a_record_with_empty_key")

        # Post_a_record_with_auto_incremented_key_only
        self.assertEqual(rs.post("person", "", record, Rocketstore._ADD_AUTO_INC), {
            "key": "3",
            "count": 1,
        })

        print("[113] test Post_a_record_with_auto_incremented_key_only")

        # Post_a_record_with_empty_collection
        with self.assertRaises(ValueError):
            rs.post("", "bad", record)

        print("[118] test Post_a_record_with_empty_collection")

        # Post_a_record_with_collection_name_that_contains_illegal_chars
        with self.assertRaises(ValueError):
            rs.post("\x00./.\x00", "bad", record)

        print(
            "[125] test Post_a_record_with_collection_name_that_contains_illegal_chars")

        # Post_a_record_with_GUID_added_to_key
        self.assertEqual(rs.post("person", "key-value", record, Rocketstore._ADD_AUTO_INC), {
            "key": "4-key-value",
            "count": 1,
        })

        print("[138] test Post_a_record_with_GUID_added_to_key")

        # Post_a_record_with_GUID_key_only
        res = rs.post("person", "", record, Rocketstore._ADD_GUID)
        res = json.dumps(res)
        pattern = r'"key": "([^"]+)", "count": 1'
        self.assertRegex(res, pattern)

        print("[141] test Post_a_record_with_GUID_key_only")

        # Post_invalid_collection:
        record["id"] += 1
        with self.assertRaises(ValueError):
            rs.post('person?<|>*":&~\x0a',
                    f"{record['id']}-{record['name']}", record)

        print("[149] test Post_invalid_collection")

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

        print("[167] test Post_invalid_key")

        # get_with_exact_key
        self.assertEqual(rs.get(
            "person", f"22756-{record['name']}"), {'count': 1, 'key': ['22756-Adam Smith'], 'result': [{'id': 22756, 'name': 'Adam Smith', 'title': 'developer', 'email': 'adam@smith.com', 'phone': '+95 555 12345', 'zip': 'DK4321', 'country': 'Distan', 'address': 'Elm tree road 555', 'test': 27}]})

        print("[173] test get_with_exact_key")

        # get_exact_key_no_hit
        self.assertEqual(rs.get("person", f"{record['id']}-{record['name']}X"), {
            "count": 0,
        })

        print("[180] test get_exact_key_no_hit")

        # get_wildcard_in_key_with_no_hit
        # print("-->", rs.get("person", f"*-{record['name']}"))
        self.assertEqual(rs.get("person", f"*-{record['name']}"), {'count': 2, 'key': ['22756-Adam Smith', 'x?<|>*":&~\n22759-Adam Smith'], 'result': [{'id': 22756, 'name': 'Adam Smith', 'title': 'developer', 'email': 'adam@smith.com', 'phone': '+95 555 12345', 'zip': 'DK4321',
                         'country': 'Distan', 'address': 'Elm tree road 555', 'test': 27}, {'id': 22759, 'name': 'Adam Smith', 'title': 'developer', 'email': 'adam@smith.com', 'phone': '+95 555 12345', 'zip': 'DK4321', 'country': 'Distan', 'address': 'Elm tree road 555', 'test': 27}]})

        print("[188] test get_wildcard_in_key_with_no_hit")

        # get_a_exact_key_no_hit
        self.assertEqual(rs.get("person", f"{record['id']}-{record['name']}X"), {
            "count": 0,
        })

        print("[195] test get_a_exact_key_no_hit")

        # get_wildcard_in_key_with_no_hit
        self.assertEqual(rs.get("person", f"*-{record['name']}X"), {
            "count": 0,
        })

        print("[202] test get_wildcard_in_key_with_no_hit")

        # get_a_list
        res = rs.get("person", "*")
        self.assertEqual(True if res["count"] == 7 else False, True)

        '''
        # BUG
        # get_a_list_of_collections_and_sequences
        self.assertEqual(rs.get(), {'count': 0})

        # get_a_list_of_collections_and_sequences_with_wildcard
        # BUG
        print("--->", rs.get(key="*_seq"))
        self.assertEqual(rs.get(key="*_seq"), {
            "count": 2,
        })
        '''

        # post_collection_as_number
        record["id"] += 1
        with self.assertRaises(ValueError):
            rs.post(33, f"{record['id']}-{record['name']}", record)

        print("[226] test post_collection_as_number")

        # get_collections_as_number
        with self.assertRaises(ValueError):
            rs.get(33)

        print("[232] test get_collections_as_number")

        # order_by_flags
        rs.post("person", "p1", 1)
        rs.post("person", "p4", 4)
        rs.post("person", "p2", 2)
        rs.post("person", "p3", 3)

        print("[240] test order_by_flags")

        order = rs.get("person", "p?", Rocketstore._ORDER)
        # Get order ascending
        self.assertEqual(order["result"], [1, 2, 3, 4])

        print("[246] test Get order ascending")

        # get keys
        self.assertEqual(rs.get("person", "p?", Rocketstore._KEYS), {
                         'count': 4, 'key': ['p1', 'p4', 'p2', 'p3']})

        print("[252] test get keys")

        # Get keys in descending order
        result = rs.get(
            "person", "p?", Rocketstore._ORDER_DESC | Rocketstore._KEYS)
        self.assertEqual(result["key"], ["p4", "p3", "p2", "p1"])

        print("[259] test Get keys in descending order")

        # Get keys in ascending order
        result = rs.get("person", "p?", Rocketstore._ORDER | Rocketstore._KEYS)
        self.assertEqual(result["key"], ["p1", "p2", "p3", "p4"])

        print("[265] keys in ascending order")

        # get record count
        self.assertEqual(rs.get("person", "p?", Rocketstore._COUNT), {
                         "count": 4,
                         })

        print("[265] test get record count")

        # Get manually deleted record where keys != cache
        os.unlink(os.path.join(rs.data_storage_area, "person", "p2"))

        self.assertEqual(rs.get("person", "p?"), {"count": 3, "key": [
                         "p1", "p4", "p3"], "result": [1, 4, 3]})

        print("[280] test get Get manually deleted record where keys != cache")

        # test_get_manually_deleted_record_where_keys_equals_cache
        os.unlink(os.path.join(rs.data_storage_area,
                  "person", "22756-Adam Smith"))

        print("[286] test_get_manually_deleted_record_where_keys_equals_cache")

        res = rs.get("person", "*")
        self.assertEqual(res["count"] == 9, True)

        key = "No Smith"
        rs.delete("person")

        rs.post("person", key, "should be ok")

        # wirte w to file
        w = os.path.join(f"{rs.data_storage_area}/person/{key}")
        with open(w, "w") as f:
            f.write("not a JSON{")
            f.close()

        print("[302] wirte w to file")

        # get_invalid_JSON_in_file
        self.assertEqual(rs.get("person", key), {
            "count": 1,
            "key": [key],
            "result": [""],
        })

        print("[311] get_invalid_JSON_in_file")

        # get_invalid_JSON_in_file
        self.assertEqual(rs.get("person", key), {
            "count": 1,
            "key": [key],
            "result": [""],
        })

        print("[320] get_invalid_JSON_in_file")

        # TODO: test time limits
        # TODO: test Json and XML

        # Delete
        rs.post(collection="delete_fodders1", record=record)
        rs.post(collection="delete_fodders1", record=record)
        rs.post(collection="delete_fodders1", record=record)
        # here have fodder1 = 3
        rs.post(collection="delete_fodders2", record=record)
        # here have fodder2 = 1
        rs.post(collection="delete_fodders3", record=record)
        # here have fodder3 = 1

        print("[335] Delete in batch")

        # Delete record with exact key
        res = rs.delete(collection="delete_fodders1", key=1)
        print("[277] Del record with key res: ", res)
        self.assertEqual(res, {
            "count": 1
        })  # remove only 1 item

        # Delete collection
        res = rs.delete(collection="delete_fodders1")
        print("[284] Del collection (1 folder + 1 seq_file): ", res)
        self.assertEqual(res, {
            "count": 2,
        })

        # Delete nonexistent collection
        print("[291] del nonexistent collection: current folders",
              rs.get("delete_fodders1"))
        self.assertEqual(rs.delete("delete_fodders1"), {
            "count": 0,
        })

        # Delete collection with wildcard
        print("[295] del nonexistent with wildcard")
        self.assertEqual(rs.delete(key="*fodders?"), {
            "count": 2,
        })

        # Delete numeric collection
        with self.assertRaises(ValueError):
            rs.delete("1")

        # Delete sequence
        print("[306] Delete sequence file")
        self.assertEqual(rs.delete("delete_fodders2_seq"), {
            "count": 1,
        })

        print("[313] Delete wildcat sequence file")
        self.assertEqual(rs.delete(key="delete_fodders*"), {
            "count": 1,
        })

        # Delete unsafe ../*
        with self.assertRaises(ValueError):
            rs.delete("delete_fodders2/../*")

        with self.assertRaises(ValueError):
            rs.delete("~/*")

        # Delete database
        self.assertEqual(rs.delete(), {
            "count": 1,
        })


    def test_markdown_format(self):
        """Test Markdown format support"""
        rs.options(**{
            "data_storage_area": "./tests/ddbb_md",
            "data_format": Rocketstore._FORMAT_MD
        })
        
        rs.delete()
        
        # Post a record in markdown format
        record_md = {
            "title": "Test Document",
            "author": "Test Author",
            "tags": ["test", "markdown"],
            "_content": "# Test Content\n\nThis is the body."
        }
        
        result = rs.post("docs", "test-doc", record_md)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["key"], "test-doc.md")
        
        print("[MD-1] test post markdown record")
        
        # Get the record back
        get_result = rs.get("docs", "test-doc")
        self.assertEqual(get_result["count"], 1)
        self.assertEqual(get_result["result"][0]["title"], "Test Document")
        self.assertEqual(get_result["result"][0]["author"], "Test Author")
        
        print("[MD-2] test get markdown record")
        
        # Test auto-detection of YAML frontmatter
        rs.options(**{
            "data_storage_area": "./tests/ddbb_md",
            "data_format": Rocketstore._FORMAT_JSON
        })
        
        # Should still be able to read markdown files
        get_result = rs.get("docs", "test-doc")
        self.assertEqual(get_result["count"], 1)
        
        print("[MD-3] test auto-detect markdown in JSON mode")
        
        # Cleanup
        rs.delete()
        
    def test_markdown_with_guid(self):
        """Test Markdown format with GUID"""
        rs.options(**{
            "data_storage_area": "./tests/ddbb_md_guid",
            "data_format": Rocketstore._FORMAT_MD
        })
        
        rs.delete()
        
        record = {
            "type": "memory",
            "context": "AI conversation",
            "_content": "User asked about Python."
        }
        
        result = rs.post("memories", "", record, Rocketstore._ADD_GUID)
        self.assertEqual(result["count"], 1)
        self.assertTrue(result["key"].endswith(".md"))
        
        print("[MD-4] test markdown with GUID")
        
        # Cleanup
        rs.delete()

    def test_markdown_records(self):
        """Test Markdown format with comprehensive operations like test_records"""
        rs.options(**{
            "data_storage_area": "./tests/ddbb_md_full",
            "data_format": Rocketstore._FORMAT_MD
        })
        
        rs.delete()
        
        record_md = {
            "id": 22756,
            "name": "Adam Smith",
            "title": "developer",
            "email": "adam@smith.com",
            "_content": "# Adam Smith\n\nDeveloper at Example Corp."
        }
        
        # Post_a_record
        self.assertEqual(rs.post("person", f"{record_md['id']}-{record_md['name']}", record_md), {
            "key": "22756-Adam Smith.md",
            "count": 1,
        })
        
        # Create_sequence
        self.assertEqual(rs.sequence("first"), 1)
        self.assertEqual(rs.sequence("first"), 2)
        
        print("[MD-5] test add in sequence")
        
        # Repost a record
        record_md["test"] = 27
        
        self.assertEqual(rs.post("person", f"{record_md['id']}-{record_md['name']}", record_md), {
            "key": "22756-Adam Smith.md",
            "count": 1,
        })
        
        print("[MD-6] test add person item")
        
        # Verify content is preserved
        get_result = rs.get("person", "22756-Adam Smith")
        self.assertEqual(get_result["count"], 1)
        self.assertEqual(get_result["result"][0]["name"], "Adam Smith")
        self.assertEqual(get_result["result"][0]["test"], 27)
        self.assertEqual(get_result["result"][0]["_content"], "# Adam Smith\n\nDeveloper at Example Corp.")
        
        print("[MD-7] test get person item with content")
        
        # Post_a_record_with_empty_key
        self.assertEqual(rs.post("person", "", record_md),
                         {'count': 1, 'key': '1.md'})
        self.assertEqual(rs.post("person", "key", record_md, Rocketstore._ADD_AUTO_INC), {
                         'count': 1, 'key': '2-key.md'})
        
        print("[MD-8] test add sequence items Post_a_record_with_empty_key")
        
        # Post_a_record_with_auto_incremented_key_only
        self.assertEqual(rs.post("person", "", record_md, Rocketstore._ADD_AUTO_INC), {
            "key": "3.md",
            "count": 1,
        })
        
        print("[MD-9] test Post_a_record_with_auto_incremented_key_only")
        
        # Post_a_record_with_empty_collection
        with self.assertRaises(ValueError):
            rs.post("", "bad", record_md)
        
        print("[MD-10] test Post_a_record_with_empty_collection")
        
        # Post_a_record_with_collection_name_that_contains_illegal_chars
        with self.assertRaises(ValueError):
            rs.post("\x00./.\x00", "bad", record_md)
        
        print("[MD-11] test Post_a_record_with_collection_name_that_contains_illegal_chars")
        
        # Post_a_record_with_GUID_added_to_key
        self.assertEqual(rs.post("person", "key-value", record_md, Rocketstore._ADD_AUTO_INC), {
            "key": "4-key-value.md",
            "count": 1,
        })
        
        print("[MD-12] test Post_a_record_with_GUID_added_to_key")
        
        # Post_a_record_with_GUID_key_only
        res = rs.post("person", "", record_md, Rocketstore._ADD_GUID)
        self.assertEqual(res["count"], 1)
        self.assertTrue(res["key"].endswith(".md"))
        # Just verify it has .md extension and some content before it
        self.assertTrue(len(res["key"]) > 3)
        
        print("[MD-13] test Post_a_record_with_GUID_key_only")
        
        # Post_invalid_collection
        record_md["id"] += 1
        with self.assertRaises(ValueError):
            rs.post('person?<|>*":&~\x0a',
                    f"{record_md['id']}-{record_md['name']}", record_md)
        
        print("[MD-14] test Post_invalid_collection")
        
        # Post_invalid_key
        record_md["id"] += 2
        
        if os.name == "nt":
            self.assertEqual(rs.post("person", f"x?<|>*\":\x0a{record_md['id']}-{record_md['name']}", record_md), {
                "key": "x22758-Adam Smith.md",
                "count": 1,
            })
        else:
            preffix = """x?<|>*\":&~\x0a"""
            self.assertEqual(
                rs.post(
                    "person", f"{preffix}{record_md['id']}-{record_md['name']}", record_md),
                {'key': 'x?<|>*":&~\n22759-Adam Smith.md', 'count': 1}
            )
        
        print("[MD-15] test Post_invalid_key")
        
        # get_with_exact_key
        get_result = rs.get("person", "22756-Adam Smith")
        self.assertEqual(get_result["count"], 1)
        self.assertEqual(get_result["result"][0]["name"], "Adam Smith")
        
        print("[MD-16] test get_with_exact_key")
        
        # get_exact_key_no_hit
        self.assertEqual(rs.get("person", f"{record_md['id']}-{record_md['name']}X"), {
            "count": 0,
        })
        
        print("[MD-17] test get_exact_key_no_hit")
        
        # get_wildcard_in_key
        get_result = rs.get("person", "*-Adam Smith")
        self.assertEqual(get_result["count"], 2)
        
        print("[MD-18] test get_wildcard_in_key")
        
        # get_a_list
        res = rs.get("person", "*")
        self.assertEqual(True if res["count"] == 7 else False, True)
        
        # post_collection_as_number
        record_md["id"] += 1
        with self.assertRaises(ValueError):
            rs.post(33, f"{record_md['id']}-{record_md['name']}", record_md)
        
        print("[MD-19] test post_collection_as_number")
        
        # get_collections_as_number
        with self.assertRaises(ValueError):
            rs.get(33)
        
        print("[MD-20] test get_collections_as_number")
        
        # order_by_flags
        rs.post("person", "p1", {"order": 1, "_content": "Content 1"})
        rs.post("person", "p4", {"order": 4, "_content": "Content 4"})
        rs.post("person", "p2", {"order": 2, "_content": "Content 2"})
        rs.post("person", "p3", {"order": 3, "_content": "Content 3"})
        
        print("[MD-21] test order_by_flags")
        
        order = rs.get("person", "p?", Rocketstore._ORDER)
        # Get order ascending
        self.assertEqual(order["result"], [{"order": 1, "_content": "Content 1"}, {"order": 2, "_content": "Content 2"}, {"order": 3, "_content": "Content 3"}, {"order": 4, "_content": "Content 4"}])
        
        print("[MD-22] test Get order ascending")
        
        # get keys
        self.assertEqual(rs.get("person", "p?", Rocketstore._KEYS), {
                         'count': 4, 'key': ['p1.md', 'p4.md', 'p2.md', 'p3.md']})
        
        print("[MD-23] test get keys")
        
        # Get keys in descending order
        result = rs.get(
            "person", "p?", Rocketstore._ORDER_DESC | Rocketstore._KEYS)
        self.assertEqual(result["key"], ["p4.md", "p3.md", "p2.md", "p1.md"])
        
        print("[MD-24] test Get keys in descending order")
        
        # Get keys in ascending order
        result = rs.get("person", "p?", Rocketstore._ORDER | Rocketstore._KEYS)
        self.assertEqual(result["key"], ["p1.md", "p2.md", "p3.md", "p4.md"])
        
        print("[MD-25] keys in ascending order")
        
        # get record count
        self.assertEqual(rs.get("person", "p?", Rocketstore._COUNT), {
                         "count": 4,
                         })
        
        print("[MD-26] test get record count")
        
        # Get manually deleted record where keys != cache
        os.unlink(os.path.join(rs.data_storage_area, "person", "p2.md"))
        
        self.assertEqual(rs.get("person", "p?"), {"count": 3, "key": [
                         "p1.md", "p4.md", "p3.md"], "result": [{"order": 1, "_content": "Content 1"}, {"order": 4, "_content": "Content 4"}, {"order": 3, "_content": "Content 3"}]})
        
        print("[MD-27] test get Get manually deleted record where keys != cache")
        
        # test_get_manually_deleted_record_where_keys_equals_cache
        os.unlink(os.path.join(rs.data_storage_area,
                  "person", "22756-Adam Smith.md"))
        
        print("[MD-28] test_get_manually_deleted_record_where_keys_equals_cache")
        
        res = rs.get("person", "*")
        self.assertEqual(res["count"] == 9, True)
        
        # Test invalid markdown file
        key = "No Smith"
        rs.delete("person")
        
        rs.post("person", key, {"data": "should be ok", "_content": "Test content"})
        
        # write invalid content to file
        w = os.path.join(f"{rs.data_storage_area}/person/{key}.md")
        with open(w, "w") as f:
            f.write("---\ninvalid: yaml: content:\n\nnot valid markdown")
            f.close()
        
        print("[MD-29] write invalid markdown to file")
        
        # get_invalid_markdown_in_file - markdown parser returns _raw for invalid files
        result = rs.get("person", key)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["key"], [f"{key}.md"])
        # Invalid markdown returns the raw content
        self.assertIn("_raw", result["result"][0])
        
        print("[MD-30] get_invalid_markdown_in_file")
        
        # Delete
        rs.post(collection="delete_fodders1", record=record_md)
        rs.post(collection="delete_fodders1", record=record_md)
        rs.post(collection="delete_fodders1", record=record_md)
        rs.post(collection="delete_fodders2", record=record_md)
        rs.post(collection="delete_fodders3", record=record_md)
        
        print("[MD-31] Delete in batch")
        
        # Delete record with exact key
        res = rs.delete(collection="delete_fodders1", key=1)
        self.assertEqual(res, {
            "count": 1
        })
        
        # Delete collection
        res = rs.delete(collection="delete_fodders1")
        self.assertEqual(res, {
            "count": 2,
        })
        
        # Delete nonexistent collection
        self.assertEqual(rs.delete("delete_fodders1"), {
            "count": 0,
        })
        
        # Delete collection with wildcard
        self.assertEqual(rs.delete(key="*fodders?"), {
            "count": 2,
        })
        
        # Delete numeric collection
        with self.assertRaises(ValueError):
            rs.delete("1")
        
        # Delete sequence
        self.assertEqual(rs.delete("delete_fodders2_seq"), {
            "count": 1,
        })
        
        self.assertEqual(rs.delete(key="delete_fodders*"), {
            "count": 1,
        })
        
        # Delete unsafe ../*
        with self.assertRaises(ValueError):
            rs.delete("delete_fodders2/../*")
        
        with self.assertRaises(ValueError):
            rs.delete("~/*")
        
        # Delete database
        self.assertEqual(rs.delete(), {
            "count": 1,
        })
        
        print("[MD-32] All markdown records tests completed")


if __name__ == '__main__':
    unittest.main()
