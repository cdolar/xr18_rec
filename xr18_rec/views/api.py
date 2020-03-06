from flask import Blueprint
from flask import current_app as app

api = Blueprint("api", __name__)

proc = None

@api.route("/rec")
def rec():
    filename = datetime.now().strftime('%Y-%m-%d--%H-%M-%S__xr18rec.wav')
    audiodev = "hw:X18XR18,0"
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
    proc = Popen(cmd, env=env)

@api.route("/stop")
def stop():
    if proc is None:
        print("No recording running to stop")
    else:
        retcode = proc.poll()
        if retcode is None:
            print("recording ongoing, terminating it")
            proc.terminate()
        else:
            print("recording stopped with returncode {}".format(retcode))

@api.route("/status")
def status():
    if proc is None:
        print("No recording running")
    else:
        retcode = proc.poll()
        if retcode is None:
            print("recording ongoing")
        else:
            print("recording stopped with returncode {}".format(retcode))
