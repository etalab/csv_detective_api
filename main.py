#!flask/bin/python
import os

from flask import Flask
from flask import request
from flask import jsonify
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())



app = Flask(__name__)


@app.route('/isAlive')
def index():
    return "true"


@app.route('/csv_detective', methods=['GET'])
def get_prediction():
    global CSV_INFO
    try:
        resource_id = request.args.get('resource_id')
        if resource_id in CSV_INFO:
            return jsonify(CSV_INFO[resource_id])
        else:
            logger.info("Resource id not found in 'database'.")
            return jsonify({"not_found": True})
    except:
        return "Send some value as resource_id"


if __name__ == '__main__':
    # load csv_detective info json
    CSV_INFO = {}
    try:
        with open("csv_data.json", "r") as filo:
            logger.info("Loading JSON file with csv info...")
            CSV_INFO = json.load(filo)
    except FileNotFoundError as fn:
        logger.error("JSON data file not found.".format(fn))
        raise

    if os.environ['ENVIRONMENT'] == 'production':
        app.run(port=80, host='0.0.0.0')
    if os.environ['ENVIRONMENT'] == 'local':
        app.run(port=5000, host='0.0.0.0')
