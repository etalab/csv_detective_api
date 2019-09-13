'''Trains and tests a model with different set of features to determine their importance

Usage:
    train_model.py <train> <test> <p> <m> [options]

Arguments:
    <train>                            An input file with the training set data
    <test>                             An input file with the testing set data
    <p>                                Path where to find the resource's CSVs
    <m>                                Path where to save the trained pipeline [default: "models/"]
    --num_files NFILES                 Number of files (CSVs) to work with [default: 10:int]
    --num_rows NROWS                   Number of rows per file to use [default: 200:int]
    --cores=<n> CORES                  Number of cores to use [default: 2:int]
'''
import json
from collections import defaultdict

import numpy as np
from argopt import argopt
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer, HashingVectorizer
from sklearn.metrics import f1_score, confusion_matrix
from sklearn.pipeline import Pipeline, FeatureUnion
from tqdm import tqdm
from xgboost import XGBClassifier

from features import ItemSelector, CustomFeatures, ColumnInfoExtractor

# from prediction import PredictColumnInfoExtractor
# from service.csv_detective_ml.utils import header_tokenizer

if __name__ == '__main__':
    parser = argopt(__doc__).parse_args()
    train_file_path = parser.train
    test_file_path = parser.test
    csv_folder_path = parser.p
    output_model_path = parser.m
    num_files = parser.num_files
    num_rows = parser.num_rows
    train_size = parser.train_size
    n_cores = int(parser.cores)

    features_dict = {0: ('custom_features', Pipeline([
        ('selector', ItemSelector(key='per_file_rows')),
        ('customfeatures', CustomFeatures(n_jobs=n_cores)),
        ("customvect", DictVectorizer())])),
                     1: ('cell_features', Pipeline([
                         ('selector', ItemSelector(key='all_columns')),
                         ('count', TfidfVectorizer(ngram_range=(1, 3), analyzer="char_wb",
                                                   binary=False, max_features=2000))])),
                     2: ('header_features', Pipeline([
                         ('selector', ItemSelector(key='all_headers')), ('hash',
                                                                         HashingVectorizer(n_features=2 ** 2,
                                                                                           ngram_range=(3, 3),
                                                                                           analyzer="char_wb"))]))}
    all_pipelines = {

        "custom_features": Pipeline([('union', FeatureUnion(transformer_list=[features_dict[0]])),
                                     ('XG', XGBClassifier(n_jobs=n_cores))]),

        "cell_features": Pipeline([('union', FeatureUnion(transformer_list=[features_dict[1]])),
                                   ('XG', XGBClassifier(n_jobs=n_cores))]),

        "header_features": Pipeline([('union', FeatureUnion(transformer_list=[features_dict[2]])),
                                     ('XG', XGBClassifier(n_jobs=n_cores))]),

        "custom_cell": Pipeline([('union', FeatureUnion(transformer_list=[features_dict[0], features_dict[1]])),
                                 ('XG', XGBClassifier(n_jobs=n_cores))]),

        "custom_header": Pipeline([('union', FeatureUnion(transformer_list=[features_dict[0], features_dict[2]])),
                                   ('XG', XGBClassifier(n_jobs=n_cores))]),

        "cell_header": Pipeline([('union', FeatureUnion(transformer_list=[features_dict[1], features_dict[2]])),
                                 ('XG', XGBClassifier(n_jobs=n_cores))]),

        "custom_cell_header": Pipeline([('union', FeatureUnion(transformer_list=[features_dict[0],
                                                                                 features_dict[1], features_dict[2]])),
                                        ('XG', XGBClassifier(n_jobs=n_cores))])
    }

    train, _ = ColumnInfoExtractor(n_files=num_files, n_rows=num_rows, train_size=1.,
                                      n_jobs=n_cores, column_sample=True).transform(
        annotations_file=train_file_path,
        csv_folder=csv_folder_path)

    test, _ = ColumnInfoExtractor(n_files=num_files, n_rows=num_rows, train_size=1.,
                                      n_jobs=n_cores, column_sample=True).transform(
        annotations_file=test_file_path,
        csv_folder=csv_folder_path)

    tqdm.write("Loading data done...")
    ablation_results = defaultdict(dict)
    for pp_name, pp in tqdm(all_pipelines.items()):
        tqdm.write(f"Fitting pipeline {pp_name}")
        pp.fit(train, train["y"])
        y_test = test["y"]
        y_pred = pp.predict(test)
        f_score = f1_score(y_true=y_test, y_pred=y_pred, average='macro')
        ablation_results[pp_name]["f_score"] = f_score
        ablation_results[pp_name]["confusion_matrix"] = str(confusion_matrix(y_true=y_test, y_pred=y_pred))
    ablation_results["tags"] = list(np.unique(test["y"]))
    json.dump(ablation_results, open("./data/ablation_results.json", "w"))
