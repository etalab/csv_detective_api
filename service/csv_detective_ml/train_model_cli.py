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
# import logging
import joblib
from argopt import argopt
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, HashingVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline, FeatureUnion
from xgboost import XGBClassifier

# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler())
from features import ItemSelector, CustomFeatures, ColumnInfoExtractor
# from prediction import PredictColumnInfoExtractor
from service.csv_detective_ml.utils import header_tokenizer

if __name__ == '__main__':
    parser = argopt(__doc__).parse_args()
    tagged_file_path = parser.i
    csv_folder_path = parser.p
    output_model_path = parser.m
    num_files = parser.num_files
    num_rows = parser.num_rows
    train_size = parser.train_size
    n_cores = int(parser.cores)

    # from csv_detective.explore_csv import routine
    # foo = routine("../03c24270-75ac-4a06-9648-44b6b5a5e0f7.csv", num_rows=100)

    pipeline = Pipeline([
        # Extract column info information from csv

        # Use FeatureUnion to combine the features from subject and body
        ('union', FeatureUnion(
            transformer_list=[

                # Pipeline for pulling custom features from the columns
                ('custom_features', Pipeline([
                    ('selector', ItemSelector(key='per_file_rows')),
                    ('customfeatures', CustomFeatures(n_jobs=n_cores)),
                    ("customvect", DictVectorizer())
                ])),
                #
                # Pipeline for standard bag-of-words models for cell values
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

    # try:
    train, test = ColumnInfoExtractor(n_files=1000, n_rows=300, train_size=.80,
                                            n_jobs=n_cores, column_sample=True).transform(
             annotations_file="./csv_detective_ml/data/distant_human_supervised_all.csv",
             csv_folder="/data/datagouv/datagouv_full")
    # except Exception as e:
    #     print("Error", e)
    #     test_distant = None

    # train, test = ColumnInfoExtractor(n_files=num_files, n_rows=num_rows, train_size=train_size,
    #                                   n_jobs=n_cores).transform(annotations_file=tagged_file_path,
    #                                                             csv_folder=csv_folder_path)

    pipeline.fit(train, train["y"])
    if test is not None:
        y_test = test["y"]
        y_pred = pipeline.predict(test)
        print(classification_report(y_test, y_pred=y_pred))

    # if test_distant is not None:
    #     print("\n\nTEST DISTANT\n\n")
    #     y_test = test_distant["y"]
    #     y_pred = pipeline.predict(test_distant)
    #     print(classification_report(y_test, y_pred=y_pred))

    # Save pipeline
    joblib.dump(pipeline, output_model_path + '/model.joblib')

    # from prediction import PredictColumnInfoExtractor
    #
    # ext = PredictColumnInfoExtractor()
    # foo = ext.transform("../03c24270-75ac-4a06-9648-44b6b5a5e0f7.csv")
    # y_pred = pipeline.predict(foo)
    # print(y_pred)
    # pass
