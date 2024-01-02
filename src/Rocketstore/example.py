"""
█▀ █▄█ █▀▀ █░█ █▀▀ █░█
▄█ ░█░ █▄▄ █▀█ ██▄ ▀▄▀

Author: <Anton Sychev> (anton at sychev dot xyz) 
sample.py (c) 2023 
Created:  2023-12-01 01:02:01 
Desc: sample create instance of RocketStore
Docs: documentation
"""

from .Rocketstore import Rocketstore, _FORMAT_JSON, _FORMAT_NATIVE, _FORMAT_XML, _ADD_AUTO_INC, _ORDER_DESC

rs = Rocketstore(**{"data_storage_area": "./webapp",
                    "data_format": _FORMAT_JSON})

rs.post("cars", "Mercedes_Benz_GT_R", {"owner": "Lisa Simpson"})

print("GET: ", rs.get("cars", ""), "\n-----\n")
# GET:  {'count': 1, 'key': ['Mercedes_Benz_GT_R'], 'result': [{'owner': 'Lisa Simpson'}]}

rs.post("cars", "BMW_740li", {"owner": "Greg Onslow"}, _ADD_AUTO_INC)
rs.post("cars", "BMW_740li", {"owner": "Sam Wise"}, _ADD_AUTO_INC)
rs.post("cars", "BMW_740li", {"owner": "Bill Bo"}, _ADD_AUTO_INC)
# tienen que haber un BMW_740li

print("GET ALL CARS: ", rs.get("cars", "*"), "\n-----\n")
'''
Get all records:
 {
  count: 2,
  key: [ 'Mercedes_Benz_GT_R', 'BMW_740li' ],
  result: [ { owner: 'Lisa Simpson' }, { owner: 'Bill Bo' } ]
}
'''


dataset = {
    "Gregs_BMW_740li": {"owner": "Greg Onslow"},
    "Lisas_Mercedes_Benz_GT_R": {"owner": "Lisa Simpson"},
    "Bills_BMW_740li": {"owner": "Bill Bo"},
}

for i in dataset:
    rs.post("cars", i, dataset[i])

print("GET BMW's: ", rs.get("cars", "*BMW*"), "\n-----\n")
'''
Get BMW's:
 {
  count: 3,
  key: [ 'BMW_740li', 'Gregs_BMW_740li', 'Bills_BMW_740li' ],
  result: [
    { owner: 'Bill Bo' },
    { owner: 'Greg Onslow' },
    { owner: 'Bill Bo' }
  ]
}
'''


print("Get list ordered by alphabetically descending keys: ",
      rs.get("cars", "", _ORDER_DESC), "\n-----\n")
'''
Get list ordered by alphabetically descending keys:
 {
  count: 5,
  key: [
    'Mercedes_Benz_GT_R',
    'BMW_740li',
    'Gregs_BMW_740li',
    'Lisas_Mercedes_Benz_GT_R',
    'Bills_BMW_740li'
  ],
  result: [
    { owner: 'Lisa Simpson' },
    { owner: 'Bill Bo' },
    { owner: 'Greg Onslow' },
    { owner: 'Lisa Simpson' },
    { owner: 'Bill Bo' }
  ]
}
'''

r = rs.delete("cars", "*Mercedes*")
print("Delete all Mercedes's: ", r, "\n-----\n")
''''
Delete all Mercedes's:
 { count: 2 }

'''

print("Return all cars: ", rs.get("cars", "*"), "\n-----\n")
'''
{
  count: 3,
  key: [ 'BMW_740li', 'Gregs_BMW_740li', 'Bills_BMW_740li' ],
  result: [
    { owner: 'Bill Bo' },
    { owner: 'Greg Onslow' },
    { owner: 'Bill Bo' }
  ]
}
'''


print("Delete all records: ", rs.delete(), "\n-----\n")
