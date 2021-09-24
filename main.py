from flask import Flask, render_template, request, redirect, jsonify
import json
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout, QApplication
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
from PyQt5.QtCore import QUrl, Qt
import nmap
import os
import pythonping
from pathlib import Path
import base64
from threading import Thread
import sys
import requests

import socket


def get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    name = s.getsockname()[0]
    s.close()
    return name


class MainWindow(QMainWindow):
    def __init__(self, f_app: Flask, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # widget = QWidget()
        # label = QLabel("Flask is running...")
        # self.layout = QVBoxLayout()
        # self.browser = QWebEnginePage()
        # # self.layout.addWidget(label)
        # self.layout.addWidget(self.browser)
        # widget.setLayout(self.layout)
        # self.setCentralWidget(widget)
        # vbox = QVBoxLayout(self)
        self.f_app = f_app
        self.webEngineView = QWebEngineView()
        self.setCentralWidget(self.webEngineView)
        self.webEngineView.load(QUrl(f"http://{get_my_ip()}:874/"))
        # vbox.addWidget(self.webEngineView)

        # self.setLayout(vbox)
        # Thread(target=while_flask_app_loaded, args=[f_app, self.webEngineView]).start()

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

    def __contains__(self, item):
        return item in self.config

    @staticmethod
    def load_config(path: str) -> dict:
        with open(path, "r") as config_file:
            try:
                return json.load(config_file)
            except Exception as e:
                print(e)
                with open(path, "w") as err_config_file:
                    json.dump({}, err_config_file)
                return {}

    def save_config(self) -> bool:
        with open(self.path, "w") as config_file:
            try:
                json.dump(self.config, config_file)
                return True
            except:
                return False

# app = Flask(__name__)

#
# app.run("0.0.0.0", port=874)
# print("MMMM")
app_ = Flask(__name__)
connected_users = []
user_config = Config("config.json")
kwargs = {'host': '0.0.0.0', 'port': 874, 'threaded': True, 'use_reloader': False, 'debug': False}
flaskThread = Thread(target=app_.run, daemon=True, kwargs=kwargs).start()

@app_.route('/connect')
def connect():
    if request.remote_addr == request.host:
        return jsonify({'status': 'false'})
    try:
        r = requests.request("get", f"http://{request.remote_addr}:874/", timeout=0.01).json()
        if r['teacher'] == False and user_config['teacher'] == True and not request.remote_addr in connected_users:
            connected_users.append(request.remote_addr)
            return jsonify({'status': 'true'})
        return jsonify({'status': 'false'})
    except:
        return jsonify({'status': 'false'})


@app_.route('/join', methods=["POST", "GET"])
def join():
    if request.method == 'POST':
        try:
            user_config["username"] = request.form["username"]
            user_config["teacher"] = request.form["user_type"] == "1"
            return redirect("/")
        except:
            pass
    return render_template("login.html")

@app_.route('/find_local_users')
def find_local_users():
    data = []
    for i in range(1, 255):
        try:
            r = requests.request("get", f"http://192.168.1.{i}:874/", timeout=0.01)
            data.append([f"192.168.1.{i}", r.json()])
        except:
            pass
    user_config["last_scan"] = jsonify(data)
    return jsonify(data)


@app_.route("/")
def index():
    if request.host.split(':')[0] == request.remote_addr:
        if not user_config.__contains__("username"):
            return redirect("/join")
        return render_template("index.html", user_config=user_config, connected_users=connected_users)
    return jsonify({"teacher": user_config["teacher"], "username": user_config["username"]})

app = QApplication(sys.argv)
window = MainWindow(app_)
window.setWindowFlags(Qt.CustomizeWindowHint)
window.show()
app.exec_()