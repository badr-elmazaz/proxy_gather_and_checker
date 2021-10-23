import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import os.path as op
import json
from fake_useragent import UserAgent


__version__ = "0.0.1"

THIS_FOLDER = op.dirname(op.abspath(__file__))

websites_path=op.join(THIS_FOLDER, "..", "proxy resources", "websites.json")
with open(websites_path) as f:
    web_sites=json.load(f)


def check_this_proxy(proxy, ua):
    try:
        response = requests.get(random.choice(web_sites),
                                headers={'User-Agent': ua.random},
                                proxies={"http": "http://"+proxy, "https": "http://"+proxy}, timeout=10)
        if response.ok:
            print("Good Proxy")
            return proxy
    except requests.exceptions.Timeout:
        print("Timout")


    except requests.exceptions.TooManyRedirects:
        print("Too many redirects")


    except requests.exceptions.RequestException as e:
        print("Generic Error ", e)
    return None




def check_proxies(http_proxies: list[str]):
    #delete empty strings
    if not http_proxies:
        raise Exception("The proxy list is empty")
    ua = UserAgent()
    http_proxies=[p for p in http_proxies if p]
    path_save_checked_proxies=op.join(THIS_FOLDER, "..", "proxy resources", "good_proxies.txt")

    print(http_proxies)
    processes = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        for currentProxy in http_proxies:
            processes.append(executor.submit(check_this_proxy, currentProxy, ua))
    good_proxies = []
    for task in as_completed(processes):
        if task.result() != None:
            good_proxies.append(task.result())
    print(f"There are {len(good_proxies) } good proxies checked:\n{good_proxies}")

    with open(path_save_checked_proxies, "w") as f:
        good_proxies = [pp + "\n" for pp in good_proxies]
        f.writelines(good_proxies)
    return good_proxies


if __name__ == '__main__':
    # checkProxies("../proxy_gather/proxies.txt")
    pass
