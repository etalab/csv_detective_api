# parsers.py
from werkzeug.datastructures import FileStorage
from flask_restplus import reqparse

file_upload = reqparse.RequestParser()
file_upload.add_argument('resource_csv',
                         type=FileStorage,
                         location='files',
                         required=True,
                         help='CSV file')