import pandas as pd
import numpy as np
import json

from utils import get_files, extract_id
from sklearn.cluster import DBSCAN, KMeans
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from itertools import chain



def extract_columns(csv_path, encoding, separator):
    try:
        df = pd.read_csv(csv_path, encoding=encoding, sep=separator)
        return list(df.columns)
    except Exception as e:
        print(e)
        print("\t{}".format(csv_path))
        return []

def cluster_data(list_headers):
    vect = CountVectorizer(ngram_range=(1,4), analyzer="char", lowercase=True, strip_accents="unicode")
    X = vect.fit_transform(list_headers)
    clust = KMeans(n_clusters=10, n_jobs=4)
    clust.fit(X)
    pass




def run():
    # Get files
    csv_file_paths = get_files("/data/datagouv/datagouv_full")
    csv_info = json.load(open("csv_data_full.json"))
    all_columns = []
    for f in csv_file_paths[:1000]:
        file_id = extract_id(f)
        if file_id not in csv_info:
            continue

        csv_info_dict = csv_info[file_id]
        encoding = "latin-1"
        separator = ","

        if "encoding" in csv_info_dict:
            encoding = csv_info[file_id]["encoding"]
        if "separator" in csv_info_dict:
            separator = csv_info[file_id]["separator"]
        if "header" in csv_info_dict:
            header = csv_info[file_id]["header"]
        else:
            continue
            #header = extract_columns(f, encoding, separator)
        all_columns.append(header)

    all_columns = list(set(list(chain.from_iterable(all_columns))))

    cluster_data(all_columns)




if __name__ == '__main__':

    run()