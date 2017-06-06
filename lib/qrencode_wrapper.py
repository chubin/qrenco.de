import gevent
from gevent.monkey import patch_all
from gevent.subprocess import Popen, PIPE, STDOUT
patch_all()

import sys
import os

MYDIR = os.path.abspath(os.path.dirname( os.path.dirname('__file__') ))
sys.path.append("%s/lib/" % MYDIR)
from buttons import GITHUB_BUTTON_FOOTER

INTERNAL_TOPICS = [':firstpage']

def github_button(button):
    repository = {
        "qrenco.de" :   'chubin/qrenco.de',
        "libqrencode":  'fukuchi/libqrencode',
    }

    full_name = repository.get(button, '')
    if not full_name:
        return ''

    short_name = full_name.split('/',1)[1]
    button = (
        "<!-- Place this tag where you want the button to render. -->"
        '<a aria-label="Star %(full_name)s on GitHub" data-count-aria-label="# stargazers on GitHub"'
        ' data-count-api="/repos/%(full_name)s#stargazers_count"'
        ' data-count-href="/%(full_name)s/stargazers"'
        ' data-icon="octicon-star"' 
        ' href="https://github.com/%(full_name)s"'
        '  class="github-button">%(short_name)s</a>'
    ) % locals()
    return button

def html_wrapper(answer):
    style =  'background-color: black; color: white;'
    buttons = "".join(github_button(x) for x in ['qrenco.de', 'libqrencode'])
    buttons += GITHUB_BUTTON_FOOTER
    return (
        "<html>"
        "<head>"
        "<title>qrenco.de</title>"
        "</head>"
        "<body style='%s'><pre>%s</pre>%s</body>"
        "</html>" 
    )% (style, answer, buttons)

def get_internal(topic):
    return open(os.path.join(MYDIR, "share", topic[1:]+".txt"), "r").read()

def qrencode_wrapper(query_string="", request_options=None, html=False):

    if query_string == "":
        query_string = ":firstpage"
    
    if query_string in INTERNAL_TOPICS:
        answer = get_internal(query_string)
    else:
        answer = query_string + "\n"
        cmd = ["qrencode", "-t", "UTF8", "-o", "-"]
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        answer = p.communicate(answer.encode('utf-8'))[0]

    if html:
        return html_wrapper(answer), True
    else:
        return answer, True
