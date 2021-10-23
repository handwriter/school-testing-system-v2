from flask import Flask, render_template, request, redirect, jsonify, send_file
import json
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent
import os
from pathlib import Path
from threading import Thread
import sys
import requests
import subprocess
from flask_cors import CORS
from contextlib import contextmanager
import socket


@contextmanager
def socketcontext(*args, **kw):
    s = socket.socket(*args, **kw)
    try:
        yield s
    finally:
        s.close()


def get_my_ip():
    with socketcontext(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
IP = get_my_ip()


class CustomQWebView(QWebEngineView):
    def mousePressEvent(self, a0: QMouseEvent) -> None:
        print(a0.button())


class MainWindow(QMainWindow):
    def __init__(self, f_app: Flask, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.f_app = f_app
        self.webEngineView = CustomQWebView()
        self.setCentralWidget(self.webEngineView)
        with f_app.test_request_context("/"):
            self.webEngineView.setHtml(render_template("empty_loading.html", ip=f"http://{IP}:874/"))


class Config(object):
    config = {}
    q_app = None  # type: QApplication
    q_window = None  # type: QMainWindow
    f_app = None  # type: Flask
    path = ""

    def __init__(self, path: str = None):
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
        if not Path(path).exists():
            with open(path, "w") as wfile:
                json.dump({}, wfile)
        with open(path, "r") as config_file:
            try:
                ld = json.load(config_file)
                if len(ld) != 0:
                    return ld
            except Exception as e:
                pass
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


app_ = Flask(__name__)
CORS(app_)
connected_users = []
notifies = []
connected_teacher = ""
user_config = Config("config.json")
kwargs = {'host': '0.0.0.0', 'port': 874, 'threaded': True, 'use_reloader': False, 'debug': False}
user_config.f_app = app_
flaskThread = Thread(target=app_.run, daemon=True, kwargs=kwargs).start()


@app_.route("/status.png")
def status():
    return send_file(open('static/img/status.png', 'rb'), mimetype="image/png")


@app_.route("/close_app")
def close_app():
    if request.host.split(':')[0] != request.remote_addr:
        return jsonify({'status': 'false'})
    user_config.q_app.quit()
    return "Close"


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


@app_.route("/connect_to")
def connect_to():
    print('cccc')
    global connected_teacher
    if not "addr" in request.args:
        print("nnottt")
        return jsonify({'status': 'false'})
    try:
        data = requests.get(f"http://{request.args['addr']}:874/connect", timeout=0.5).json()
        print(data)
        if data['status'] == 'true':
            connected_teacher = request.args['addr']
        return jsonify(data)
    except Exception as e:
        return jsonify({'status': 'false', 'error': str(e)})


@app_.route("/disconnect")
def disconnect():
    if not 'addr' in request.args:
        return jsonify({'status': 'false'})
    if request.remote_addr != request.args['addr'] or not request.args['addr'] in connected_users or not user_config[
        "teacher"]:
        return jsonify({'status': 'false'})
    connected_users.remove(request.args['addr'])
    return jsonify({'status': 'true'})


@app_.route("/disconnect_from")
def disconnect_from():
    global connected_teacher
    if request.host.split(':')[0] != request.remote_addr or connected_teacher == '' or user_config["teacher"]:
        return jsonify({'status': 'false'})
    try:
        data = requests.get(f"http://{connected_teacher}:874/disconnect?addr={request.host.split(':')[0]}",
                            timeout=0.5).json()
        if data['status'] == 'true':
            connected_teacher = ""
        return data
    except Exception as e:
        return jsonify({'status': 'false', "error": str(e)})


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
    if request.host.split(':')[0] != request.remote_addr:
        return jsonify({'status': 'false', 'error': 'Permission denied'})
    data = []
    for i in range(1, 255):
        try:
            r = requests.request("get", f"http://192.168.1.{i}:874/", timeout=0.01)
            data.append([f"192.168.1.{i}", r.json()])
        except:
            pass
    user_config["last_scan"] = data
    return jsonify({"users_data": data, "connected_users": connected_users})


@app_.route("/get_other_file")
def get_other_file():
    if connected_teacher == request.remote_addr:
        try:
            file = requests.get(f"http://{request.remote_addr}/get_file?f_name={request.args['f_name']}")
            open(f'{ROOT_DIR}/SharedFiles/{request.args["f_name"]}', 'wb').write(file.content)
            subprocess.Popen(f'explorer /select,{request.args["f_name"]}', cwd=ROOT_DIR + "/SharedFiles/")
            return jsonify({'status': 'true'})
        except:
            pass
    return jsonify({'status': 'false'})


@app_.route('/user_data')
def usr_data():
    usr = {'connected_users': connected_users, "connected_teacher": connected_teacher}
    usr.update(user_config.config)
    if request.host.split(':')[0] == request.remote_addr:
        return jsonify(usr)


@app_.route("/")
def index():
    if request.host.split(':')[0] == request.remote_addr:
        if not user_config.__contains__("username"):
            return redirect("/join")
        return render_template("index.html", user_config=user_config, connected_users=connected_users, active_item=0,
                               last_scan=user_config["last_scan"], connected_teacher=connected_teacher)
    return jsonify({"teacher": user_config["teacher"], "username": user_config["username"]})


@app_.route("/files", methods=["GET", "POST"])
def files():
    files = []
    for i in os.walk(f"{ROOT_DIR}/SharedFiles/"):
        files = i[2]
        break
    print(files)
    if request.host.split(':')[0] == request.remote_addr:
        other_data = []
        if connected_teacher != '':
            a = requests.get(f"http://{connected_teacher}:874/files").json()
            if a['status'] == 'true':
                other_data = a['files']
        return render_template("files.html", active_item=1, user_config=user_config, files=files, other_data=other_data,
                               connected_teacher=connected_teacher)
    elif user_config["teacher"] and request.remote_addr in connected_users:
        return jsonify({'status': 'true', 'files': files})
    return jsonify({"status": "false"})


@app_.route('/open_file')
def open_file():
    if request.host.split(':')[0] != request.remote_addr:
        return jsonify({'status': 'false', 'error': 'Permission denied'})
    try:
        subprocess.Popen(request.args["f_name"], shell=True, cwd=ROOT_DIR + "/SharedFiles/")
        return jsonify({'status': 'true'})
    except:
        return jsonify({'status': 'false'})


@app_.route('/select_file')
def select_file():
    if request.host.split(':')[0] != request.remote_addr:
        return jsonify({'status': 'false', 'error': 'Permission denied'})
    try:
        subprocess.Popen(f'explorer /select,{request.args["f_name"]}', cwd=ROOT_DIR + "/SharedFiles/")
        return jsonify({'status': 'true'})
    except:
        return jsonify({'status': 'false'})


@app_.route("/delete_file")
def delete_file():
    if request.host.split(':')[0] != request.remote_addr:
        return jsonify({'status': 'false', 'error': 'Permission denied'})
    try:
        if '..' in Path(f"{ROOT_DIR}/SharedFiles/{request.args['f_name']}").parts:
            raise Exception()
        os.remove('SharedFiles/' + request.args['f_name'])
        return jsonify({"status": "true"})
    except:
        return jsonify({'status': 'false', 'error': 'Permission denied'})


@app_.route('/get_file')
def get_file():
    try:
        if '..' in Path(f"{ROOT_DIR}/SharedFiles/{request.args['f_name']}").parts:
            raise Exception()
        return send_file(f"{ROOT_DIR}/SharedFiles/{request.args['f_name']}", download_name=request.args['f_name'])
    except Exception as e:
        print(e)
        return jsonify({'status': 'false', 'error': 'Permission denied'})


@app_.route("/upload_file", methods=["POST"])
def upload_file():
    if request.remote_addr != connected_teacher:
        return jsonify({'status': 'false', 'error': "Permission denied"})
    request.files["upload_file"].save("SharedFiles/" + request.files["upload_file"].filename)
    notifies.append(request.files["upload_file"].filename)
    return "Ok"


@app_.route('/send_file')
def sends_file():
    if request.host.split(':')[0] != request.remote_addr:
        return jsonify({'status': 'false', 'error': 'Permission denied'})
    for i in connected_users:
        try:
            requests.post(f"http://{i}:874/upload_file",
                          files={"upload_file": open(ROOT_DIR + "/SharedFiles/" + request.args['f_name'], "rb")})
            pass
        except Exception as e:
            print(e)
            continue
    return jsonify({'status': 'true'})


@app_.route('/notifies')
def notifications():
    if request.host.split(':')[0] != request.remote_addr or len(notifies) == 0:
        return jsonify({'status': 'false', 'error': 'Permission denied'})
    try:
        print(notifies)
        dt = notifies.copy()
        notifies.clear()
        return jsonify({'status': 'true', 'notify': dt[-1]})
    except Exception as e:
        return jsonify({'status': 'false'})


app = QApplication(sys.argv)
user_config.q_app = app
window = MainWindow(app_)
user_config.q_window = window
window.setWindowFlags(Qt.CustomizeWindowHint)
window.show()
app.exec_()