from flask import Flask
import json
from pathlib import Path


class Config(object):
    config = {}
    path = ""

    def __init__(self, path: str=None):
        if path:
            self.path = path
            self.config = self.load_config(path)

    def __getitem__(self, item):
        if not item in self.config:
            return False
        return self.config[item]

    def __setitem__(self, item, value):
        self.config[item] = value
        self.save_config()

    @staticmethod
    def load_config(path: str) -> dict:
        with open(path, "w") as config_file:
            try:
                return json.load(config_file)
            except:
                json.dump({}, config_file)
                return {}

    def save_config(self) -> bool:
        with open(self.path, "w") as config_file:
            try:
                json.dump(self.config, config_file)
                return True
            except:
                return False


app = Flask(__name__)
user_config = Config("config.json")


@app.route('/')
def index():
    return "Hello, world!"

app.run("0.0.0.0")