"""
Functions to match the contents (the columns) of a DGF CSV with their corresponding reference dataset.
For the moment it is hard-coded. Maybe make the match in some intelligent way later??
"""
from collections import defaultdict

MATCH_DICT = {
    "adresse": ["BAN"],
    "code_commune_insee": ["BAN"],
    "code_departement": ["BAN"],
    "code_postal": ["BAN"],
    "code_region": ["BAN"],
    "commune": ["BAN"],
    "siren": ["RNA", "SUB"],
    "siret": ["RNA", "SUB"]
}

REFERENCES_DICT = {
    "BAN": {
        "name": "Base Adresse Nationale",
        "url": "https://www.data.gouv.fr/en/datasets/base-adresse-nationale/"
    },
    "RNA": {
        "name": "Répertoire National des Associations",
        "url": "https://www.data.gouv.fr/en/datasets/repertoire-national-des-associations/"
    },
    "SUB": {
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
    if analysis_type in response:
        column_types = [t for t in response[analysis_type].values()]
        reference_datasets = get_reference_dataset(column_types)
        response["reference_datasets"] = reference_datasets

    return response

def get_reference_dataset(column_types):
    if not isinstance(column_types, list):
        column_types = [column_types]
    reference_datasets = defaultdict(list)
    for tipo in column_types:
        if tipo not in MATCH_DICT:
            continue
        references = MATCH_DICT[tipo]
        for ref in references:
            if ref not in REFERENCES_DICT:
                continue
            reference_datasets[tipo].append(REFERENCES_DICT[ref])
    return reference_datasets