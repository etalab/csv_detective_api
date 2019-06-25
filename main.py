#!flask/bin/python

import requests
from flask import Flask
from flask import request
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


# load csv_detective info json

app = Flask(__name__)



@app.route('/isAlive')
def index():
    return "true"


@app.route('/prediction/api/v1.0/csv_detective', methods=['GET'])
def get_prediction():
    resource_id = float(request.args.get('resource_id'))
    resource_url = "here some url"
    r = requests.get(resource_url, allow_redirects=True, timeout=5)
    resource_content = r.content



    # prediction = ML_PIPELINE.predict([[feature1, feature2, feature3]])
    # return str(prediction)
    return




if __name__ == '__main__':
    pass
    # if os.environ['ENVIRONMENT'] == 'production':
    #     app.run(port=80, host='0.0.0.0')
    # if os.environ['ENVIRONMENT'] == 'local':
    #     app.run(port=5000, host='0.0.0.0')

