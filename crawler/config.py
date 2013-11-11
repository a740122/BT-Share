#!/usr/bin/env python
# encoding: utf-8
import os

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

MONGO_SETTINGS = {
    "host": "localhost",
    "port": 27017,
    "database":"bt_tornado"
}

GMAIL_CONFIG = {
    'mail_host': "smtp.gmail.com",
    'mail_port': 25,
    'mail_user': "zhkzyth",
    'mail_pass': "zhg709394",
    'mail_postfix': "gmail.com",
}
