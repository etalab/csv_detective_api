
"""
Here we train a machine learning models to detect the type of column. We need :
1. Load the annotation csv /home/pavel/etalab/code/csv_true_detective/data/columns_annotation.csv
    a. Get the filenames found in this file
2. Start csv_detective routine for each filename
3. Get the
"""
import random
import string
from collections import Counter
# from csv_detective.machine_learning.train_model_cli import RESOURCE_ID_COLUMNS
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.feature_selection import RFE
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.tree import ExtraTreeClassifier
from sklearn.svm import SVC
from scipy.sparse import vstack, hstack
from xgboost import XGBClassifier

from csv_detective.machine_learning import logger

import numpy as np
import pandas as pd



def get_sparsity(matrix):
    return matrix.nnz / (matrix.shape[0] * matrix.shape[1])


def extra_features(columns, labels):
    labels = labels
    list_features = []
    is_float = lambda x: x.replace('.','',1).isdigit() and "." in x
    for j, rows in enumerate(columns):
        numeric_col = np.array([float(f) for f in rows if f.isdigit()], dtype=float)

        for i, value in enumerate(rows):
            # Add column features if existent
            if len(numeric_col):
                features = {"num_unique": len(np.unique(numeric_col)),
                            "col_sum": 1 if sum(numeric_col) < len(numeric_col) else 0}

            else:
                features = {}
            #
            # features = {}

            # if j > 0:
            #     column_prev = columns[j - 1][:]
            #     # np.random.shuffle(column_prev)
            #     features[str(hash("".join(column_prev)) % (10 ** 2))] = 1
            # elif j + 1 < len(columns):
            #     column_next = columns[j + 1][:]
            #     # np.random.shuffle(column_next)
            #     features[str(hash("".join(column_next)) % (10 ** 2))] = 1

            columns_copy = columns[j][:]
            np.random.shuffle(columns_copy)

            # features[str(hash("".join(columns_copy)) % (10 ** 3))] = 1

            features["is_numeric"] = 1 if value.isnumeric() or is_float(value) else 0
            # features["single_char"] = 1 if len(value.strip()) == 1 else 0
            if features["is_numeric"]:
                try:
                    numeric_value = int(value)
                except:
                    numeric_value = float(value)

                if numeric_value < 0:
                    features["<0"] = 1
                if 0 <= numeric_value < 2:
                    features[">=0<2"] = 1
                elif 2 <= numeric_value < 500:
                    features[">=2<500"] = 1
                elif 500 <= numeric_value < 1000:
                    features[">=500<1000"] = 1
                elif 1000 <= numeric_value < 10000:
                    features[">=1k<10k"] = 1
                elif 10000 <= numeric_value:
                    features[">=10k<100k"] = 1

            # num lowercase
            features["num_lower"] = sum(1 for c in value if c.islower())

            # num uppercase
            features["num_upper"] = sum(1 for c in value if c.isupper())


            # num chars
            features["num_chars"] = len(value)

            # num numeric
            features["num_numeric"] = sum(1 for c in value if c.isnumeric())

            # num alpha
            features["num_alpha"] = sum(1 for c in value if c.isalpha())

            # num distinct chars
            features["num_unique_chars"] = len(set(value))

            # num white spaces
            # features["num_spaces"] = value.count(" ")

            # num of special chars
            features["num_special_chars"] = sum(1 for c in value if c in string.punctuation)

            list_features.append(features)

    return list_features



def features_cell(rows, labels):

    list_features = []
    is_float = lambda x: x.replace('.','',1).isdigit() and "." in x

    for i, value in enumerate(rows):
        features = {}
        value = value.replace(" ", "")
        features["is_numeric"] = 1 if value.isnumeric() or is_float(value) else 0
        # features["single_char"] = 1 if len(value.strip()) == 1 else 0
        if features["is_numeric"]:
            try:
                numeric_value = int(value)
            except:
                numeric_value = float(value)

            if numeric_value < 0:
                features["<0"] = 1
            if 0 <= numeric_value < 2:
                features[">=0<2"] = 1
            elif 2 <= numeric_value < 1000:
                features[">=2<1000"] = 1
            elif 1000 <= numeric_value < 10000:
                features[">=1k<10k"] = 1
            elif 10000 <= numeric_value:
                features[">=10k<100k"] = 1

        # "contextual" features

        # if i > 0:
        #     features["is_numeric-1"] = 1 if rows[i-1].isnumeric() or is_float(rows[i-1]) else 0
        #     features["num_chars_-1"] = len(rows[i-1])
        #     if i > 1:
        #         features["is_numeric-2"] = 1 if rows[i-2].isnumeric() or is_float(rows[i-2]) else 0
        #         features["num_chars_-2"] = len(rows[i-2])
        # if i <= len(rows) - 2:
        #     features["is_numeric+1"] = 1 if rows[i+1].isnumeric() or is_float(rows[i+1]) else 0
        #     features["num_chars_+1"] = len(rows[i+1])
        #     if i <= len(rows) - 3:
        #         features["is_numeric+2"] = 1 if rows[i+2].isnumeric() or is_float(rows[i+2]) else 0
        #         features["num_chars_+2"] = len(rows[i+2])



        # num lowercase
        features["num_lower"] = sum(1 for c in value if c.islower())

        # num uppercase
        features["num_upper"] = sum(1 for c in value if c.isupper())


        # num chars
        features["num_chars"] = len(value)

        # num numeric
        features["num_numeric"] = sum(1 for c in value if c.isnumeric())

        # num alpha
        features["num_alpha"] = sum(1 for c in value if c.isalpha())

        # num distinct chars
        features["num_unique_chars"] = len(set(value))

        # num white spaces
        features["num_spaces"] = value.count(" ")

        # num of special chars
        features["num_special_chars"] = sum(1 for c in value if c in string.punctuation)

        list_features.append(features)

    return list_features



def features_column_wise(column:pd.Series):
    """Extract features of the column (np.array)

    """

    features = {}

    column = column.dropna()
    if column.empty:
        return {"empty_column": 1}


    # number of chars
    features["length_avg"] = np.mean(column.apply(len))
    features["length_min"] = np.min(column.apply(len))
    features["length_max"] = np.max(column.apply(len))
    features["length_std"] = np.std(column.apply(len))

    # type of chars
    features["chars_num_unique"] = len(Counter(column.to_string(header=False, index=False).replace("\n", "").replace(" ", "")))
    features["chars_avg_num_digits"] = np.mean(column.apply(lambda x: sum(1 for c in x if c.isdigit())))
    features["chars_avg_num_letters"] = np.mean(column.apply(lambda x: sum(1 for c in x if c.isalpha())))
    features["chars_avg_num_lowercase"] = np.mean(column.apply(lambda x: sum(1 for c in x if c.islower())))
    features["chars_avg_num_uppercase"] = np.mean(column.apply(lambda x: sum(1 for c in x if c.isupper())))

    features["values_nunique"] = column.nunique()
    return features


def train_model(list_features_dict, y_true):
    dv = DictVectorizer(sparse=False)
    X = dv.fit_transform(list_features_dict)
    sss = StratifiedShuffleSplit(n_splits=1, test_size=0.3, random_state=42)

    indices = list(sss.split(X, y_true))
    train_indices, test_indices = indices[0][0], indices[0][1]

    X_train, X_test = X[train_indices], X[test_indices]
    y_train, y_test = y_true[train_indices], y_true[test_indices]

    clf = LogisticRegression()
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    print(classification_report(y_true=y_test, y_pred=y_pred))


def show_confusion_matrix(y_true, y_pred, labels):
    import seaborn as sns
    import matplotlib.pyplot as plt

    cm = confusion_matrix(y_true=y_true, y_pred=y_pred, labels=np.unique(y_true))

    ax = plt.subplot()
    sns.heatmap(cm, annot=True, ax=ax, fmt="g")  # annot=True to annotate cells

    # labels, title and ticks
    ax.set_xlabel('Predicted labels')
    ax.set_ylabel('True labels')
    ax.set_title('Confusion Matrix')
    ax.xaxis.set_ticklabels(labels, rotation=90)
    ax.yaxis.set_ticklabels(labels, rotation=0)
    plt.show()


def explain_parameters(clf:LogisticRegression, label_id, vectorizers, features_names, n_feats=10):

    if len(vectorizers) > 1:
        features = np.array(vectorizers[0].get_feature_names() + vectorizers[1].get_feature_names())
    else:
        features = np.array(vectorizers[0].get_feature_names())

    top_coefs_ids = clf.coef_[label_id].argsort()[::-1][:10]
    bottom_coefs_ids = clf.coef_[label_id].argsort()[:10][::-1]

    # top_coefs_feats = features[top_coefs_ids]
    # bottom_coefs_feats = features[bottom_coefs_ids]

    top_bottom_ids = list(top_coefs_ids) + list(bottom_coefs_ids)
    top_bottom_weights = clf.coef_[label_id][top_bottom_ids]
    top_bottom_feats = features[top_bottom_ids]

    for w, f in zip(top_bottom_weights, top_bottom_feats):
        logger.info("{0}:{1}".format(w, f))
    pass


def lime_explanation(clf, X_train, X_test, y_train, y_test, feature_names):
    from lime.lime_tabular import LimeTabularExplainer

    class_names = np.unique(y_train)
    explainer = LimeTabularExplainer(training_data=X_train.todense(), mode="classification", training_labels=y_train,
                                     feature_names=feature_names, class_names=class_names,
                                     discretize_continuous=False)

    bools_ids = np.where(y_test == "booleen")[0]


    print(bools_ids[0])
    exp = explainer.explain_instance(data_row=X_test[bools_ids[0]].A[0], predict_fn=clf.predict_proba,
                                     num_features=6, labels=[0, 3])

    print('Explanation for class %s' % class_names[0])
    print('\n'.join(map(str, exp.as_list(label=0))))
    print()
    print('Explanation for class %s' % class_names[3])
    print('\n'.join(map(str, exp.as_list(label=3))))

    pass


def train_model2(X, y_true, vectorizers):

    sss = StratifiedShuffleSplit(n_splits=1, test_size=0.3, random_state=42)
    y_true = np.array(list(y_true))
    indices = list(sss.split(X, y_true))
    train_indices, test_indices = indices[0][0], indices[0][1]

    feature_names = vectorizers[0].get_feature_names()# + vectorizers[1].get_feature_names()

    X_train, X_test = X[train_indices], X[test_indices]
    y_train, y_test = y_true[train_indices], y_true[test_indices]

    # clf = SVC(kernel="linear")
    # clf = LogisticRegression(multi_class="ovr", n_jobs=-1, solver="lbfgs")
    # clf = HistGradientBoostingClassifier()
    # clf = MLPClassifier(hidden_layer_sizes=(100, 100), activation="relu")
    # clf = ExtraTreeClassifier(class_weight="balanced")
    clf = XGBClassifier(n_jobs=5)
    # clf = RandomForestClassifier(n_estimators=200, n_jobs=5, class_weight="balanced_subsample")
    # clf = SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, random_state=42, max_iter=5, tol=None)

    # rfe = RFE(estimator=clf, n_features_to_select=1, step=1)
    # rfe.fit(X_train, y_train)


    logger.info("Fitting a matrix with shape {0} and sparsity {1}".format(X_train.shape, get_sparsity(X_train)))
    clf.fit(X_train, y_train)
    # print(rfe.ranking_)
    # import pickle
    # pickle.dump(clf, open("clf_training", "wb"))
    # pickle.dump([X_train, y_train], open("xytrain", "wb"))
    y_pred = clf.predict(X_test)



    # lime_explanation(clf, X_train, X_test, y_train, y_test, feature_names)
    print(classification_report(y_true=y_test, y_pred=y_pred))
    # show_confusion_matrix(y_true=y_test, y_pred=y_pred, labels=np.unique(y_true))
    return clf


def explore_features(label, labels_rows, vectorizer, data_matrix):
    labels_rows = np.array(labels_rows)
    features = np.array(vectorizer.get_feature_names())

    label_ids = np.where(labels_rows == label)[0]
    nnz_features_ids = data_matrix[label_ids, :].nonzero()[1]


    nnz_features = features[nnz_features_ids]

    print(nnz_features)



def create_data_matrix(documents, columns_names, extra_features, labels):

    # Text from the cell value itself
    cell_cv = CountVectorizer(ngram_range=(1, 3), analyzer="char_wb", binary=False, max_features=2000)
    X_cell = cell_cv.fit_transform(documents)
    logger.info("Built cell matrix with shape {}".format(X_cell.shape))


    # Text from the header
    header_cv = CountVectorizer(ngram_range=(1, 3), analyzer="char")
    X_header = header_cv.fit_transform(columns_names)
    logger.info("Built header matrix with shape {}".format(X_header.shape))

    # Hand-crafted features
    extra_dv = DictVectorizer()
    X_extra = extra_dv.fit_transform(extra_features)
    logger.info("Built extra features matrix with shape {0}. Sparsity {1}".format(X_extra.shape, get_sparsity(X_extra)))

    # all_features = cell_cv.get_feature_names() + extra_dv.get_feature_names()

    X_all = hstack([X_extra], format="csr")

    logger.info("Built a matrix with shape {}".format(X_all.shape))

    # Explore
    # explore_features("booleen", features_cols=all_features, labels_rows=labels, data_matrix=X_all)

    return X_all, cell_cv, header_cv, extra_dv


if __name__ == '__main__':
    file_path = "/data/datagouv/csv_top/edf158f9-bdde-4e6e-b92c-c156c9316383.csv"

