from Rocketstore import Rocketstore

rs = Rocketstore(**{"data_storage_area": "./test"})

print(rs)
print("test Constants:", rs._ADD_AUTO_INC)
print("test Constants: ", Rocketstore._ADD_AUTO_INC)

dataInput = {
    "content": "hello asfalsdfsalfaslflasl",
    "embeddings": [0.2, 0.31231312, 0.111],
}


out = rs.post("glOtc6EzYQTZEt0J18cU1f4Ycdz1H8WWTDVkBQTp1Gv2BWgb",
              "memories", dataInput)

print(out)


out = rs.post("glOtc6EzYQTZEt0J18cU1f4Ycdz1H8WWTDVkBQTp1Gv2BWgb",
              "memories", dataInput, rs._ADD_AUTO_INC)

print(out)

out = rs.post("glOtc6EzYQTZEt0J18cU1f4Ycdz1H8WWTDVkBQTp1Gv2BWgb",
              "memories", dataInput, Rocketstore._ADD_AUTO_INC)

print(out)
