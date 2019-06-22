#!flask/bin/python
import os

import requests
from flask import Flask
from flask import request

# creating and saving some models
from prediction import PredictColumnInfoExtractor

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

    # prediction = ML_PIPELINE.predict([[feature1, feature2, feature3]])
    return str(prediction)




if __name__ == '__main__':
    ext = PredictColumnInfoExtractor()
    foo = ext.transform("55cd803a-998d-4a5c-9741-4cd0ee0a7699.csv")

    pass

    # if os.environ['ENVIRONMENT'] == 'production':
    #     app.run(port=80, host='0.0.0.0')
    # if os.environ['ENVIRONMENT'] == 'local':
    #     app.run(port=5000, host='0.0.0.0')

