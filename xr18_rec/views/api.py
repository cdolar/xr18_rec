from flask import Blueprint, jsonify, make_response
from flask import current_app as app

from subprocess import Popen, PIPE, TimeoutExpired
from datetime import datetime
from time import sleep

import os

api = Blueprint("api", __name__)

@api.route("/rec")
def rec():
    filename = datetime.now().strftime('%Y-%m-%d--%H-%M-%S__xr18rec.wav')
    #audiodev = "hw:X18XR18,0"
    audiodev = "hw:CODEC,0"
    buffersize = 512*1024
    channels = 12
    bits = 24
    rate = 48000
    env = os.environ
    env['AUDIODEV']=audiodev
    cmd = [
        'rec',
        '--buffer={}'.format(buffersize),
        '-c {}'.format(channels),
        '-b {}'.format(bits),
        '-r {}'.format(rate),
        filename
    ]
    global proc
    proc = Popen(cmd, env=env, stdout=PIPE, stderr=PIPE, text=True)
    output = ""
    err = ""
    #try:
    #    (output, err) = proc.communicate(timeout=2)
    #except TimeoutExpired:
    #    pass
    
    return make_response(jsonify({"status":"started recording", "filename":filename, "output":output, "error":err, "pid":proc.pid,"args":proc.args}))

@api.route("/stop")
def stop():
    global proc
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
    global proc
    if proc is None:
        status = "No recording running"
    else:
        retcode = proc.poll()
        if retcode is None:
            status = "recording ongoing"
        else:
            status = "recording stopped with returncode {}".format(retcode)
    return make_response(jsonify({"status":status}))
