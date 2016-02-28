from core.utils import *
from io import StringIO
import sys

commands = [
    ('/python', ['command'])
]
description = 'Executes python code.'


def run(m):
    input = get_input(m)

    if not input:
        return send_message(m, 'No input')

    cout = StringIO()
    sys.stdout = cout
    cerr = StringIO()
    sys.stderr = cerr
    try:
        exec(input)
    except:
        send_exception(m)

    if cout.getvalue():
        send_message(m, str(cout.getvalue()))

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
