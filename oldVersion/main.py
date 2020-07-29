# -*- coding: utf-8 -*-
import json

from driver import Driver

if __name__ == '__main__':
    url = 'http://127.0.0.1:8069/web'
    username = 'admin@meow.com'
    password = 'admin'
    filename = 'test.json'

    d = Driver(url, username, password, filename)
