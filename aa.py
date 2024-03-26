import json
aa={"type":"featureC","features":["1","2"]}
bb = json.dumps(aa)
# bb = str(aa)
cc = json.loads(bb)
print(type(bb))
print(cc)