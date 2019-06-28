# import os
from collections import defaultdict

from sklearn.base import BaseEstimator, TransformerMixin
from csv_detective.detection import detect_encoding, detect_separator, detect_headers, parse_table
import numpy as np
import features


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
        try:
            table, total_lines = parse_table(
                file_path,
                encoding,
                sep,
                header_row_idx,
                n_rows,
                random_state=42
            )
        except Exception as e:
            return
        if table.empty:
            print("Could not read {}".format(file_path))
            return
        return table

    def _extract_columns(self, file_path):

        csv_df = self._load_file(file_path=file_path, n_rows=self.n_rows)

        if csv_df is None:
            return {"error": "Could not read file with pandas"}

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
        datasets_info = {"all_columns": rows_values, "all_headers": columns_names, "per_file_rows": [file_columns],
                         "headers": list(csv_df.columns)}

        return datasets_info

    def transform(self, csv_path):
        columns_info = self._extract_columns(csv_path)
        return columns_info


def get_columns_ML_prediction(csv_path, pipeline, num_rows=500):
    ext = PredictColumnInfoExtractor(num_rows=num_rows)
    csv_info = ext.transform(csv_path)
    if not csv_info:
        # logger.error("Could not read {}".format(csv_path))
        return

    y_pred = pipeline.predict(csv_info)
    return y_pred, csv_info


def get_columns_types(y_pred, csv_info):
    def get_most_frequent(list_predictions):
        u, counts = np.unique(list_predictions, return_counts=True)
        return u[0]

    from collections import OrderedDict
    num_columns = [len(f) for f in csv_info["per_file_rows"]][0]
    assert (len(y_pred) == len(csv_info["all_headers"]))
    dict_columns = defaultdict(list)
    head_pred = list(zip(csv_info["all_headers"], y_pred))
    for header in csv_info["headers"]:
        per_head_predictions = [f[1] for f in head_pred if f[0] == header.lower()]
        if not per_head_predictions:
            continue
        else:
            most_freq_label = get_most_frequent(per_head_predictions)
            if most_freq_label == "O":
                continue
            dict_columns[header].append(most_freq_label)
    return dict_columns


# y_pred, csv_info = get_columns_prediction("03c24270-75ac-4a06-9648-44b6b5a5e0f7.csv")
# dict_columns = get_columns_types(y_pred, csv_info)
pass
