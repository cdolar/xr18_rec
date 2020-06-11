import os, os.path
from subprocess import Popen, PIPE, TimeoutExpired, STDOUT
from datetime import datetime
from time import sleep, localtime
from glob import glob
from threading import Thread
from flask import Blueprint, jsonify, make_response, request, send_from_directory, abort
from flask import current_app as app
from flask_socketio import emit
from xr18_rec import socketio


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
        status.append("No recording/playback running")
    else:
        retcode = proc.poll()
        if retcode is None:
            status.append("recording/playback ongoing")
        else:
            status.append("recording/playback stopped with returncode {}".format(retcode))
        return status


@api.route("/rec")
def rec():
    filename = os.path.join("/media", "pi", "MUSIC2", datetime.now().strftime('%Y-%m-%d--%H-%M-%S__xr18rec.wav'))
    audiodev = request.args.get("audiodev")
    if audiodev is None:
        audiodev = "hw:X18XR18,0"
        #audiodev = "hw:CODEC,0"
    buffersize = 512*1024
    channels = 18
    bits = 32
    rate = 48000
    env = os.environ
    env['AUDIODEV']=audiodev
    cmd = [
        'rec',
        '--buffer={}'.format(buffersize),
        '-c {}'.format(channels),
        #'-b {}'.format(bits),
        #'-r {}'.format(rate),
        filename
    ]
    global proc
    if proc is not None:
        stop()
    proc = Popen(cmd, env=env, stdout=PIPE, stderr=STDOUT, text=True)
    # get immediate status
    status = getStatus()
    return make_response(
        jsonify(
            {
                "status":"started recording",
                "filename":filename,
                "status":status,
                "pid":proc.pid,
                "args":proc.args,
                "audiodev":audiodev
            }
        )
    )


@api.route("/stop")
def stop():
    global proc
    status = ""
    if proc is None:
        status = "No recording running to stop"
    else:
        retcode = proc.poll()
        if retcode is None:
            status = "recording/playback ongoing, terminating it"
            proc.terminate()
        else:
            status = "recording/playback stopped with returncode {}".format(retcode)
    return make_response(jsonify({"status":status}))


@api.route("/status")
def status():
    status = getStatus()
    return make_response(jsonify({"status":status}))


@api.route("/files")
def get_files():
    curr_dir = os.getcwd()
    os.chdir(os.path.join("/media","pi","MUSIC2"))
    files = sorted(glob("*.wav"))
    filedata = {"files":[]}
    for f in files:
        filedata["files"].append({"filename": f, "creation_time": localtime(os.path.getctime(f))})
    os.chdir(curr_dir)
    return make_response(jsonify(filedata))


@api.route("/play/<filename>")
def play(filename):
    audiodev = request.args.get("audiodev")
    if audiodev is None:
        audiodev = "hw:X18XR18,0"
        #audiodev = "hw:CODEC,0"
    buffersize = 8*1024
    channels = 18
    bits = 24
    rate = 48000
    env = os.environ
    env['AUDIODEV']=audiodev
    cmd = [
        'play',
        '--buffer={}'.format(buffersize),
        '-c {}'.format(channels),
        #'-b {}'.format(bits),
        #'-r {}'.format(rate),
        os.path.join("/media","pi","MUSIC2",filename)
    ]
    global proc
    if proc is not None:
        stop()
    proc = Popen(cmd, env=env, stdout=PIPE, stderr=STDOUT, text=True)
    # get immediate status
    status = getStatus()
    return make_response(
        jsonify(
            {
                "status":"started playback", 
                "filename":filename, 
                "status":status,
                "pid":proc.pid,
                "args":proc.args,
                "audiodev":audiodev
            }
        )
    )

@api.route("/download/<filename>")
def download(filename):
    print(filename)
    try:
        return send_from_directory(os.path.join("/media","pi","MUSIC2"), filename=filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

