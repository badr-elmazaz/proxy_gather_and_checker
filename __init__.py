import os
import os.path as op
import json

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

config_path=op.join(THIS_FOLDER, "static", "config.json")
with open(config_path) as config_file:
        config=json.load(config_file)