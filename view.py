from flask import Flask, render_template, redirect, session, request
from flask_apscheduler import APScheduler
import os
import sys
from StreamManager import StreamManager
from OutManager import OutManager
from flask_apscheduler import APScheduler

class Config:
    SCHEDULER_API_ENABLED = True
    PREFERRED_URL_SCHEME = 'http'

app = Flask(__name__)
app.config.from_object(Config())

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

streammanager = StreamManager()
outmanager = OutManager()

@scheduler.task('interval', id='do_job_1', seconds=3, misfire_grace_time=900)
def job1():
    streammanager.UpdateStates()

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/out")
def out():
    return render_template('out.html')

@app.route("/getdevices")
def getdevices():
    try:
        return streammanager.GetAudioDevices()
    except:
        return {}

@app.route("/getoutdevices")
def getoutdevices():
    try:
        return outmanager.GetAudioDevices()
    except:
        return {}

@app.route("/getstates")
def getstates():
    try:
        return streammanager.GetAllStates()
    except:
        return {}

@app.route("/getoutstates")
def getoutstates():
    try:
        return outmanager.GetAllStates()
    except:
        return {}

@app.route("/stop/<uid>")
def stop(uid):
    try:
        return streammanager.StopStreaming(int(uid))
    except:
        return {}

@app.route("/stopout/<uid>")
def stopout(uid):
    try:
        return outmanager.StopStreaming(int(uid))
    except:
        return {}

@app.route("/startstream", methods=['POST'])
def startrec():
    if request.method == 'POST':
        info = request.get_json(silent=True)
        url = info['url']
        device = int(info['device'])
        devicename = info['devicename']
        try:
            if url[:4] != 'http':
                url = "http://" + url
        except:
            return {'uid': 0}
        uid = streammanager.StartStreaming(url, device, devicename)
        return {'uid': uid}
    
@app.route("/startout", methods=['POST'])
def startout():
    if request.method == 'POST':
        info = request.get_json(silent=True)
        url = info['url']
        device = int(info['device'])
        devicename = info['devicename']
        uid = outmanager.StartStreaming(url, device, devicename)
        return {'uid': uid}

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5010))
    print("Starting server on port " + str(port) , file=sys.stderr)
    app.run(debug=False, host='0.0.0.0', port=port)