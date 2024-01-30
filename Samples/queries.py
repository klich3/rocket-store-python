"""
█▀ █▄█ █▀▀ █░█ █▀▀ █░█
▄█ ░█░ █▄▄ █▀█ ██▄ ▀▄▀

Author: <Anton Sychev> (anton at sychev dot xyz) 
queries.py (c) 2024 
Created:  2024-01-11 20:49:20 
Desc: queries samples
Docs: documentation
"""


import os
from Rocketstore import Rocketstore

rs = Rocketstore(**{"data_storage_area": os.path.join(os.getcwd(), "rwdb")})

rs.post(
    "bl_54e2e7228e9e44ec9e17e7848759e867",
    "",
    {"content": "global item"},
    Rocketstore._ADD_AUTO_INC,
)
rs.post(
    "bl_54e2e7228e9e44ec9e17e7848759e867",
    "",
    {"content": "global item 2"},
    Rocketstore._ADD_AUTO_INC,
)

rs.post(
    "bl_54e2e7228e9e44ec9e17e7848759e867",
    "ses_784dac38ee0c4f709bddc0deb0b421bd",
    {"content": "user session 1"},
    Rocketstore._ADD_AUTO_INC,
)
rs.post(
    "bl_54e2e7228e9e44ec9e17e7848759e867",
    "ses_784dac38ee0c4f709bddc0deb0b421bd",
    {"content": "user session 2"},
    Rocketstore._ADD_AUTO_INC,
)
rs.post(
    "bl_54e2e7228e9e44ec9e17e7848759e867",
    "ses_784dac38ee0c4f709bddc0deb0b421bd",
    {"content": "user session 3"},
    Rocketstore._ADD_AUTO_INC,
)
rs.post(
    "bl_54e2e7228e9e44ec9e17e7848759e867",
    "ses_784dac38ee0c4f709bddc0deb0b421bd",
    {"content": "user session 4"},
    Rocketstore._ADD_AUTO_INC,
)
rs.post(
    "bl_54e2e7228e9e44ec9e17e7848759e867",
    "ses_784dac38ee0c4f709bddc0deb0b421bd",
    {"content": "user session 5"},
    Rocketstore._ADD_AUTO_INC,
)
rs.post(
    "bl_54e2e7228e9e44ec9e17e7848759e867",
    "ses_784dac38ee0c4f709bddc0deb0b421bd",
    {"content": "user session 6"},
    Rocketstore._ADD_AUTO_INC,
)


rs.get("bl_54e2e7228e9e44ec9e17e7848759e867")
"""
{'count': 7, 'key': ['6-ses_784dac38ee0c4f709bddc0deb0b421bd', '7-ses_784dac38ee0c4f709bddc0deb0b421bd', '1', '5-ses_784dac38ee0c4f709bddc0deb0b421bd', '3-ses_784dac38ee0c4f709bddc0deb0b421bd', '4-ses_784dac38ee0c4f709bddc0deb0b421bd', '2'], 'result': [{'content': 'user session 1'}, {'content': 'user session 1'}, {'content': 'global item'}, {'content': 'user session 1'}, {'content': 'user session 1'}, {'content': 'user session 1'}, {'content': 'global item 2'}]}
"""

rs.get("bl_54e2e7228e9e44ec9e17e7848759e867",
       "*ses_784dac38ee0c4f709bddc0deb0b421bd")
"""
{'count': 5, 'key': ['6-ses_784dac38ee0c4f709bddc0deb0b421bd', '7-ses_784dac38ee0c4f709bddc0deb0b421bd', '5-ses_784dac38ee0c4f709bddc0deb0b421bd', '3-ses_784dac38ee0c4f709bddc0deb0b421bd', '4-ses_784dac38ee0c4f709bddc0deb0b421bd'], 'result': [{'content': 'user session 1'}, {'content': 'user session 1'}, {'content': 'user session 1'}, {'content': 'user session 1'}, {'content': 'user session 1'}]}
"""

rs.get("bl_54e2e7228e9e44ec9e17e7848759e867", "*")
"""
{'count': 7, 'key': ['6-ses_784dac38ee0c4f709bddc0deb0b421bd', '7-ses_784dac38ee0c4f709bddc0deb0b421bd', '1', '5-ses_784dac38ee0c4f709bddc0deb0b421bd', '3-ses_784dac38ee0c4f709bddc0deb0b421bd', '4-ses_784dac38ee0c4f709bddc0deb0b421bd', '2'], 'result': [{'content': 'user session 1'}, {'content': 'user session 1'}, {'content': 'global item'}, {'content': 'user session 1'}, {'content': 'user session 1'}, {'content': 'user session 1'}, {'content': 'global item 2'}]}
"""

rs.get("bl_54e2e7228e9e44ec9e17e7848759e867", "?", Rocketstore._KEYS)
"""
{'count': 2, 'key': ['1', '2']}
"""

rs.get("bl_54e2e7228e9e44ec9e17e7848759e867", "*", Rocketstore._KEYS)
"""
{'count': 7, 'key': ['6-ses_784dac38ee0c4f709bddc0deb0b421bd', '7-ses_784dac38ee0c4f709bddc0deb0b421bd', '1', '5-ses_784dac38ee0c4f709bddc0deb0b421bd', '3-ses_784dac38ee0c4f709bddc0deb0b421bd', '4-ses_784dac38ee0c4f709bddc0deb0b421bd', '2']}
"""

rs.get("bl_54e2e7228e9e44ec9e17e7848759e867", "?", Rocketstore._KEYS)
"""
{'count': 2, 'key': ['1', '2']}
"""
rs.get("bl_54e2e7228e9e44ec9e17e7848759e867", "?")
"""
{'count': 2, 'key': ['1', '2'], 'result': [{'content': 'global item'}, {'content': 'global item 2'}]}
"""
