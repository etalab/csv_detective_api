# CSV Detective API and FrontEnd


## What?
CSV Detective is a tool that gives you information about a CSV, such as its encoding and separator, as well as the type of columns contained inside: whether there are columns containing a SIRET or a SIREN number, a postal code, a department or a commune name, a geographic position, etc.

This UI builds on CSV Detective. We improved it, APIfied it, and through this interface, allow a friendlier use. Also a machine learning model to detect types was added (which is work in progress).

## Why?
This tool was developed with data.gouv.fr (DGF) in mind. Being a repository of open datasets is one of the main tasks of DGF. In that sense, knowing what is inside the large collection of CSVs it contains can be useful for several tasks:

*    Enrich the results of the search engine with the contents of the CSVs.
*    Link datasets together according to their values.
*    Link datasets with well-maintained, trustable reference datasets.
*    Group datasets together according to their general topic.

# How?
CSV Detective has two strategies to detect a column type:

1.    Rules + References: using regular expressions and also comparing the values with reference data (e.g., if the value 69007 appears in a list of postal codes, then it is a postal code.
2.   Supervised Learning (In progress): manually tagging columnt types and then determining simple features coupled to the content of the cells themselves to train classification algorithms.


## python-flask-docker-sklearn-template
A simple example of python api for real time machine learning.
On init, a simple linear regression model is created and saved on machine. On request arrival for prediction, the simple model is loaded and returning prediction.    
For more information read [this post](https://blog.solutotlv.com/deployed-scikit-learn-model-flask-docker/?utm_source=Github&utm_medium=python-flask-sklearn-docker-template)


# requirements  
docker installed


# Run on docker - local 

docker build . -t {some tag name}  -f ./Dockerfile_local  
detached : docker run -p 3000:5000 -d {some tag name}  
interactive (recommended for debug): docker run -p 3000:5000 -it {some tag name}  


# Run on docker - production 

Using uWSGI and nginx for production  
docker build . -t {some tag name}   
detached : docker run -p 3000:80 -d {some tag name}  
interactive (recommended for debug): docker run -p 3000:80 -it {some tag name}  


# Run on local computer

python -m venv env  
source env/bin/activate  
python -m pip install -r ./requirements.txt  
python main.py  


# Use sample api  

127.0.0.1:3000/isAlive  
127.0.0.1:3000/prediction/api/v1.0/some_prediction?f1=4&f2=4&f3=4  

# csv_detective_api
API to find the output of csv_detective
