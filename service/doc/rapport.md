# CSV Detective with Machine Learning



## Motivation

In order to better understand the data contained in DGF, it would be ideal to actually know what is inside the large number of CSVs within the site.
[copy from github page]


## CSV Detective

CSV Detective is a tool that tries to find information about the contents of a CSV. It can give us two main kinds of information: metadata and types of columns.

### Metadata

By metadata I mean useful information that defines the file, for example its separator character, the number of rows contained, the header titles, the encoding, and so on.

~~~{
"encoding":"UTF-8"
"header":["Code RNE, Code Site, TYPE, ..."
"header_row_idx":0
"heading_columns":0
"ints_as_floats":[]
"separator":";"
"total_lines":119
"trailing_columns":0
}`
~~~

### Types of columns

The second kind concern the type of column we have inside the CSV. By _type_ I mean the semantic class of a given column. For example, if the column contains email addresses, or country names, or dates, etc. Specifically, the types CSV Detective finds are related to the data contained in data.gouv.fr (DGF). That is, it includes the types mentioned before, but also some specific to the French cosystem : SIRET/SIREN codes, postal codes, communes/department codes, names of communes, names of departements, adresses, and so on.



### How it works?

The current version of CSV Detective works by using a mix of rules (regular expressions) and by looking inside of reference datasets. The latter method works by first having a trustable source of data, of a known data type, e.g., a list with the postal codes of France. We can then match the values found in the CSV and decide if it is indeed a postal code depending on whether we find it or not within the list. This rule based + predefined lists method is straight-forward and interpretable, something that is not to dismiss easily. 

A well known disadvantage of using rules is that they suddenly become too much to control. Also, we have to define them by hand and they often need expert domain knowledge to be defined (what is the difference between a lambert 93 and wgs coordinate?). This can be problematic for the maintainers and newcomers to the project. Regarding the reference lists, an issue is that we need first to find this trustable data. They are also temporally fixed, i.e., they do not evolve over time. New, interesting types may emerge for which we do not have ready-to-use lists. Finally, both approaches (rule based, reference lists) require a computationally intensive check of each of the values within a column of a CSV and each of the rules or values in the reference data.

A possible solution to both problems (hard-coded rules and reference data) is to use a simple Machine Learning (ML) approach to deal with these issues. We need to define much less rules (for feature engineering) and the inference process is much faster than the current rule+reference approach. In this article we describe what we are trying at Etalab.

## Machine Learning csv_detective

Finding the types of columns is not a new challenge. For example, in this (work)[https://medium.com/liveramp-engineering/using-machine-learning-to-auto-detect-column-types-in-customer-files-80413c976a1e] by M. Haggy and J. Zhang.  Our approach is very similar. [add gael truc] Still, I describe the whole procedure to show what can be done with simple machine learning techniques.

### What types to detect? 

The first step to classify column types is to define what types are we looking for. To determine the types I focuse on I used a simple, yet questionable technique. First, I got a sample of CSVs contained in DGF. This sample was not randomly chosen, it was selected based on their popularity[really?]. It consists on around 150 CSVs files representing the most frequent resources used in DGF. Secondly, I ran csv_detective as it is, and created a list with the types found by the system. I said this technique was questionable because I limit myself to the types already defined by csv_detective, and furthermore by its correctness. Still, I think it is a godd starting point.

All in all, csv_detective found these categories:

| csv_detected       | longitude_l93      | region       |
|--------------------|--------------------|--------------|
| code_region        | latitude_l93       | json_geojson |
| code_commune_insee | siren              | sexe         |
| year               | adresse            | url          |
| commune            | longitude_wgs_fr_m | datetime_iso |
| code_postal        | latitude_wgs_fr_me | pays         |
| booleen            | departement        |              |
| date               | iso_country_code   |              |
| code_departement   | latlon_wgs         |              |


### Manual Annotation

I manually annotated columns with their true data type by looking at a sample of the contents of each column. I did it in two times, first with the results found by csv_detective over the 150 top files; and secondly with the results found by csv_detective over a sample of all the CSV resources in DGF. First I will describe the procedure of the top150 tagging.

#### First Annotation: 150 top resources of DGF


Based on the top 150 files, I  created a sort of annotation file to manually tag the data contained in each column of each of these CSV files. The annotation file contains five columns and 4748 lines. Each line represent a column of each one of the CSV files. An extract is shown below:

| columns | sample              | human_detected     | csv_detected       | id       |
|---------|---------------------|--------------------|--------------------|----------|
| REG     | [32, 1, ...]        |                    | code_region        | 03c24270 |
| DEP     | [42, 17, 50, ...]   |                    | N/A                | 03c24270 |
| COMM    | [53014, 84072, ...] |                    | code_commune_insee | 03c24270 |


In this example, per line,  we see find the first three of the columns within a file `03c24270.csv`, one column per row. The first column show us the headings (REG, DEP, COMM). The second gives us a sample (here shortened) of 10 different values found in the column. The third column is to be filled by the annotator (me). The fourth column shows what csv_detective found. Finally, column five contains the identification of the csv file (identification within the DGF database).

The goal of the annotation process was thus to manually fill the human_detected column (number three)  by looking at the sample (in column two) and choosing one of the categories found in the table above. The annotated excerpt shown above is:

| columns | sample              | human_detected     | csv_detected       | id       |
|---------|---------------------|--------------------|--------------------|----------|
| REG     | [32, 1, ...]        | code_region        | code_region        | 03c24270 |
| DEP     | [42, 17, 50, ...]   | code_departement   | N/A                | 03c24270 |
| COMM    | [53014, 84072, ...] | code_commune_insee | code_commune_insee | 03c24270 |

When I started training models with this annotated data I quickly found out a big issue with this top150 datasets. While they are 150 files and almost 5000k columns to learn from, there are several CSVs that change very little among them. This is due to the fact that several CVS files come from the same DGF dataset, i.e., a certain dataset contains two or more CSV files that are popular (they are in the top 150) but actually contain very similar data. So at one point, the models I was training were overfitting to the reduced number of different types within my data. This discovery made it clear that I had to get more data, or at least a little bit more heterogeneous.

#### Second Annotation: 100 columns of each type

For the reasons explained above, I decided to diversify my dataset. Lucky me, I had already gathered a big CSV dataset: all the CSV files referenced in DGF mainly because we have several experiments ideas to test over collection. All in all, we have 19284 CSV files, 108 Gb uncompressed.

To increase my annotated column-type dataset, I ran csv_detective for each of these files and then sampled 100 columns of each type detected. Then, I manually annotated the data by checking the results, looking at the content sample, and fixing the errors made by csv_detective. The output is a file just as the shown above (table with 5 columns). This time we have 2812 lines representing the sampled columns (100 per type, when possible). The column types found this time are 32. They are shown below:

| csv_detected     | code_commune_insee | tel_fr             |
|------------------|--------------------|--------------------|
| adresse          | sexe               | email              |
| year             | url                | twitter            |
| date             | csp_insee          | code_fantoir       |
| code_departement | longitude_l93      | siret              |
| region           | latitude_l93       | uai                |
| departement      | iso_country_code   | code_csp_insee     |
| latitude_wgs     | insee_canton       | jour_de_la_semaine |
| latlon_wgs       | longitude_wgs      | date_fr            |
| json_geojson     | code_postal        | insee_ape700       |
| booleen          | pays               | datetime_iso       |
| commune          | siren              |                    |

Finally, I decided to join these two datasets, the top150 with the 100 sampled columns. This gives me a dataset of 7459 lines which in theory is more heterogeneous that the vanilla top150 dataset.
[pic with freq by type]

### Supervised Type Detection

#### Features

I hand-engieneered three sets of features, depending of the information they exploit.
1. Custom hand-crafted features: nine features which intutively gives us information about the content of each cell value of each column. They are shown in the list below.
    a. Does the value represents a float? (binary)
    b. Number of lower-case characters (numeric)
    c. Number of upper-case characters (numeric)
    d. Number of characters (numeric)
    e. Number of numeric characters (numeric)
    f. Number of alphabet characters (numeric)
    g. Number of unique characters (numeric)
    h. Number of spaces (numeric)
    i. Number of punctuation characters (numeric)

2. Cell-values' bag-of-words: the actual content of each cell, in each column is used to build a bag-of-models feature set. I operate at character level, using 3-gramsm weighted by tf-idf.


3. Headings' bag-of-words: the word/words that are part of the heading of the column are evidently a dead give away for the content of the column. I transform the headings into character-level  3-grams features, again weighted with at tf-idf scheme. These features use the top 2000 most frequent tokens in the vocabulary. Using the headings is without a doubt a polemic decision. For one, one could simply match the headings with a selected number of already-known headings (types) and we would be done. Still, the idea is to detect column types even if the heading does not correspond to whatever it should contain, that is, if we have a column with a heading "code SIRET" and the contents of the column are not code SIRETs, we should be able to detect that. Finally, the headings are very strong  signals that we should leverage to solve this proiblem.

#### Learning Algorithm


Phew! Once I have 7459 annotated columns I can try to learn something, if anything. As usual, this part is somehow the fastest one once you have the learning data.

The model I used is the good old XGBoost (via its Python with default parameters. I tried a MLP with 2 layers, both with 512 units, similar to what [] tried. I got faster training and better results with XGBoost.

The validation is done with a 
