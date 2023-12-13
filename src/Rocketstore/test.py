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

        currentFolder = os.getcwd()

        self.assertEqual(rs.data_storage_area, currentFolder)
        self.assertEqual(rs.data_format, _FORMAT_NATIVE)

    def test_set_options_to_unwritable_directory(self):
        with self.assertRaises(Exception):
            rs.options(**{
                "data_storage_area": "/rsdb/sdgdf",
                "data_format": _FORMAT_NATIVE
            })

    def test_Post_a_record(self):
        self.assertEqual(rs.post("person", f"{record['id']}-{record['name']}", record), {
            "key":  "22756-Adam Smith",
            "count": 1,
        })

    def test_Create_sequence(self):
        self.assertEqual(rs.sequence("first"), 1)
        self.assertEqual(rs.sequence("first"), 2)

    def test_Reposet_a_record(self):
        record["test"] = 27
        self.assertEqual(rs.post("person", f"{record['id']}-{record['name']}", record), {
            "key": "22756-Adam Smith",
            "count": 1,
        })

    def test_Count_record(self):
        print(rs.get("person", f"{record['id']}-{record['name']}"))

        self.assertEqual(rs.get("person", f"{record['id']}-{record['name']}"), {
            "count": 1,
            "key": ["22756-Adam Smith"],
            "result": {"id": 22756, "name": "Adam Smith", "title": "developer", "email": "adam@smith.com", "phone": "+95 555 12345", "zip": "DK4321", "country": "Distan", "address": "Elm tree road 555", "test": 27}
        })

    def test_Post_a_record_with_empty_key(self):
        self.assertEqual(rs.post("person", "", record), {
            "key": "1-key",
            "count": 1,
        })

    def test_Post_a_record_with_auto_incremented_value_added_to_key(self):
        self.assertEqual(rs.post("person", "key", record, _ADD_AUTO_INC), {
            "key": "2-key",
            "count": 1,
        })

    def test_Post_a_record_with_auto_incremented_key_only(self):
        self.assertEqual(rs.post("person", "", record, _ADD_AUTO_INC), {
            "key": "3",
            "count": 1,
        })

    def test_Post_a_record_with_empty_collection(self):
        with self.assertRaises(ValueError):
            rs.post("", "bad", record)

    def test_Post_a_record_with_collection_name_that_contains_illegal_chars(self):
        with self.assertRaises(ValueError):
            rs.post("\x00./.\x00", "bad", record)

    def test_Post_a_record_with_GUID_added_to_key(self):
        self.assertEqual(rs.post("person", "key-value", record, _ADD_AUTO_INC), {
            "key": "4-key-value",
            "count": 1,
        })

    def test_Post_a_record_with_GUID_key_only(self):
        self.assertEqual(rs.post("person", "", record, _ADD_GUID), {
            "count": 1,
        })

    def test_Post_invalid_collection(self):
        record["id"] += 1
        with self.assertRaises(ValueError):
            rs.post("person?<|>*\":&~\x0a",
                    f"{record['id']}-{record['name']}", record)

    def test_Post_invalid_key(self):
        record["id"] += 2
        self.assertEqual(rs.post("person", f"x?<|>*\":&~\x0a{record['id']}-{record['name']}", record), {
            "key": "x<|>\":&\n22758-Adam Smith",
            "count": 1,
        })

    def test_get_with_exact_key(self):
        self.assertEqual(rs.get("person", f"22756-{record['name']}"), {
            "count": 1,
            "key": ["22756-Adam Smith"],
        })

    def test_get_exact_key_no_hit(self):
        self.assertEqual(rs.get("person", f"{record['id']}-{record['name']}X"), {
            "count": 0,
        })

    def test_get_wildcard_in_key_with_no_hit(self):
        self.assertEqual(rs.get("person", f"*-{record['name']}X"), {
            "count": 1,
            "key": ["22756-Adam Smith"],
        })

    def test_get_a_exact_key_no_hit(self):
        self.assertEqual(rs.get("person", f"{record['id']}-{record['name']}X"), {
            "count": 0,
        })

    def test_get_wildcard_in_key_with_no_hit(self):
        self.assertEqual(rs.get("person", f"*-{record['name']}X"), {
            "count": 0,
        })

    def test_get_a_list(self):
        self.assertEqual(rs.get("person", "*"), {
            "count": 7,
        })

    def test_get_a_list_of_collections_and_sequences(self):
        self.assertEqual(rs.get([]), {
            "count": 4,
        })

    def test_get_a_list_of_collections_and_sequences_with_wildcard(self):
        self.assertEqual(rs.get(None, "*_seq"), {
            "count": 2,
        })

    def test_post_collection_as_number(self):
        record["id"] += 1
        with self.assertRaises(ValueError):
            rs.post(33, f"{record['id']}-{record['name']}", record)

    def test_get_collections_as_number(self):
        with self.assertRaises(ValueError):
            rs.get(33)

    '''
    def test_order_by_flags(self):
        rs.post("person", "p1", 1)
        rs.post("person", "p4", 4)
        rs.post("person", "p2", 2)
        rs.post("person", "p3", 3)
    '''




    '''

	// compare order of array values
	function test_order(arr1, arr2) {
		for (let i in arr1) if (arr1[i] != arr2[i]) return false;
		return true;
	}

	result = await rs.get("person", "p?", store._ORDER);

	await tst("Get order ascending", test_order, [result.record, [1, 2, 3, 4]], true);

	await tst("Get keys", rs.get, ["person", "p?", store._KEYS], { count: 4 });

	result = await rs.get("person", "p?", store._ORDER_DESC | store._KEYS);
	await tst("Get keys in descending order", test_order, [result.key, ["p4", "p3", "p2", "p1"]], true);

	result = await rs.get("person", "p?", store._ORDER | store._KEYS);
	await tst("Get keys in ascending order", test_order, [result.key, ["p1", "p2", "p3", "p4"]], true);

	await tst("Get record count", rs.get, ["person", "p?", store._COUNT], { count: 4 });

	await fs.rmSync(`${rs.data_storage_area}/person/p2`, { force: true, recursive: true });
	await tst("Get manually deleted record where keys != cache", rs.get, ["person", "p?"], {
		count: 3,
		key: ["p1", "p4", "p3"],
		result: [1, 4, 3],
	});

    '''

    def test_get_manually_deleted_record_where_keys_equals_cache(self):
        os.remove(f"{rs.data_storage_area}/person/22756-Adam Smith")
        self.assertEqual(rs.get("person", "*"), {
            "count": 9,
        })

    
    key = "No Smith"

    rs.delete("person")
    rs.post("person", key, "should be ok")

    #wirte w to file
    w = os.path.join(f"{rs.data_storage_area}/person/{key}") 
    with  open(w, "w") as f:
        f.write("not a JSON")
        f.close()

    def test_get_invalid_JSON_in_file(self):
        self.assertEqual(rs.get("person", self.key), {
            "count": 1,
            "key": [self.key],
            "result": [""],
        })

	await tst("Get invalid JSON in file", rs.get, ["person", key], { count: 1, key: ["No Smith"], result: [""] });

    '''
	// test time limits
	// test Json and XML

	// Delete
	await rs.post("delete_fodders1", "", record);
	await rs.post("delete_fodders1", "", record);
	await rs.post("delete_fodders1", "", record);
	//here have fodder1 = 3
	await rs.post("delete_fodders2", "", record);
	//here have fodder2 = 1
	await rs.post("delete_fodders3", "", record);
	//here have fodder3 = 1

	await tst("Delete record with exact key", rs.delete, ["delete_fodders1", 1], { count: 1 }); //remove only 1 item
	await tst("Delete collection", rs.delete, ["delete_fodders1"], { count: 2 });

	await tst("Delete nonexistent collection", rs.delete, ["delete_fodders1"], { count: 0 });
	await tst("Delete collection with wildcard", rs.delete, ["", "*fodders?"], { count: 2 });

	await tst(
		"Delete numeric collection",
		rs.delete,
		["1"],
		"Collection name contains illegal characters (For a javascript identifier)",
	);

	await tst("Delete sequence", rs.delete, ["", "delete_fodders2_seq"], { count: 1 });
	await tst("Delete sequence", rs.delete, ["", "delete_fodders*"], { count: 1 });

	await tst(
		"Delete unsafe ../*",
		rs.delete,
		["delete_fodders2/../*"],
		"Collection name contains illegal characters (For a javascript identifier)",
	);

	await tst(
		"Delete unsafe ~/*",
		rs.delete,
		["~/*"],
		"Collection name contains illegal characters (For a javascript identifier)",
	);

	// Test asynchronous object integrityGet a list of collections and sequences
	let i;
	let obj = {};
	let promises = [];

	for (i = 0; i < 4; i++) {
		obj.id = i;
		promises.push(rs.post("async", i, obj));
	}

	await Promise.all(promises);

	await tst("Post test asynchronous integrity of records", rs.get, ["async", "", store._ORDER_ASC], {
		count: 4,
		key: ["0", "1", "2", "3"],
		result: [{ id: 0 }, { id: 1 }, { id: 2 }, { id: 3 }],
	});

	await tst("Delete database", rs.delete, [], { count: 1 });
    '''


if __name__ == '__main__':
    unittest.main()
