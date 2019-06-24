# import os
import pickle
from collections import defaultdict

import joblib
from joblib import Parallel, delayed
from sklearn.base import BaseEstimator, TransformerMixin
from csv_detective.detection import detect_encoding, detect_separator, detect_headers, parse_table
import pandas as pd
from tqdm import tqdm
import numpy as np
from csv_detective_ml_train import  features

ML_PIPELINE = joblib.load('../models/model.joblib')



class PredictColumnInfoExtractor(BaseEstimator, TransformerMixin):
    """Extract the subject & body from a usenet post in a single pass.

    Takes a sequence of strings and produces a dict of sequences.  Keys are
    `subject` and `body`.
    """

    def __init__(self, n_rows=200, n_jobs=1, save_dataset=False):

        self.n_rows = n_rows
        self.n_jobs = n_jobs
        self.save_dataset = save_dataset
        self._file_idx = {}

    def fit(self, X, y=None):
        return self

    def _load_file(self, file_path, n_rows):
        with open(file_path, mode='rb') as binary_file:
            encoding = detect_encoding(binary_file)['encoding']

        with open(file_path, 'r', encoding=encoding) as str_file:
            sep = detect_separator(str_file)
            header_row_idx, header = detect_headers(str_file, sep)
            if header is None:
                return_dict = {'error': True}
                return return_dict
            elif isinstance(header, list):
                if any([x is None for x in header]):
                    return_dict = {'error': True}
                    return return_dict

        table, total_lines = parse_table(
            file_path,
            encoding,
            sep,
            header_row_idx,
            n_rows,
            random_state=42
        )

        if table.empty:
            print("Could not read {}".format(file_path))
            return
        return table

    def _extract_columns(self, file_path):

        csv_df = self._load_file(file_path=file_path, n_rows=self.n_rows)

        if csv_df is None:
            return None

        file_columns = []
        columns_names = []
        for j in range(len(csv_df.columns)):
            # Get all values of the column j and clean it a little bit
            temp_list = csv_df.iloc[:, j].dropna().apply(lambda x: x.replace(" ", "")).to_list()
            file_columns.append(temp_list)
            columns_names.extend([csv_df.columns[j].lower()] * len(temp_list))

            rows_values = []

        # Get both lists of labels and values-per-column in a single flat huge list
        for i in range(csv_df.shape[1]):
            rows_values.extend(file_columns[i])

        assert len(rows_values) == len(columns_names)
        datasets_info = {"all_columns": rows_values, "all_headers": columns_names, "per_file_rows": [file_columns]}

        return datasets_info

    def _extract_columns_selector(self, csv_path):
        """
        Choses the path of execution, either parallel or single core
        :param csv_folder:
        :return:
        """
        csv_info = self._extract_columns(csv_path)

        return csv_info

    def transform(self, csv_path):
        columns_info = self._extract_columns_selector(csv_path)
        return columns_info


def detect_columns_types(csv_path):
    ext = PredictColumnInfoExtractor()
    foo = ext.transform(csv_path)
    y_pred = ML_PIPELINE.predict(foo)
    print(y_pred)
    pass

# detect_columns_types("../03c24270-75ac-4a06-9648-44b6b5a5e0f7.csv")
pass