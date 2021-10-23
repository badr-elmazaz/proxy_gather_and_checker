# from meinheld import server
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_httpauth import HTTPBasicAuth
import json
import sched, time
from os import path as op
import os




app = Flask(__name__)
auth = HTTPBasicAuth()
api = Api(app, prefix="/api/v1")


THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

config_path=op.join(THIS_FOLDER, "static", "config.json")
with open(config_path) as config_file:
        config=json.load(config_file)


USERS_ALLOWED = config["basic_auth"]


def update_config(c: dict):
    with open('static/config.json', 'w') as config_file:
        json.dump(c, config_file)
        config

@auth.verify_password
def verify_pwd(username, password):
    if not (username, password):
        return False
    return USERS_ALLOWED.get(username) == password


class http_proxy(Resource):
    @auth.login_required
    def get(self):
        # from proxy_gather.Proxy import get_a_good_http_proxy
        # proxy=get_a_good_http_proxy()
        proxy = next(p.proxy_pool)
        return jsonify(proxy)

class get_all_configs(Resource):
    @auth.login_required
    def get(self):

        return jsonify([{"url": k["url"],"regex": k["regex"]} for k in config["proxy_gather"]["web_sites"]])

class get_url_config(Resource):
    @auth.login_required
    def get(self):
        url=request.args.get('url').strip()
        if url[-1]!="/":
            url+="/"
        for k in config["proxy_gather"]["web_sites"]:
            if k["url"]==url:
                return jsonify({"url": k["url"],"regex": k["regex"]})
        return jsonify(None)


class update_config(Resource):
    @auth.login_required
    def post(self):
        configuration=request.get_json()
        for k in config["proxy_gather"]["web_sites"]:
            if k["url"] == config["url"]:
                k["regex"]=configuration["regex"]
                break
        else:
            config["proxy_gather"]["web_sites"].append(configuration)
            update_config(config)

        #todo save the json e reopen it


class delete_config(Resource):
    @auth.login_required
    def delete(self):
        url = request.args.get('url').strip()
        if url[-1] != "/":
            url += "/"

        delete=None
        for i in range(len(config["proxy_gather"]["web_sites"])):
            print(config["proxy_gather"]["web_sites"][i])
            if config["proxy_gather"]["web_sites"][i]["url"]== url:
                delete=i
                break
        print(delete)
        if delete is not None:
            del config["proxy_gather"]["web_sites"][delete]
            update_config(config)
            return jsonify(True)
        return False

class get_all_proxy_list(Resource):
    @auth.login_required
    def get(self):
        path=op.join("proxy_gather", "proxy resources", "good_proxy.txt")
        with open(path, "r") as f:
            return jsonify([p.replace("\n", "") for p in f.readlines()])


api.add_resource(http_proxy, "/http/proxy")
api.add_resource(get_all_configs, "/configs")
api.add_resource(get_url_config, "/config")
api.add_resource(update_config, "/config")
api.add_resource(delete_config, "/config")
api.add_resource(get_all_proxy_list, "/all-proxy-list")






if __name__ == '__main__':
    from proxy_gather.Proxy import routine
    from proxy_gather.Proxy import on_startup
    import proxy_gather.Proxy  as p

    on_startup()
    print(f"TEST {next(p.proxy_pool)}")
    host = config["web_application"]["Flask"]["host"]
    port = config["web_application"]["Flask"]["port"]
    app.run(host=host, port=port)

    s = sched.scheduler(time.time, time.sleep)
    # each 12 hours
    s.enter(43200, 1, routine)
    # each 2 hours
    s.enter(7200, 1, on_startup)
    s.run()