import requests

proxy="5.135.160.119:3141"
try:
    response = requests.get('http://2253-78-40-163-30.ngrok.io/',
                        proxies={"http": "http://" + proxy}, timeout=15)
except requests.exceptions.RequestException as e:
    print("Error ", e)
