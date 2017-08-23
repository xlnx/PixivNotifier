import json

src = '{"main": {"key":1}}'

t = json.loads(src)
t['err'] = 1
print t