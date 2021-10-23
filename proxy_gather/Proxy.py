import random
import re
from itertools import cycle
from time import sleep

import psutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

from google_advanced_search.search.google_search import *
from proxy_checker.checkProxy import check_proxies

__version__ = "0.0.1"

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
config_path = op.join(THIS_FOLDER, "..", "static", "config.json")
with open(config_path) as config_file:
    config = json.load(config_file)

CONFIG_PATH = config["proxy_gather"]
CONFIG_PATH_FREE_PROXY_CZ = config["proxy_gather"]["web_sites"][0]
CONFIG_PATH_SPYS_ONE = config["proxy_gather"]["web_sites"][1]
proxy_pool = None


def resourcesUsage():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    print(f"CPU: {cpu}%\nRAM: {ram}%")


def processResourcesUsage():
    thisProcess = psutil.Process(os.getpid())
    ram = thisProcess.memory_percent()
    print(f"{thisProcess.memory_full_info().rss / (1024 * 1024)} MB\nPercent Memory: {ram}%")


def get_new_chrome_session():
    options = Options()
    # headless mode without gui
    if CONFIG_PATH["web_driver"]["headless"]:
        options.add_argument('--headless')
    try:
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    except:
        print("Connection Error, check your internet access")
        sys.exit()

    return driver


def get_http_proxy_free_proxy_cz():
    free_proxy_cz_url = CONFIG_PATH_FREE_PROXY_CZ["url"]

    regex = CONFIG_PATH_FREE_PROXY_CZ["regex"]
    driver = get_new_chrome_session()
    driver.get(free_proxy_cz_url)
    try:
        driver.get(free_proxy_cz_url)
    except:
        print("Connection Error, check your internet access")
        sys.exit()
    page_source = driver.page_source
    driver.quit()
    found = re.findall(regex, page_source)
    proxies_found = set([ip[0] + ":" + ip[1] for ip in found])
    print(f"In the website {free_proxy_cz_url} I found {len(proxies_found)} proxies")
    return proxies_found


# todo get_http_generic_with_regex(regex: str, web_site: str)
# do a google search 20 results for each page search ip search next page href realtive to the website

# todo generic scraper input literals function

# todo if yes literals passed by endpoints


def get_http_proxy_spys_one():
    spys_one_url = CONFIG_PATH_SPYS_ONE["url"]
    regex = CONFIG_PATH_SPYS_ONE["regex"]
    driver = get_new_chrome_session()
    try:
        driver.get(spys_one_url)
    except:
        print("Connection Error, check your internet access")
        sys.exit()
    select = Select(driver.find_element_by_id(CONFIG_PATH_SPYS_ONE["config"]["element1"]))

    select.select_by_visible_text(CONFIG_PATH_SPYS_ONE["config"]["element2"])
    sleep(5)
    page_source = driver.page_source
    driver.quit()
    found = re.findall(regex, page_source)
    # print("found:", found)
    proxies_found = set([ip[0] + ":" + ip[1] for ip in found])
    print(f"In the website {spys_one_url} I found {len(proxies_found)} proxies")
    return proxies_found


def google_it():
    query_type = QueryType.ALL_THESE_WORDS_PARAMETER
    num_results = config["google_search"]["num_results"]
    q = config["google_search"]["query"]
    query = Query(q, query_type)
    last_update = LastUpdate.PAST24Hours
    results = search(query=query, last_update=last_update, num_results=num_results)

    for result in results:
        yield getattr(result, "url")


def use_generic_regex(url: str):
    regex = config["proxy_gather"]["generic_regex"]
    driver = get_new_chrome_session()
    try:
        driver.get(url)
    except:
        print("Connection Error, check your internet access")
        sys.exit()
    sleep(3)
    page_source = driver.page_source
    driver.quit()
    found = re.findall(regex, page_source)
    # print("found:", found)
    proxies_found = set([ip[0] + ":" + ip[1] for ip in found])
    print(f"In the website {url} I found {len(proxies_found)} proxies:\n{proxies_found}")
    return proxies_found


def get_proxy_pool():
    path_good_proxies = op.join(THIS_FOLDER, "..", "proxy resources", "good_proxy.txt")
    # todo check if it is empty
    with open(path_good_proxies, "r") as f:
        proxies = f.read().splitlines()
        print(f"Proxies Pool:\n{proxies}")
    return cycle(proxies)


def routine():
    global proxy_pool
    path_save_proxies_after_checking = op.join(THIS_FOLDER, "..", "proxy resources", "good_proxy.txt")
    http_proxies1 = set()
    # http_proxies1 = get_http_proxy_free_proxy_cz()
    http_proxies2 = get_http_proxy_spys_one()
    http_proxies = set.union(http_proxies1, http_proxies2)
    print(f"I found {len(http_proxies)} proxies: {http_proxies}")
    print("I'm checking them")
    if len(check_proxies(http_proxies)) == 0:
        raise Exception("There are not good proxies")
    proxy_pool = get_proxy_pool()


def on_startup():
    global proxy_pool
    path_good_proxies = op.join(THIS_FOLDER, "..", "proxy resources", "good_proxy.txt")
    with open(path_good_proxies, "r") as f:
        proxies = f.read().splitlines()
    if len(proxies) == 0:
        routine()
    else:
        good_proxies = check_proxies(proxies)
        if len(good_proxies) == 0:
            routine()
        else:
            with open(path_good_proxies, "w") as f:
                f.writelines(good_proxies)
            proxy_pool = get_proxy_pool()


def get_a_good_http_proxy():
    path = op.join(THIS_FOLDER, "../proxy resources", "good_proxy.txt")
    proxy = []
    with open(path, "r") as f:
        proxy = [a.replace("\n", "") for a in f.readlines()]
        print(proxy)
    if len(proxy) == 0:
        routine()
        return get_a_good_http_proxy()
    return random.choice(proxy)


ports_most_used = [81, 82, 83, 84, 85, 86, 88, 1337, 3124, 3127, 3129, 6515, 6588, 6666, 6675, 8000, 8001, 8008, 8081,
                   8082, 8085, 8088, 8090, 8123, 8800, 8888, 8909, 9000, 9415, 36081, 54321, 60099]
ports_most_used = set(ports_most_used)


def get_all_proxies_ip(source_page: str):
    pass


def get_all_proxies_port(source_page: str):
    pass


def get_all_proxies_by_ips_and_ports(proxy: str, ports: set) -> str:
    for port in ports:
        try_proxy = proxy + ":" + str(port)
        print(f"I'm try this combination {try_proxy}")
        tmp_list = []
        tmp_list.append(try_proxy)
        tmp = check_proxies(tmp_list)
        if tmp:
            return tmp[0]
            print("Good")
        else:
            print("BAD")
    return None
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_proxies_new_method():
    ip_regex = config["proxy_gather"]["ip_regex"]
    urls = list(google_it())
    print(urls)
    good_combinations = set()
    global ports_most_used
    for url in urls:
        driver = get_new_chrome_session()
        try:
            driver.get(url)
        except:
            print("Connection Error, check your internet access")
            sys.exit()
        sleep(2)
        page_source = driver.page_source
        driver.quit()
        ips_found = re.findall(ip_regex, page_source)
        print("found:", ips_found)

        processes = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            for ip_found in ips_found:
                processes.append(executor.submit(get_all_proxies_by_ips_and_ports, ip_found, ports_most_used))
        for task in as_completed(processes):
            if task.result() != None:
                good_combinations.add(task.result())





    print(f"All good proxies:\n{good_combinations}")
    return good_combinations


if __name__ == '__main__':
    get_proxies_new_method()

    # on_startup()

    # routine()

    # urls = list(google_it())
    # print(urls)
    # proxies = set()
    # for url in urls:
    #     proxies = set.union(use_generic_regex(url), proxies)
    # print(proxies)

    # proxies=set()
    # p1 = get_http_proxy_spys_one()
    # p2= get_http_proxy_free_proxy_cz()
    # proxies=set.union(p1, p2)
    # print(proxies)

    # http_proxies=get_http_proxy_spys_one()
    # p = [pp + "\n" for pp in http_proxies]
    # path=op.join("proxy resources", "http_proxy_2.txt")
    # with open(path, "w") as f:
    #     f.writelines(p)
    # checkProxies(path)

    # httpProxies = getHppProxy()
    #
    # print(f"Proxies got:\n{httpProxies}")
    # print("I'm saving it in a file")
    # p = [pp + "\n" for pp in httpProxies]
    # f = open(r"proxy resources/http_proxy.txt", "w+")
    #
    # f.writelines(p)
    # f.close()
    # print("I'm checking them")
    # p = "proxy resources/http_proxy.txt"
    # checkProxies(p)
