from Rocketstore import Rocketstore, _ADD_AUTO_INC

rs = Rocketstore(**{"data_storage_area": "./test"})

print(rs)

dataInput = {
    "content": "hello asfalsdfsalfaslflasl",
    "embeddings": [0.2, 0.31231312, 0.111],
}


out = rs.post("glOtc6EzYQTZEt0J18cU1f4Ycdz1H8WWTDVkBQTp1Gv2BWgb",
              "memories", dataInput)

print(out)


out = rs.post("glOtc6EzYQTZEt0J18cU1f4Ycdz1H8WWTDVkBQTp1Gv2BWgb",
              "memories", dataInput, _ADD_AUTO_INC)

print(out)
