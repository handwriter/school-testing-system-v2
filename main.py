from flask import Flask, render_template, request, redirect, jsonify, send_file
import json
# from PyQt5.QtWidgets import QMainWindow, QApplication
# from PyQt5.QtWebEngineWidgets import QWebEngineView
# from PyQt5.QtCore import Qt, QSize
# from PyQt5.QtGui import QMouseEvent, QIcon
import os
from pathlib import Path
from threading import Thread
import sys
import requests
import subprocess
import PySimpleGUI as sg
from psgtray import SystemTray
from flask_cors import CORS
from contextlib import contextmanager
import socket
from sdamgia import SdamGIA
from html.parser import HTMLParser
import base64


class HTMLFilter(HTMLParser):
    text = ""

    def handle_data(self, data):
        self.text += data



SDAMGIA = SdamGIA()

ICON_BASE64 = b'AAABAAEAQEAAAAEAIAAoQgAAFgAAACgAAABAAAAAgAAAAAEAIAAAAAAAAEAAAMMOAADDDgAAAAAAAAAAAAD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AIS56KqJu+PGi7vj/////wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8Aibrkqou748aLu+P/i7vj/4u74/+Lu+P/ibvj/4u74/+BvOOq////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wCGuuWqibvjxom74/+JuuT/ibrk/4m65P+Lu+P/i7vj/4u64/+VkJf/mZia/5mZmf+Lu+P/ibvj4////wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8AvNFqjsHRbMbB0Wz/wNBs/4m64/+Ju+P/ibvj/4m74/+JuuT/ibrk/4m74/+Ju+P/iLni/4yXov+ZmJr/mZia/5mYmv+ZmJr/4ufu/+z0/v+ZmZn/i7vj/4m74/////8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AMHRa46/z2z/irrj/4m74/+Ju+P/i7vj/4u74/+Ju+P/ibvj/4m74/+Iu+P/kZ+r/5iamv+bmJn/m5iZ/5mYmf/Q0df/7vT8/+zz///s8///7PP//+7z/v/s9P7/mZmZ/4u74/+Ju+P/////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wCIu+Oqibvjxom74/+Ju+P/i7vj/4u74/+Ju+P/ibvj/4u74/+InbD/mpmb/5mYmv+ZmJr/mZia/8fM0f/v9f3/7PT+/+z0/v/s9P7/7PT+/+z0/v/s8///7PP//+zz///u8/7/7PT+/5qamv+JuuT/ibvj/////wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AIm746qJu+PGibvj/4m74/+Ju+P/ibvj/4m74/+Ju+P/iL7f/42dr/+bl5n/mZia/5uYmf+ZmZn/urzC/+z0/v/u8/3/7PT+/+z0/v/s9P7/7PT+/+z0/v/s9P7/7PT+/+z0/v/s9P7/7PP//+zz///s8///7vP+/+z0/v+Ympr/ibrk/4m74/+Ju+Oq////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8Aibvjxom74/+Ju+P/ibvj/4m74/+Ju+P/iaSv/5mZmf+ZmZn/m5iZ/5yZmv+foqb/7PP+/+zz///s8///7PT+/+z0/v/s9P7/7vP+/+z0/v/s9P7/7PT+/+z0/v/s9P7/7PT+/+z0/v/s9P7/7PT+/+zz///s8///7PP//+7z/v/s9P7/8fX8/5WXnv+Ju+P/ibvjqv///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AIm746qJu+P/ibvj/4m74/+UmJz/mZia/5ednf/s8v//7PP//+zz///s8///7PP//+rz///r9f3/6PP+/+z0/v/s9P7/7PT+/+7z/v/s9P7/7PT+/+z0/v/s9P7/7PT+/+z0/v/s9P7/7PT+/+z0/v/s8///7PP//+zz///u8/7/7PT+/+7z/v+ZmZn/ibvj/4m74/////8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wCHvOGOibvj/4m74/+Ju+P/7PT+/+z0/v/s8///7vP+/+zz//+ytLf/mZmX/5uYmf+ZmZn/lpaY/83S1/+ZmJr/7PT8/+z0/v/u8/7/7PT+/+z0/v/s9P7/7PT+/+z0/v/s9P7/7PT+/+z0/v/s9P7/7PP//+zz///s8/7/oaeo/+z0/v/u8/7/mZmZ/4m74/+Ju+P/////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AIm74/+Ju+P/ibvj/+r0/v/s9P7/7PP//5mYmv+cmJn/6vT+/+z0/v/s9P7/7PT+/+z0/v/s9P7/yMvQ/+z1/v/s9P7/7vP+/+z0/v/s9P7/7PT+/+z0/v/s9P7/7fb9/+z0/P+pr7P/mZea/5eYmv+XmJr/l5iW/+z0/v/s9P7/7vP+/5mZmf+Lu+P/ibvj/8DQav////8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AMHQbuOJu+P/ibvj/4u74//q9P7/7PT+/+z0/v+Xl5f/7PT+/+z0/v/s9P7/7PT+/+z0/v/s9P7/7PT+/+r0/v+Qk5f/7PT+/+7z/v/q9P7/6/X//7S1uv+XmJr/mZmX/5uZl/+YmZf/7vL+/+z0/v/s8///7PP//+z0/v/s9P7/7PT+/+7z/v+bmZf/iLri/4m74/+Pwsj/wdFs/////wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AMHPb6rB0G7/ibvj/4m74/+Lu+P/7vP+/+z0/v/s9P7/m5ma/+z0/v/s9P7/7PT+/+z0/v/s9P7/7PT+/+z0/v/s9P7/mZmZ/+z0/v/u8/7/mZmX/5mZmf/t8///7fX//+z0/v/s9P7/7PT+/+z0/v/q9P7/6vP+/5WWmf+ZmJr/mZia/5mYmv/u8/7/qa20/5K61f+Ju+P/ibvj/8HRbP/B0Wzj////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////ALXFeo7D0G7/wdBu/4m74/+Ju+P/i7vj/+7y/v/s9P7/7PT+/5mZmf/s9P7/7PT+/+z0/v/s9P7/7PT+/+z0/v/s9P7/7PT+/5mZmf/s9P7/7vP+/+z0/v/s9P7/7vP+/+7z/v/q9P7/lZeY/5mZmf+ZmZn/mZia/5eYnf/t8/7/7vP+/+zz///s8///7vP+/+7z/v+cl5n/ibvj/4m74//B0Wz/wdFs/8HRbMb///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wDD0G7/w9Bu/8HQbv+EueT/ibvj/4u74/+Ku+H/7PT+/+z0/v+bmZf/7PT+/+z0/v/s9P7/7PT+/+z0/v/s9P7/7PT+/+z0/v+XmJr/7PT+/+7z/v/l7/D/mZmZ/5mYmv+amZv/l5aV/+r0/v/s9P7/7PT+/+zz///s8///6vP//+rz///q8vz/mZia/+7z/v/u8v//mZia/4m74/+Ju+P/wdFs/8HRbP/B0Wz/vs2Djv///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wDB0G7jw9Bu/8PQbv/B0G7/us12/4m74/+Lu+P/ibvj/+z0/v/s9P7/l5ia/+70/P/s9P7/7PT+/+z0/v/s9P7/7PT+/+z0/v/s9P7/l5ia/+z0/v/u8/7/7PT+/+zz///u8/7/7vP+/+7z/v/s9P7/7PT+/+z0/v+amJn/m5iZ/5uYmf+cmZj/1t3k/+zz/v/u8/7/7vL//5mYmv+Ju+P/ibvj/8LQav/B0Wz/wdFs/8HQbv////8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8AwdBu/8PQbv/D0G7/wdBu/8HQbv+Ju+P/i7vj/4m74//s9P7/7PT+/46Tl//s9Pz/7PT+/+z0/v/s9P7/7PT+/+z0/v/s9P7/7PT+/+v1/P/v9fz/7vP+/+z0/v/s8///6/T+/5iYmf+ZmZn/mZmZ/5mZmf/S0tb/6/P+/+zz///s8///7PP//+7z/v/s8///7vP+/+7y//+XmJr/i7rk/4m74/+60XL/wdFs/8HRbP/B0G7/wdBrxv///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8AwdFs48HQbv/D0G7/w9Bu/8HQbv/B0G7/ibvj/4u74/+Ju+P/7/X9/+z0/v/s9P3/lJWZ/+z0/v/s9P7/7PT+/+z0/v/s9P7/7PT+/+z0/v+ZmJr/7PT+/+7z/v/s9P7/m5mX/73Bx//s9Pz/7PT+/+zz///s8///7PP//+zz///s8///7PP//+zz///u8/7/7PP//+7z/v/u8v//l5ia/4G85P+Ju+P/ibrk/8HRbP/B0Wz/wdBu/8PQbP////8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8AusaCAsHRbP/B0G7/w9Bu/8PQbv/B0G7/wdBu/4m74/+Lu+P/ibvj/+r0/v/s9P7/7PP//5yYm//s9P7/7fX//+ry/f+XmJr/m5iZ/5uZl/+bmJn/7PT8/+z0/v/u8/7/7PT+/+z0/v/s9P7/7PT+/+z0/v/s8///7PP//+zz///s8///7PP//+zz///s8///7vP+/+zz///u8/7/7vL//+jz/f+ZmZn/ibvj/4m65P/B0Wz/wdFs/8HQbv/D0Gz/wdBuxv///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AMHRbOPB0Wz/wdBu/8PQbv/D0G7/wdBu/8HQbv+IuuL/i7vj/4m74/+gv9j/7PT+/+zz///s9P7/mZmZ/5mZmf+srrH/7fX//+zz///s9P7/7PP//+zz///s9P7/7vP+/+z0/v/s9P7/7PT+/+z0/v/s9P7/7PP//+zz///s8///7PP//+zz///s8///7PP//+7z/v/s8///7vP+/+7y///u8/7/mpiZ/4m74/+JuuT/v9Bu/8HRbP/B0G7/w9Bs/8HQbv////8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wDB0Wz/wdFs/8HQbv/D0G7/w9Bu/8HQbv/B0G7/kr/K/4u74/+Ju+P/ibvj/+z0/v/s8///7PT+/+z0/v/s8///7PT+/+z0/v/s8///7PT+/+/0/v/P09z/7PT+/+7z/v/s9P7/7PT+/+z0/v/s9P7/7PT+/+zz///s8///7PP//+zz///s8///7PP//+zz///u8/7/7PP//+7z/v/u8v//7vP+/5uYmf+Lu+P/ibrk/8PQbv/B0Wz/wdBu/8PQbP/B0G7/wdJqjv///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wDB0mmqwdFs/8HRbP/B0G7/w9Bu/8PQbv/B0G7/wdBu/8HQbv+Lu+P/ibvj/4m74//s9P7/7PP//+z0/v/s9P7/6vP//5OVl/+ZmZn/mZia/5mZmf+YmJr/6vT+/5mZmf/s9Pz/7PT+/+z0/v/s9P7/7PT+/+z0/v/s8///7PP//+zz///s8///7PP//+zz///s8///7vP+/+zz//+XmJb/8PP6/+7z/v+cmZr/i7vj/4m65P+60Gv/wdFs/8HQbv/D0Gz/wdBu/8HRbOP///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8AwdFs/8HRbP/B0Wz/wdBu/8PQbv/D0G7/wdBu/8HQbv/B0G7/i7vj/4m74/+Ju+P/7PT+/+zz///s9P7/l5iZ/5iZm//s9P3/7PT+/1wK2//q8/v/7vP+/+z0/v/s9P7/mZqX/+z0/v/s9P7/7PT+/+z0/v/s9P7/7PP//+vz///q8///6vT+/5CSlv+ZmJr/mZia/5mYmv+Ulpj/8PT8/+zz/v/u8/7/mZia/4m65P+JuuT/irvh/8HRbP/B0G7/w9Bs/8HQbv/B0Wz/////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AMHRbP/B0Wz/wdFs/8HQbv/D0G7/w9Bu/8HQbv/B0G7/wdBu/4m84f+Ju+P/ibvj/+rz///s8///7PT+/5eYmv/s9P7/7PT+/+3z+v9cCtv/XAnc/+z0/P/s9P7/7PP//5mZmf/q9P7/7PT+/+z0/v/t9f//j5CX/5mYmv+amJn/m5iZ/5iamv/q9P7/7PP//+zz///s9P7/7PP//+zz///s8///7vP+/+/z+v+Goqz/ibrk/4m84P/B0Wz/wdBu/8PQbP/B0G7/wdFs/7nIbI7///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wDB0Wz/wdFs/8HRbP/B0G7/w9Bu/8PQbv/B0G7/wdBu/8HQbv+JvOH/ibvj/4m74//o7/7/7PP//+z0/v+ZmZn/7PT+/+z0/v9cCtv/XArb/1wJ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/wD///8A////AP///wD///8A////AP///wD///8AwdBsqsHRbP/B0Wz/wdFs/8HQbv+/z2z/UVBN/01NTf9MTU3/T0xN/8LTaf/B0G7/iLnj/4m74/+JuuT/yN/1/+z0/v/u8/7/mZiZ/+z0/v/s9P7/7PP//+zz///s8///7PP//+z0/v/u8/7/mZmZ/+z0/v/s9P7/7PP//+vy+/+Xlpj/mpmb/5mYmv+bmJn/lpSY/+r1/P8flvr/H5f4/x2Y+P8fl/j/HZj4/x2Y+P8dl/r/HZj4/x6X+P8dhvD/HYbw/x2G8P8dhvD/HYbw/x2G8P+OjH//jox//46Mfsb///8A////AP///wD///8A////AP///wD///8A////AL7KhGDB0Wz/wdFs/1FTP/9PTE7/TU1N/01NTf9NTU3/TU1N/01NTf8+Pj7/Pj4+/zw9Pv+Ju+P/ibrk/4m74//s9P7/7vP+/5iYmv/s9P7/7PT+/+zz///s8///7PP//+zz///s9P7/7vP+/5mYmv/s9P7/7PT+/6uts/+Tlpr/7PL//+70/P/s9P7/7PP//+zz///s8///7PT+/83p//8dmPj/H5f4/x2Y+P8dmPj/HZf6/x2Y+P8dmPj/HZf6/x+X9v8dhvD/HYbw/x2G8P+OjH//jox//46Mf/+OjH//jox//4BWy47///8A////AP///wD///8A////AP///wD///8AwdFs/09MTv9PTE7/T0xO/01NTf/v7+//8vLy//Ly8v86P97/ODg4/zs7O/8+Pj7/Pj4+/4i54/+Lu+P/7PT+/+7z/v+amJj/7PT+/+z0/v/s8///7PP//+zz///s8///7PT+/+7z/v/t9Pr/6PT7/+z0/v/s8///7PP//+zz/v/t9f//6fT8/5eYmv+ZmJr/mZia/5mYmv/o7PP/7PT+/yOU9v8dmPj/HZj4/x2X+v8dmPj/HZj4/x2X+v8dl/r/HZj4/xiH7P8dh+7/jox//46Mf/+OjH//jox//4uJg/+AUtL/gFLS/4JdxY7///8A////AP///wD///8A////AE9MTv9PTE7/9PH0//Hx8f9MTEz/8vLy//Ly8v/y8vL/OUPS/8LCwv/CwsL/wsLC/z09Pf8+Pj7/irnj/+z0/v/u8/7/7vf+/+zz/f/s9P7/7PP//+zz///s8///7PP//+z0/v/u8/7/7PT+/5aXlv/u8/7/7PP//5mYmv+bmJn/mpqa/9PX3P/t8/7/7PP//+zz///s8///7PP//+z0/v/t9f//5+vy/xuW9P8dl/r/HZj4/x2Y+P8dl/r/HZf6/x2Y+P8dmPj/////AI6Lf6qOjH//jox//46Mf/+AUtL/gFLS/4BS0v+AUtL/gFLS4////wD///8A////AE1MTuNPTE7/TkpN//Hx8f/y8vL/8vLy//Ly8v/y8vL/8vLy/8HBwf/CwsL/wsLC/8LCwv8+Pj7/Pj4+/z4+Pv/s9P7/7vP+/+30/P+ZmJr/7PT+/+zz///s8///7PP//+zz///s9P7/7vP+/+z0/v+XmJr/7vP+/+zz///s8///7PP+/+7z/v/s9P7/7PT+/+rz///p8Pf/mZmZ/5mYmv+ZmZn/mZia/+ry9//u8/7/7PP//x2Y9v8dmPj/HZf6/x2X+v8dmPj/HZj4xv///wD///8A////AI2LfcaJgor/gFLS/4BS0v+AUtL/gFLS/4BS0v9/UdHG////AE1MTo5NTE7/9PH0/01NTf/y8vL/8vLy//Ly8v/y8vL/8vLy//Ly8v/CwsL/wsLC/8LCwv89PT3/wsLC/8HBwf8+Pj7/Pj0//+7z/v/s8/7/mZia/+z0/v/s8///7PP//+zz///s8///7PT+/+7z/v/s9P7/l5ia/+7z/v/s8///7PP///D0/P+dmJn/mZmZ/5mZmf+bmJn/6PL8/+z0/v/s9P7/7PT+/+zz///s8///7PP//+zz///s8///6/P//x2X+v8dl/r/HZj4/////wD///8A////AP///wD///8Al3TU44BT0f+AUtL/gFLS/4BS0v+AUtL/////AP///wBNTE7/TEtN//Pw8v/y8vL/8vLy//Ly8v/y8vL/8vLy//Ly8v/y8vL/wsLC/8LCwv/CwsL/wsLC/8LCwv/CwsL/wsLC/z49P//s9P7/7PP+/5mZmf/q9P7/7PP//+zz///s8///7PP//+z0/v/u9Pz/lpmd/5OUmf/u8/7/7PP//62ztf/t9v3/7PP//+z0/v/s9P7/7PT+/+z0/v/s9P7/7PT+/+z0/v/s8///7PP//+zz///s8///7PP//+zz//+ZmJr/Xq7x/x6Y9cb///8A////AP///wD///8ArprIfpd20v+XdtL/lHLN/4BT0f+AU9H/f1LQjv///wCGhoYlTUxO/0tKTP/08fP/8vLy//Ly8v/y8vL/8vLy//Ly8v/y8vL/8vLy/8LCwv/CwsL/wsLC/8LCwv/CwsL/wsLC/8LCwv8+PT//Pj0+/+zz/v+Ul5j/mZ6i/+zz/v/w9v7/m5mX/5uYmf+bmJn/nJqY/+vz+//u8/7/7vP+/+zz///s8///7PP//+zz///s9P7/7PT+/+z0/v/s9P7/7PT+/+z0/P/s9Pz/7PP//+zz///s8///7PP//+zz///s8///ibrk/4m65P+JuuTj////AP///wD///8A////AJd20uOXdtL/l3bS/5d20v+XdtL/flPM/////wD///8ATU1Nqk1MTv/U1NT/9PLy//Ly8v/y8vL/8vLy//Ly8v/y8vL/8vLy//Hx8f/CwsL/wsLC/8LCwv/CwsL/wsLC/z09Pf85OTn/Ozs9/0A9Pv/s8///7PP//8vR1f+VmZn/8fb9/+7z/P/u8v//7vL//+zz///s8///7vP+/+7z/v/s8///7PP//+zz///s8///7PT+/+30/P+lf4X/poOH/6aDh/+mg4f/poOH/+zz///s8///7PP//9ns/P+HuuT/i7vj/4m65P+JuuT/ibrk/////wD///8A////AJd9v46XdtL/l3bS/5d20v+XdtL/l3bS/5d30I7///8A////AE1NTf9JSEr/eHzV/z5Gzv/y8vL/8vLy//Ly8v/y8vL/8vLy//Ly8v/CwsL/PT09/zw8PP/CwsL/wsLC/8LCwv/CwsL/wsLC/8HAw/9APT7/7PP//+zz///s8///7PP//+zz///s8///7vL//+7y///s8///7PP//+7z/v/u8/7/6PP+/6aEhf+mg4f/pYOH/6aDh/+mg4f/poOH/6aDh/+mg4f/poOH/7WSlf+Ju+P/ibvj/4m74/+Ju+P/i7vj/4m65P+Kueb/nsOz/7/SbMb///8A////AP///wD///8AlXbQxpV20v+VdtL/lXbS/5V20v////8A////AP///wBNTU3/9vX3//Xy9f/y8vL/8vLy//Ly8v/y8vL/8vLy//Ly8v9JSUn/xcC8/8LCwv/CwsL/wsLC/8LCwv/CwsL/wsLC/8LCwv/Av8L/QD0+/+zz///s8///7PP//+zz///s8///7PP//+7y/v/v9P//ooKI/6aDh/+mg4f/poOH/6aDh/+mg4f/poOH/6aDh/+mg4f/poOH/6aDh/+mg4f/poOH/6aDh//eur7/ibvj/4i64v+hwL3/wdFs/8HRbP/B0Wz/wdBu/8HQbv////8A////AP///wD///8A////AP///wD///8AlXfQ45V30P+Ud82O////AP///wD///8ATU1N/+Tj5v/18vX/8vLy//Ly8v/y8vL/8vLy//Ly8v/v7+//TU1N/z09Pf/CwsL/wsLC/8LCwv/CwsL/wsLC/8LCwv/CwsL/sbGz/0A9Pv/s8///7PP//+zz///s8///7PP//+zz//+khIX/poSF/6SEh/+mg4f/poOH/6aDh/+mg4f/poOH/6aDh/+mg4f/poOH/6aDh/+mg4f/poOH/6aDh/+mg4f/poOH/8HRbP/B0Wz/wdFs/8HRbP/B0Wz/wdFs/8HQbv/F23GO////AP///wD///8A////AP///wD///8A////AP///wCfjcOK////AP///wD///8A////AE5OTuNMS03/TkpN//Ly8v/y8vL/8vLy//Ly8v9NTU3/8vLy//Ly8v/CwsL/wsLC/8LCwv/CwsL/wsLC/8LCwv/Bw8H/LTWz/zI3rf9APT7/7PP//+zz///s8///7PP//+zz///s8///pISF/6aEhf+khIf/poOH/6aDh/+mg4f/poOH/6aDh/+mg4f/poOH/6aDh/+mg4f/pYKF/+C8wP/gvMD/poOH/8TSbv/B0Wz/wdFs/8HRbP/B0Wz/wdFs/8HRbP/B0G7j////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wBMTEyqTUxO/09MTv/y8vL/8vLy//Ly8v+/v7//8vLy//Ly8v/x8fH/wsLC/8LCwv/CwsL/wsLC/8LCwv/CwsL/wsLC/8LCxP9APT7/QD0+/+zy///n8v//ibrk/4m74/+Ju+P/ibvj/6CEhP+mhIX/pISH/6aDh/+mg4f/poOH/6aDh/+lgoX/4LzA/+C8wP/eu7//pISF/6SEh/+llHP/wdFr/8PQbP/D0Gz/wdFs/8HRbP/B0Wz/wdFs/8HRbP/B0Wzj////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AE1MTv9QTE//8vLy//f39//y8vL/8vLy//Ly8v/y8vL/wsLC/8LCwv/CwsL/wsLC/8LCwv/CwsL/wsLC/8LCwv/CwsT/QD0+/zE4Pv+JuuP/i7rk/4u65P+Ju+P/ibvj/4y62f/A0Wz/o4OE/969wP/gvMD/4b6//+C8wP+mg4f/poSF/6WEhf+khIX/pISF/6SEhf+khIf/w9Bs/8PQbP/D0Gz/w9Bs/8HRbP/B0Wz/wdFs/8HRbP/B0Wz/////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wBNTE7jTU1N//Hx8f/y8vL/8vLy//Ly8v/y8vL/8vLy/8LCwv/CwsL/wsLC/8LCwv/CwsL/wsLC/z09Pf8+Pj7/PDw+/0A9Pv+JuuT/j7nd/8HQbv/B0Wz/wdFs/8HRbP/D0Gz/wdBu/8HQbv/Fz23/rJh6/8DRbP+mgoT/poSF/6aEhf+nnnb/v9Fs/8HRbP+khIX/oISH/8PQbP/D0Gz/w9Bs/8PQbP/B0Wz/wdFs/8HRbP/B0Wz/////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AE1NTf/v7+//8fHx/0xMTP/y8vL/8vLy//Ly8v/CwsL/wsLC/8LCwv/CwsL/wsLC/8LCwv/BwcH/Ojo6/z49P/9EPjn/wdFs/8HQbP/B0G7/wdFs/8HRbP/B0Wz/w9Bs/8HQbv/B0G7/wdFs/8PQbP/B0Wz/wdFr/6aEhf+mhIX/ooSG/6aEhf+khIX/pISH/8HRbP/D0Gz/w9Bs/8PQbP/D0Gz/wdFs/8HRbP/B0Wz/////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AJGW56hNTU3/TU1N/01NTf9LS0v/8vLy//Ly8v/w8vL/wsLC/8LCwv/CwsL/UFBQ/8LCwv/CwsL/wsLC/z4+Pv8+PT//wdFs/8HRbP/B0Gz/wdBu/8HRbP/B0Wz/wdFs/8PQbP/B0G7/wdBu/8HRbP/D0Gz/wdFs/8HRbP/A0Wz/qoOF/62fef/B0Gz/w9Bs/8PQbP/D0Gz/w9Bs/8PQbP/D0Gz/w9Bs/8HRbP/B0Wzj////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////ADZC26o3Q9z/TE5OxkxMTKpNTU3/TExM//Ly8v/y8vL/O0Xc/8TBxP/EwcT/wsLC/z09Pf8+Pj7/PT09/z4+Pv8+Pj7/wdBu/8HRbP/B0Wz/wdBs/8HQbv/B0Wz/wdFs/8HRbP/D0Gz/wdBu/8HQbv/B0Wz/w9Bs/8HRbP/B0Wz/wdFs/8HRbP/B0Wz/w9Bs/8PQbP/D0Gz/w9Bs/8PQbP/D0Gz/w9Bs/8PQbP/E0m6q////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8AN0Tb/////wD///8ATU1Njk1NTf9NTU3/TU1N/yo1q//EwcT/xMHE/8HBwf8+Pj7/Pj4+/z4+Pv8+Pjnjv9Bu/8HQbv/B0Wz/wdFs/8HQbP/B0G7/wdFs/8HRbP/B0Wz/w9Bs/8HQbv/B0G7/wdFs/8PQbP/B0Wz/wdFs/8HRbP/B0Wz/wdFs/8PQbP/D0Gz/w9Bs/8PQbP/D0Gz/w9Bs/8PRa+P///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8ATU1Njk1NTf9BPj//QDw//0A8P/8+Pj7/Pj4+/z4+Pqr///8A////AP///wDB0WzjwdFs/8HRbP/B0Gz/wdBu/8HRbP/B0Wz/wdFs/8PQbP/B0G7/wdBu/8HRbP/D0Gz/wdFs/8HRbP/B0Wz/wdFs/8HRbP/D0Gz/w9Bs/8PQbP/D0Gz/w9Bs47vMchn///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AEpKSo5NTU3jT0xN4////wD///8A////AP///wD///8A////AP///wD///8A////AP///wDA0GrGwdFr/8HQbv/B0Wz/wdFs/8HRbP/D0Gz/wdBu/8HQbv/B0Wz/w9Bs/8HRbP/B0Wz/wdFs/8HRbP/B0Wz/w9Bs/8PQbP/E0m7G////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AE1NTf8AAAAAT0xO/09MTf9PTE7j////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8Av89oqsHSa+PB0mv/w9Bs/8HQbv/B0G7/wdFs/8PQbP/B0Wz/wdFs/8HRbP/B0Wz/wdFrqv///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AE1NTf8AAAAAN0Pe/0VFV/8AAAAAAAAAAExLTY7///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wBPT0//NkHd/zdD3v85Qt7/OULe/3V/5J1NTU3j////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8Ab29v+QAAAABue+N/OULe/zlC3v8AAAAATU1N/////wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AE1NTf8AAAAAAAAAAAAAAAAAAAAAAAAAAE1NTar///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wBLS0uqR0dH/wAAAAAAAAAAAAAAAE1NTf////8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AFlZWXxNTU3/TU1N/01NTcb///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//////+P////////8Af///////4AB//////8AAAH/////+AAAAf/////AAAAB////+AAAAAD////gAAAAAP///+AAAAAA////4AAAAAD////wAAAAAH///+AAAAAAP///wAAAAAAf//+AAAAAAA///4AAAAAAB///AAAAAAAH//8AAAAAAAP//gAAAAAAA//8AAAAAAAB//wAAAAAAAH//AAAAAAAAP/4AAAAAAAA//gAAAAAAAD/+AAAAAAAAH/4AAAAAAAAf/AAAAAAAAB/8AAAAAAAAH/wAAAAAAAAf/AAAAAAAAB/8AAAAAAAAH/wAAAAAAAAf/AAAAAAAAB/8AAAAAAAAH/wAAAAAAAAf/AAAAAAAAA/8AAAAAAAAA/wAAAAAAAAA/gAAAAAAAAA+AAAAAAAAQBwAAAAAAABwCAAAAAAAAPgYAAAAAAAA8BAAAAAAAADwMAAAAAAAAOAwAAAAAAAA8HAAAAAAAAH8cAAAAAAAAf7wAAAAAAAD//AAAAAAAAf/+AAAAAAAD//4AAAAAAAf//wAAAAAAD//+AAAAAAAf//wAAAAAAD///sAAAAAA////8A4AAAH////x/4AAD////+j/8AB/////03/////////Af////////9F/////////33/////////O/////////+H////////8='


PLATFORMS = {
    "resh": "Решу ЕГЭ",
    "komp": "КомпЕГЭ"
}

RESH_EGE_SUBJECTS = {
    'Математика': 'math',
    'Физика': 'phys',
    'Информатика': 'inf',
    'Русский язык': 'rus',
    'Биология': 'bio',
    'Английский язык': 'en',
    'Химия': 'chem',
    'География': 'geo',
    'Обществознание': 'soc',
    'Немецкий': 'de',
    'Французский': 'fr',
    'Литература': 'lit',
    'Испанский': 'sp',
    'История': 'hist'
}



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


ROOT_DIR = os.path.expanduser('~/Documents/SchoolTestSystem/')
if not Path(ROOT_DIR).exists():
    Path(ROOT_DIR).mkdir()
IP = get_my_ip()
if not Path(ROOT_DIR + "/SharedFiles/").exists():
    Path(ROOT_DIR + "/SharedFiles/").mkdir()


# class CustomQWebView(QWebEngineView):
#     def mousePressEvent(self, a0: QMouseEvent) -> None:
#         print(a0.button())
#
#
# class MainWindow(QMainWindow):
#     def __init__(self, f_app: Flask, *args, **kwargs):
#         super(MainWindow, self).__init__(*args, **kwargs)
#         self.f_app = f_app
#         self.webEngineView = CustomQWebView()
#         self.setCentralWidget(self.webEngineView)
#         app_icon = QIcon()
#         app_icon.addFile('16.png', QSize(16, 16))
#         app_icon.addFile('32.png', QSize(32, 32))
#         app_icon.addFile('48.png', QSize(48, 48))
#         app_icon.addFile('48.png', QSize(64, 64))
#         app_icon.addFile('256.png', QSize(256, 256))
#         app_icon.addFile('512.png', QSize(512, 512))
#         app_icon.addFile('1024.png', QSize(1024, 1024))
#         # app.setWindowIcon(app_icon)
#         with f_app.test_request_context("/"):
#             self.webEngineView.setHtml(render_template("empty_loading.html", ip=f"http://{IP}:874/"))


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
user_config = Config(ROOT_DIR + "/config.json")
kwargs = {'host': '0.0.0.0', 'port': 874, 'threaded': True, 'use_reloader': False, 'debug': False}

user_config.f_app = app_


# flaskThread = Thread(target=app_.run, daemon=True, kwargs=kwargs).start()


@app_.route("/status.png")
def status():
    return send_file(open('static/img/status.png', 'rb'), mimetype="image/png")


@app_.route("/close_app")
def close_app():
    if request.host.split(':')[0] != request.remote_addr:
        return jsonify({'status': 'false'})
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    # sys.exit(0)
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


@app_.route('/logout')
def logout():
    if request.host.split(':')[0] != request.remote_addr:
        return jsonify({'status': 'false', 'error': 'Permission denied'})
    user_config.config = {}
    user_config.save_config()
    return redirect("/join")


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
    print(request.headers)
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


@app_.route('/select_directory')
def select_directory():
    if request.host.split(':')[0] != request.remote_addr:
        return jsonify({'status': 'false', 'error': 'Permission denied'})
    try:
        os.startfile(ROOT_DIR + f"/{request.args['f_name']}")
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


@app_.route('/tests')
def tests():
    active_test_data = False
    if connected_teacher != '' and not user_config["teacher"]:
        active_test_data = requests.get(f"http://{connected_teacher}:874/active_test").json()
    files = []
    for i in os.walk(f"{ROOT_DIR}/SharedFiles/"):
        files = list(filter(lambda x: x.split(".")[-1] == "ts", i[2]))
        break
    print(files)
    return render_template("tests.html", active_item=2, user_config=user_config, files=files,
                           active_test_data=active_test_data, platforms=PLATFORMS)


@app_.route('/new_test', methods=["GET", "POST"])
def new_test():
    if request.method == "POST":
        user_config["new_test"]["q"][int(request.form["n"])]["text"] = request.form["qtext"]
        user_config["new_test"]["q"][int(request.form["n"])]["answer"] = request.form["qans"]
        user_config["new_test"]["title"] = request.form["test-title"]
        return render_template("new_test.html", active_item=2, user_config=user_config, contentColumn=True,
                               current=int(request.form["n"]))
    curr = 0
    if request.args.keys().__len__() == 0:
        user_config["new_test"] = {"title": "Новый тест", "q": [{"text": "Текст вопроса", "answer": "Ответ"}]}
    else:
        if "curr" in request.args:
            curr = int(request.args["curr"])
        elif "open" in request.args:
            with open(f'{ROOT_DIR}/SharedFiles/{request.args["open"]}', 'r') as fp:
                user_config["new_test"] = json.loads(fp.read())
        elif "save" in request.args:
            with open(f'{ROOT_DIR}/SharedFiles/{user_config["new_test"]["title"]}.ts', 'w') as fp:
                json.dump(user_config["new_test"], fp)
            return redirect("/tests")
    if curr >= len(user_config["new_test"]["q"]):
        user_config["new_test"]["q"].append({"text": "Текст вопроса", "answer": "Ответ"})
        curr = len(user_config["new_test"]["q"]) - 1
    return render_template("new_test.html", active_item=2, user_config=user_config, contentColumn=True, current=curr)


@app_.route("/active_stats")
def active_stats():
    return jsonify(user_config["active_test"])

@app_.route("/save_answer", methods=["POST"])
def save_answer():
    if request.remote_addr not in user_config["active_test"]["u"]:
        user_config["active_test"]["u"][request.remote_addr] = {"status": True}
    if user_config["active_test"]["u"][request.remote_addr]["status"]:
        user_config["active_test"]["u"][request.remote_addr][request.json["curr"]] = request.json["answer"]
    return jsonify({"status": False})

@app_.route("/get_answer", methods=["GET"])
def get_answer():
    if request.remote_addr in user_config["active_test"]["u"]:
        if request.json["curr"] in user_config["active_test"]["u"][request.remote_addr]:
            return jsonify({"answer": user_config["active_test"]["u"][request.remote_addr][request.json["curr"]]})
    return jsonify({"answer": ""})

@app_.route("/test_result", methods=["POST"])
def test_result():
    if request.remote_addr in user_config["active_test"]["u"]:
        user_config["active_test"]["u"][request.remote_addr]["status"] = False
        res = 0
        for i in user_config["active_test"]["u"][request.remote_addr]:
            if not i.isdigit():
                continue
            if user_config["active_test"]["u"][request.remote_addr][i] == user_config["active_test"]["q"][int(i)]["answer"]:
                res += 1
        return jsonify({"result": res})

    return jsonify({"result": 0})

@app_.route("/finish_test")
def finish_test():
    res = requests.post(f"http://{connected_teacher}:874/test_result").json()
    res2 = requests.get(f"http://{connected_teacher}:874/active_test").json()
    return render_template("finished_test.html", user_config=user_config, cur=int(res["result"]),
                           max=int(res2["count"]))





@app_.route("/active_test")
def active_test():
    if user_config["active_test"]:
        if "curr" in request.args:
            print(len(user_config["active_test"]["q"]))
            return jsonify(
                {"status": False, "data": user_config["active_test"]["q"][int(request.args["curr"])]["text"],
                 "count": len(user_config["active_test"]["q"])})
        return jsonify({"status": True, "filename": user_config["active_test"]["title"] + ".ts",
                        "count": len(user_config["active_test"]["q"])})
    else:
        return jsonify({"status": False, "filename": "false"})


@app_.route('/start_test', methods=["GET", "POST"])
def start_test():
    with open(f'{ROOT_DIR}/SharedFiles/{request.args["name"]}.ts', 'r') as fp:
        user_config["active_test"] = json.loads(fp.read())
        user_config["active_test"]["u"] = {}
    return redirect("active_stats")


@app_.route('/test/<int:curr>', methods=["GET", "POST"])
def test(curr):
    if request.method == "POST":
        requests.post(f"http://{connected_teacher}:874/save_answer", json={"curr": str(curr), "answer": request.form["qans"]})
        return redirect(f"/test/{curr + 1}")
    #curr = 0
    #if "curr" in request.args:
    #    curr = request.args["curr"]
    res = requests.get(f"http://{connected_teacher}:874/active_test?curr={curr}").json()
    if curr >= res["count"]:
        curr = 0
    ans = requests.get(f"http://{connected_teacher}:874/get_answer", json={"curr": str(curr)}).json()["answer"]

    return render_template("test.html", user_config=user_config, active_item=2, contentColumn=True, res=res, curr=curr, ans=ans)


@app_.route('/import_test/<string:platform>', methods=["GET", "POST"])
def import_test(platform):
    platform_index = list(PLATFORMS.keys()).index(platform)
    if request.method == "POST":
        test_data = {}
        if platform_index == 0 and "qid" in request.form and "subj" in request.form:
            data = []
            for ids in SDAMGIA.get_test_by_id(RESH_EGE_SUBJECTS[request.form["subj"]], str(request.form["qid"])):
                data.append(SDAMGIA.get_problem_by_id(RESH_EGE_SUBJECTS[request.form["subj"]], ids))
            test_data = {"title": f'{request.form["subj"]} {str(request.form["qid"])}', "q": []}
            for task in data:
                test_data["q"].append({"text": task["condition"]["text"], "answer": task["answer"]})
        elif platform_index == 1 and "qid" in request.form:
            test_data = {"title": f'{str(request.form["qid"])}', "q": []}
            res = requests.get(f"https://kompege.ru/api/v1/variant/kim/{request.form['qid']}").json()
            for task in res["tasks"]:
                if res["hideAnswer"]:
                    test_data["q"].append({"text": task["text"], "answer": "Ответ"})
                    continue
                test_data["q"].append({"text": task["text"], "answer": task["key"]})

        with open(f'{ROOT_DIR}/SharedFiles/{test_data["title"]}.ts', 'w') as fp:
            json.dump(test_data, fp)
        return redirect("/tests")

    return render_template("import_test.html", user_config=user_config, active_item=2, contentColumn=True,
                           platform=PLATFORMS[platform], subjects=RESH_EGE_SUBJECTS, platform_index=platform_index)




def tray_process():
    menu = ['', ['Open', '---', 'Exit']]
    layout = [[sg.Text('School Test System')]]
    window = sg.Window('Tray Window', layout, finalize=True, enable_close_attempted_event=True)
    tray = SystemTray(menu, single_click_events=False, window=window, tooltip="School Test System", icon=ICON_BASE64)
    window.hide()
    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Exit'):
            break

        if values[0] in ('Open', sg.EVENT_SYSTEM_TRAY_ICON_DOUBLE_CLICKED):
            os.system(f"start \"\" http://{IP}:874/")
        elif values[0] == "Exit":
            break
        window.hide()
        tray.show_icon()

    tray.close()
    window.close()
    requests.get(f"http://{IP}:874/close_app")

sys.stdout.flush()
trayThread = Thread(target=tray_process, daemon=True).start()
#os.system(f"start \"\" http://{IP}:874/")
app_.run("0.0.0.0", 874)

# app = QApplication(sys.argv)
# user_config.q_app = app
# window = MainWindow(app_)
# user_config.q_window = window
# window.setWindowFlags(Qt.CustomizeWindowHint)
# window.show()
# app.exec_()
