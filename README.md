# CSV Detective API and Frontend


## What?
[CSV Detective](https://github.com/etalab/csv_detective) is a tool that gives you information about a CSV, such as its encoding and separator, as well as the type of columns contained inside: whether there are columns containing a SIRET or a SIREN number, a postal code, a department or a commune name, a geographic position, etc.

This UI builds on CSV Detective. We improved it, APIfied it, and through this interface, allow a friendlier use. Also a machine learning model to detect types was added (which is work in progress).

## Why?
This tool was developed with data.gouv.fr (DGF) in mind. Being a repository of open datasets is one of the main tasks of DGF. In that sense, knowing what is inside the large collection of CSVs it contains can be useful for several tasks:

*    Enrich the results of the search engine with the contents of the CSVs.
*    Link datasets together according to their values.
*    Link datasets with well-maintained, trustable reference datasets.
*    Group datasets together according to their general topic.

## How?
CSV Detective has two strategies to detect a column type:
               
1.   _Rules + References_: using regular expressions and also comparing the values with reference data (e.g., if the value 69007 appears in a list of postal codes, then it is a postal code.
2.   _Supervised Learning (In progress)_: manually tagging column types and then determining simple features coupled to the content of the cells themselves to train classification algorithms.

# Requirements

The easiest way to install this API is by cloning it and creating a Docker container. To do this you first need docker and docker-compose installed.
After cloning, move into the project's folder and run `docker-compose up`.

# Using the API 

The API is described in `localhost:5000` via the API swagger interface.

