from flask import Flask, render_template, jsonify, request
import threading
import requests
import time
import numpy as np
from dependencies.parse_config_file import parseConfigFile

app = Flask(__name__)

# Global variables to control the start/stop of API calls and to store the API URL and data
fetching = False
api_thread = None
api_url = ''
latest_data = {}

cf = parseConfigFile("config_files/spot_3.cfg", Rx_Ant=4, Tx_Ant=2)
rangeArray = np.array(range(cf["numRangeBins"])) * cf["rangeIdxToMeters"]


def fetch_api_data():
    global fetching, api_url, latest_data
    while fetching:
        response = requests.get(api_url)
        data = response.json()
        data['Range_Array'] = rangeArray.tolist()
        latest_data = data
        time.sleep(2)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start', methods=['POST'])
def start():
    global fetching, api_thread, api_url
    if not fetching:
        fetching = True
        api_url = request.json.get('api_url')  # Get the API URL from the request
        api_thread = threading.Thread(target=fetch_api_data)
        api_thread.start()
    return jsonify({'status': 'started'})


@app.route('/stop', methods=['POST'])
def stop():
    global fetching
    fetching = False
    if api_thread is not None:
        api_thread.join()
    return jsonify({'status': 'stopped'})


@app.route('/latest-data', methods=['GET'])
def latest_data_route():
    return jsonify(latest_data)


if __name__ == '__main__':
    app.run(debug=True)
