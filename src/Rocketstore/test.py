"""
█▀ █▄█ █▀▀ █░█ █▀▀ █░█
▄█ ░█░ █▄▄ █▀█ ██▄ ▀▄▀

Author: <Anton Sychev> (anton at sychev dot xyz) 
test.py (c) 2023 
Created:  2023-12-01 01:01:52 
Desc: Test file of funcionality
Docs: documentation
"""

import os
import unittest
import shutil
import tempfile
import json
import re
from unittest.mock import MagicMock, patch
import Rocketstore


class TestRocketstore(unittest.TestCase):
    def setUp(self):
        # Crear un directorio temporal para las pruebas
        self.temp_dir = "test/webapp"
        os.makedirs(self.temp_dir, exist_ok=True)

    def tearDown(self):
        # Eliminar el directorio temporal después de las pruebas
        shutil.rmtree(self.temp_dir)

    def test_bad_data_format(self):
        with self.assertRaises(Exception) as context:
            Rocketstore({"data_storage_area": "./", "data_format": "a"})
        self.assertFalse(
            "Unknown data format: 'a'" in str(context.exception))

    def test_set_options_unwritable_dir(self):
        with self.assertRaises(Exception) as context:
            Rocketstore({"data_storage_area": "/rsdb/sdgdf/"})
        self.assertFalse(
            "Unable to create data storage directory '/rsdb/sdgdf': " in str(context.exception))

    '''
    def test_post_and_get(self):
        rs = Rocketstore({"data_storage_area": self.temp_dir})

        # Prueba del método post
        record = {
            "id": "22756",
            "name": "Adam Smith",
            "title": "developer",
            "email": "adam@smith.com",
            "phone": "+95 555 12345",
            "zip": "DK4321",
            "country": "Distan",
            "address": "Elm tree road 555",
        }
        result = rs.post("person", "22756-Adam Smith", record)
        self.assertEqual(result["key"], "22756-Adam Smith")
        self.assertEqual(result["count"], 1)

        # Prueba del método get
        result = rs.get("person", "22756-Adam Smith")
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["key"], ["22756-Adam Smith"])
        self.assertEqual(result["result"], [record])

    def test_delete(self):
        rs = Rocketstore({"data_storage_area": self.temp_dir})

        # Prueba del método post
        record = {
            "id": "22756",
            "name": "Adam Smith",
            "title": "developer",
            "email": "adam@smith.com",
            "phone": "+95 555 12345",
            "zip": "DK4321",
            "country": "Distan",
            "address": "Elm tree road 555",
        }
        result = rs.post("person", "22756-Adam Smith", record)
        self.assertEqual(result["key"], "22756-Adam Smith")
        self.assertEqual(result["count"], 1)

        # Prueba del método delete
        result = rs.delete("person", "22756-Adam Smith")
        self.assertEqual(result["count"], 1)

        # Prueba del método get después de la eliminación
        result = rs.get("person", "22756-Adam Smith")
        self.assertEqual(result["count"], 0)

    # Otras pruebas adaptadas...
    '''


if __name__ == "__main__":
    unittest.main()
