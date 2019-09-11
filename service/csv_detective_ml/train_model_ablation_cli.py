'''Loads an annotated file and extracts features and tagged types for each resource id

Usage:
    train_model.py <i> <p> <m> [options]

Arguments:
    <i>                                An input file or directory (if dir it will convert all txt files inside).
    <p>                                Path where to find the resource's CSVs
    <m>                                Path where to save the trained pipeline [default: "models/"]
    --num_files NFILES                 Number of files (CSVs) to work with [default: 10:int]
    --num_rows NROWS                   Number of rows per file to use [default: 200:int]
    --cores=<n> CORES                  Number of cores to use [default: 2:int]
    --train_size TRAIN                 Percentage for training . If 1.0, then no testing is done [default: 0.7:float]
'''
import json
from argopt import argopt
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer, HashingVectorizer
from sklearn.metrics import f1_score
from sklearn.pipeline import Pipeline, FeatureUnion
from tqdm import tqdm
from xgboost import XGBClassifier

from features import ItemSelector, CustomFeatures, ColumnInfoExtractor

# from prediction import PredictColumnInfoExtractor
# from service.csv_detective_ml.utils import header_tokenizer

if __name__ == '__main__':
    parser = argopt(__doc__).parse_args()
    tagged_file_path = parser.i
    csv_folder_path = parser.p
    output_model_path = parser.m
    num_files = parser.num_files
    num_rows = parser.num_rows
    train_size = parser.train_size
    n_cores = int(parser.cores)

    pipeline = Pipeline([
        # Extract column info information from csv

        # Use FeatureUnion to combine the features from subject and body
        ('union', FeatureUnion(
            transformer_list=[

                # Pipeline for custom hand-crafted features for cell values
                ('custom_features', Pipeline([
                    ('selector', ItemSelector(key='per_file_rows')),
                    ("customvect", DictVectorizer())
                ])),
                #
                # Pipeline for standard bag-of-words features for cell values
                ('cell_features', Pipeline([
                    ('selector', ItemSelector(key='all_columns')),
                    ('count', TfidfVectorizer(ngram_range=(1, 3), analyzer="char_wb", binary=False, max_features=2000)),
                ])),

                # Pipeline for standard bag-of-words models for header values
                ('header_features', Pipeline([
                    ('selector', ItemSelector(key='all_headers')),
                    # ('count', TfidfVectorizer(ngram_range=(4, 4), analyzer="char_wb",
                    #                           binary=False, max_features=2000)),
                    ('hash', HashingVectorizer(n_features=2 ** 2, ngram_range=(3, 3), analyzer="char_wb")),

                ])),

            ],

            # weight components in FeatureUnion
            transformer_weights={
                'custom_features': 1.6,
                'cell_features': 1,
                'header_features': .3,
            },

        )),

        # Use a SVC classifier on the combined features
        ('XG', XGBClassifier(n_jobs=n_cores)),
        # ("MLP", MLPClassifier((512, ))),
        # ("LR", LogisticRegression(n_jobs=n_cores, solver="liblinear", multi_class="auto", class_weight="balanced")),

    ])

    features_dict = {0: ('custom_features', Pipeline([
        ('selector', ItemSelector(key='per_file_rows')),
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

    train, test = ColumnInfoExtractor(n_files=num_files, n_rows=num_rows, train_size=train_size,
                                      n_jobs=n_cores, column_sample=True).transform(
        annotations_file=tagged_file_path,
        csv_folder=csv_folder_path)

    tqdm.write("Loading data done...")
    ablation_results = {}
    for pp_name, pp in tqdm(all_pipelines.items()):
        tqdm.write(f"Fitting pipeline {pp_name}")
        pp.fit(train, train["y"])
        y_test = test["y"]
        y_pred = pp.predict(test)
        f_score = f1_score(y_true=y_test, y_pred=y_pred, average='macro')
        ablation_results[pp_name] = f_score

    json.dump(ablation_results, "./data/ablation_results.json")
