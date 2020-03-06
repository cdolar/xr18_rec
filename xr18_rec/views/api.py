from flask import Blueprint, jsonify, make_response
from flask import current_app as app

from subprocess import Popen, PIPE
from datetime import datetime
from time import sleep

import os

api = Blueprint("api", __name__)

proc = None

@api.route("/rec")
def rec():
    filename = datetime.now().strftime('%Y-%m-%d--%H-%M-%S__xr18rec.wav')
    #audiodev = "hw:X18XR18,0"
    audiodev = "hw:CODEC,0"
    buffersize = 512*1024
    channels = 12
    bits = 24
    rate = 48
    env = os.environ
    env['AUDIODEV']=audiodev
    cmd = [
        'rec',
        '--buffer {}'.format(buffersize),
        '-c {}'.format(channels),
        '-b {}'.format(bits),
        '-r {}'.format(rate),
        filename
    ]
    proc = Popen(cmd, env=env, stdout=PIPE, stderr=PIPE, text=True)
    (output, err) = proc.communicate(timeout=2)
    return make_response(jsonify({"status":"started recording", "filename":filename, "output":output, "error":err}))

@api.route("/stop")
def stop():
    status = ""
    if proc is None:
        status = "No recording running to stop"
    else:
        retcode = proc.poll()
        if retcode is None:
            status = "recording ongoing, terminating it"
            proc.terminate()
        else:
            status = "recording stopped with returncode {}".format(retcode)
    return make_response(jsonify({"status":status}))

@api.route("/status")
def status():
    status = ""
    if proc is None:
        status = "No recording running"
    else:
        retcode = proc.poll()
        if retcode is None:
            status = "recording ongoing"
        else:
            status = "recording stopped with returncode {}".format(retcode)
    return make_response(jsonify({"status":status}))
