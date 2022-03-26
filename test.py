import requests

print(requests.post("http://192.168.1.64:874/save_answer", json={"1": "1"}).content)