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


print("1 - UUID ok")
out = rs.post("56685a22-3273-4fda-a9b6-6f5e9f0cd68a",
              "56685a22-3273-4fda-a9b6-6f5e9f0cd68a", dataInput, Rocketstore._ADD_AUTO_INC)

print("2 - UUID + _ ok")
out = rs.post("54e2e7228e9e44ec9e17e7848759e867",
              "ses_784dac38ee0c4f709bddc0deb0b421bd", dataInput, Rocketstore._ADD_AUTO_INC)


print("3 - valid")
out = rs.post("eval'56685a22-3273-4fda-a9b6-6f5e9f0cd68a'",
              "56685a22-3273-4fda-a9b6-6f5e9f0cd68a", dataInput, Rocketstore._ADD_AUTO_INC)

print("4 - UUID ok")
out = rs.post("ses-54e2e7228e9e44ec9e17e7848759e867",
              "ses_784dac38ee0c4f709bddc0deb0b421bd", dataInput, Rocketstore._ADD_AUTO_INC)

print("5 - valid")
out = rs.post("var await",
              "ses_784dac38ee0c4f709bddc0deb0b421bd", dataInput, Rocketstore._ADD_AUTO_INC)

print("6 - invalid")
out = rs.post("⚠️",
              "🙂", dataInput, Rocketstore._ADD_AUTO_INC)

print("7 - invalid")
out = rs.post("�]|[��-��-��-�][�-�]|�[�-�]",
              "stetsetᜠse", dataInput, Rocketstore._ADD_AUTO_INC)
