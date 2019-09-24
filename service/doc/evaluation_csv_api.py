#!/usr/bin/env python
# coding: utf-8

# In[138]:

import pandas as pd
import json
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
# Matplotlib for additional customization
from matplotlib import pyplot as plt
import seaborn as sns
sns.set(rc={'figure.figsize':(11.7,8.27)})
sns.set(font_scale=1.3)  # crazy big


metrics = ['accuracy', 'weighted avg', 'O']

def print_confusion_matrix(confusion_matrix, class_names, figsize = (10,10), fontsize=13):
    df_cm = pd.DataFrame(
        confusion_matrix, index=class_names, columns=class_names, 
    )
    fig = plt.figure(figsize=figsize)
    sns.set_palette(sns.color_palette("Blues"))
    try:
        heatmap = sns.heatmap(df_cm, annot=True, fmt="d", annot_kws={"size": 9}, cbar=False, cmap="Blues")
    except ValueError:
        raise ValueError("Confusion matrix values must be integers.")
    heatmap.yaxis.set_ticklabels(heatmap.yaxis.get_ticklabels(), rotation=0, ha='right', fontsize=fontsize)
    heatmap.xaxis.set_ticklabels(heatmap.xaxis.get_ticklabels(), rotation=90, ha='right', fontsize=fontsize)
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

    return fig


df_annotations = pd.read_csv("../csv_detective_ml/data/columns_annotation_nonewtypes.csv").iloc[:, 0:5]


# print(classification_report(df_annotations.human_detected.fillna("O"), df_annotations.csv_detected.fillna("O")))
res_dict = classification_report(df_annotations.human_detected.fillna("O"), df_annotations.csv_detected.fillna("O"), output_dict=True)
conf_matrix = confusion_matrix(df_annotations.human_detected.fillna("O"), df_annotations.csv_detected.fillna("O"))
df_res = pd.DataFrame(res_dict).transpose()
print(classification_report(df_annotations.human_detected.fillna("O"), df_annotations.csv_detected.fillna("O")))


# In[169]:


df_res = df_res[["precision", "recall", "f1-score", "support"]]
# df_classif_report["type_name"] = df_classif_report.index
# print(foo)
# sns.set_palette("colorblind")

t_df_res = df_res.drop(metrics)

# Create bar plot with fmeasures
plt.xticks(rotation=90)
sns.barplot(x=t_df_res.index, y="f1-score", data=t_df_res, palette="Blues")
plt.savefig("img/rb_f1.svg", figsize=(10, 10), dpi=200, transparent=False, bbox_inches="tight")



conf_matrix = print_confusion_matrix(conf_matrix, df_res.index.values[:-3]);
conf_matrix.savefig("img/rb_matrix.svg", figsize=(10, 10), dpi=200, transparent=False, bbox_inches="tight")

# In[12]:


print(classification_report(df_annotations.human_detected.fillna("O"), df_annotations.human_detected.fillna("O")))


# In[7]:



json_csv_detective = json.load(open("csv_data.json"))


# In[29]:


json_csv_detective


# In[30]:


def get_results_list(method="ml"):
    all_columns = []
    col_method = "columns_{}".format(method) 
    for _, row in df_annotations.iterrows():
        if row["id"] in json_csv_detective:
            if col_method not in json_csv_detective[row["id"]]:
                all_columns.append(np.nan)
                continue
            if row["columns"] in json_csv_detective[row["id"]][col_method] :
                all_columns.append(json_csv_detective[row["id"]][col_method][row["columns"]][0])
            else:
                all_columns.append(np.nan)

        else:
            print("You should not be here :(")
            
    return all_columns


# In[48]:



# In[31]:


ml_results = get_results_list("ml")


# In[32]:


rb_results = get_results_list("rb")


# In[33]:


df_annotations["ML_model"] = ml_results


# In[34]:


df_annotations["RB_model"] = rb_results


# In[35]:


from sklearn.metrics import f1_score
f1_score(df_annotations.human_detected.fillna("O"), df_annotations.ML_model.fillna("O"), average="macro")


# In[36]:


f1_score(df_annotations.human_detected.fillna("O"), df_annotations.RB_model.fillna("O"), average="macro")


# In[37]:


rb_results


# In[19]:


#df_annotations.iloc[77]
get_ipython().system('hostname')


# In[22]:


f1_score(df_annotations.human_detected.fillna("O"), df_annotations.csv_detected.fillna("O"), average="macro")


# In[41]:


print(classification_report(df_annotations.human_detected.fillna("O"), df_annotations.RB_model.fillna("O")))


# In[42]:


print(classification_report(df_annotations.human_detected.fillna("O"), df_annotations.ML_model.fillna("O")))

