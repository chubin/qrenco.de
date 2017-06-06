#!/usr/bin/env python
# vim: set encoding=utf-8

import gevent
from gevent.wsgi import WSGIServer
from gevent.queue import Queue
from gevent.monkey import patch_all
patch_all()

import sys
import logging
import os
import re
import requests
import socket
import subprocess
import time
import traceback
import dateutil.parser
import json

import jinja2
from flask import Flask, request, render_template, send_from_directory, send_file, make_response, redirect
app = Flask(__name__)

MYDIR = os.path.abspath(os.path.dirname( os.path.dirname('__file__') ))
sys.path.append("%s/lib/" % MYDIR)

from globals import FILE_QUERIES_LOG, LOG_FILE, TEMPLATES, STATIC, log, error

from qrencode_wrapper import qrencode_wrapper

if not os.path.exists(os.path.dirname(LOG_FILE)):
    os.makedirs(os.path.dirname(LOG_FILE))
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s %(message)s')

my_loader = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader(TEMPLATES),
])
app.jinja_loader = my_loader

def is_html_needed(user_agent):
    plaintext_clients = [ 'curl', 'wget', 'fetch', 'httpie', 'lwp-request', 'python-requests']
    if any([x in user_agent for x in plaintext_clients]):
        return False
    return True

def parse_args(args):
    result = {}

    q = ""
    for key, val in args.items():
        if len(val) == 0:
            q += key
            continue

    if q is None:
        return result
    if 'T' in q:
        result['no-terminal'] = True
    if 'q' in q:
        result['quiet'] = True

    for key, val in args.items():
        if val == 'True':
            val = True
        if val == 'False':
            val = False
        result[key] = val

    return result

@app.route('/files/<path:path>')
def send_static(path):
    return send_from_directory(STATIC, path)

@app.route('/favicon.ico')
def send_favicon():
    return send_from_directory(STATIC, 'favicon.ico')

@app.route('/malformed-response.html')
def send_malformed():
    return send_from_directory(STATIC, 'malformed-response.html')

def log_query(ip, found, topic, user_agent):
    log_entry = "%s %s %s %s" % (ip, found, topic, user_agent)
    with open(FILE_QUERIES_LOG, 'a') as my_file:
        my_file.write(log_entry.encode('utf-8')+"\n")

@app.route("/", methods=['GET', 'POST'])
@app.route("/<path:topic>", methods=["GET", "POST"])
def answer(topic = None):
    """
    Main rendering function, it processes incoming weather queries.
    Depending on user agent it returns output in HTML or ANSI format.

    Incoming data:
        request.args
        request.headers
        request.remote_addr
        request.referrer
        request.query_string
    """

    user_agent = request.headers.get('User-Agent', '').lower()
    html_needed = is_html_needed(user_agent)
    options = parse_args(request.args)

    if request.headers.getlist("X-Forwarded-For"):
       ip = request.headers.getlist("X-Forwarded-For")[0]
       if ip.startswith('::ffff:'):
           ip = ip[7:]
    else:
       ip = request.remote_addr
    if request.headers.getlist("X-Forwarded-For"):
       ip = request.headers.getlist("X-Forwarded-For")[0]
       if ip.startswith('::ffff:'):
           ip = ip[7:]
    else:
       ip = request.remote_addr


    if request.method == 'POST':
        data = ''
        for k, v in request.form.items():
            if k == '':
                if topic is None:
                    topic_name = "UNNAMED"
                else:
                    topic_name = topic
                data = v
            else:
                if v == '':
                    if topic is None:
                        topic_name = "UNNAMED"
                    else:
                        topic_name = topic
                    cheatsheet = k
                else:
                    topic_name = k
                    data = v

            answer, found = qrencode_wrapper(query_string=data, html=is_html_needed(user_agent))

        return answer
        # if html_needed:
        #     return redirect("/")
        # else:
        #     return "OK\n"

    if 'topic' in request.args:
        return redirect("/%s" % request.args.get('topic'))

    query_string = request.url
    if query_string.startswith('http://'):
        query_string = query_string[7:]
    elif query_string.startswith('https://'):
        query_string = query_string[8:]

    query_string = query_string[query_string.index('/')+1:]
    answer, found = qrencode_wrapper(query_string=query_string, request_options=options, html=is_html_needed(user_agent))
    
    log_query(ip, found, topic, user_agent)
    return answer

server = WSGIServer(("", 8003), app) # log=None)
server.serve_forever()

