#!flask/bin/python

import requests
from flask import Flask
from flask import request
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


# creating and saving some models
from csv_detective_ml.prediction import get_columns_prediction, get_columns_types

# reg_model = linear_model.LinearRegression()
# reg_model.fit([[1., 1., 5.], [2., 2., 5.], [3., 3., 1.]], [0., 0., 1.])
# pickle.dump(reg_model, open('some_model.pkl', 'wb'))

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

    y_pred, csv_info = get_columns_prediction("03c24270-75ac-4a06-9648-44b6b5a5e0f7.csv")
    dict_columns = get_columns_types(y_pred, csv_info)


    # prediction = ML_PIPELINE.predict([[feature1, feature2, feature3]])
    # return str(prediction)
    return




if __name__ == '__main__':
    pass
    # if os.environ['ENVIRONMENT'] == 'production':
    #     app.run(port=80, host='0.0.0.0')
    # if os.environ['ENVIRONMENT'] == 'local':
    #     app.run(port=5000, host='0.0.0.0')

