"""
Functions to match the contents (the columns) of a DGF CSV with their corresponding reference dataset.
For the moment it is hard-coded. Maybe make the match in some intelligent way later??

BAN : 0
RAN : 1
SUB: 2

"""
from collections import defaultdict

MATCH_DICT = {
    "adresse": [0],
    "code_commune_insee": [0],
    "code_departement": [0],
    "code_postal": [0],
    "code_region": [0],
    "commune": [0],
    "siren": [1, 2],
    "siret": [1, 2]
}

REFERENCES_DICT = {
    0: {
        "acronym": "BAN",
        "name": "Base Adresse Nationale",
        "url": "https://www.data.gouv.fr/en/datasets/base-adresse-nationale/"
    },
    1: {
        "acronym": "RNA",
        "name": "Répertoire National des Associations",
        "url": "https://www.data.gouv.fr/en/datasets/repertoire-national-des-associations/"
    },

    2: {
        "acronym": "SUB",
        "name": "Subventions",
        "url": "https://www.data.gouv.fr/en/search/?q=subventions"
    }
}


def link_reference_datasets(response, analysis_type="columns_rb"):
    """
    Add the reference datasets to those found by csv_detective
    :param response:
    :param analysis_type:
    :return:
    """
    columns_types_rb = []
    columns_types_ml = []
    if "columns_rb" in response and response["columns_rb"]:
        columns_types_rb = list(response["columns_rb"].values())  # column_types = ["uai", "boleeen", "commune", ...]
    if "columns_ml" in response and response["columns_ml"]:
        columns_types_ml = list(response["columns_ml"].values())

    columns_types = list(set(columns_types_rb + columns_types_ml))

    if columns_types:
        reference_datasets = get_reference_dataset(columns_types)
        response["reference_matched_datasets"] = {}
        response["reference_matched_datasets"]["matched_datasets"] = reference_datasets
        response["reference_matched_datasets"]["reference_datasets"] = REFERENCES_DICT

    return response


def get_reference_dataset(column_types):
    reference_datasets = defaultdict(list)
    for tipo in column_types:
        if tipo not in MATCH_DICT:
            continue
        ref_ds_id = MATCH_DICT[tipo]
        for id in ref_ds_id:
            reference_datasets[id].append(tipo)
    return reference_datasets


# b = {"columns_rb": {"a": "adresse", "b": "code_departement", "s":"siren", "t":"siret"}}
# b = {"columns_rb": {"a": "uai", "b": "nopo", "s":"foo", "t":"bar"}}
# print (link_reference_datasets(b))
