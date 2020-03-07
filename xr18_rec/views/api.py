from flask import Blueprint, jsonify, make_response
from flask import current_app as app
from flask_socketio import emit

from subprocess import Popen, PIPE, TimeoutExpired, STDOUT
from datetime import datetime
from time import sleep

from xr18_rec import socketio

from threading import Thread


import os


api = Blueprint("api", __name__)
global proc, worker
proc = None

def relayStdOut():
    global proc
    while True:
        if proc is not None:
            for line in iter(proc.stdout.readline,''):
                socketio.emit('cmd_line_output',{"stdout":line})

worker = Thread(target=relayStdOut, daemon=True)
worker.start()

def getStatus():
    """ Helper Function to get status
    """
    status = []
    global proc
    if proc is None:
        status.append("No recording running")
    else:
        retcode = proc.poll()
        if retcode is None:
            status.append("recording ongoing")
        else:
            status.append("recording stopped with returncode {}".format(retcode))
        return status


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
    proc = Popen(cmd, env=env, stdout=PIPE, stderr=STDOUT, text=True)
    # get immediate status
    status = getStatus()
    return make_response(jsonify({"status":"started recording", "filename":filename, "status":status,"pid":proc.pid,"args":proc.args}))

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
    status = getStatus()
    return make_response(jsonify({"status":status}))

