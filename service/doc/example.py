"""
# CSV Detective with Machine Learning

CSV Detective is a tool that tries to find information about the contents of a CSV. It can give us two main kinds of information: metadata and types of columns.

### Metadata

By metadata I mean useful information that defines the file, for example its separator character, the number of rows contained, the header titles, the encoding, and so on.

`{
"encoding":"UTF-8"
"header":["Code RNE, Code Site, TYPE, ..."
"header_row_idx":0
"heading_columns":0
"ints_as_floats":[]
"separator":";"
"total_lines":119
"trailing_columns":0
}`


### Types of columns

The second kind concern the type of column we have inside the CSV. By _type_ I mean the semantic class of a given column. For example, if the column contains email addresses, or country names, or dates, etc. Specifically, the types CSV Detective finds are related to the data contained in data.gouv.fr (DGF). That is, it includes the types mentioned before, but also some specific to the French cosystem : SIRET/SIREN codes, postal codes, communes/department codes, names of communes, names of departements, adresses, and so on.

## Motivation

In order to better understand the data contained in DGF, it would be ideal to actually know what is inside the large number of CSVs within the site.
[copy from github page]

## How it works?

The current version of CSV Detective finds the data described above by using a mix of rules (regular expressions) and by looking inside of reference datasets. The latter method works by first having a trustable source of data types, for example a list with the postal codes of France. We can then match the values found in the CSV and decide if it is indeed a postal code depending on whether we found said value or not within the list. This rule based + predefined lists method is straight-forward and interpretable, something that is not to dismiss easily. 

A well known disadvantage of using rules is that they suddenly become too much to control. Also, we have to define them by hand and they often need expert domain knowledge to be defined (what is the difference between a lambert 93 and wgs coordinate?). This can be problematic for the maintainers and newcomers to the project. Regarding the reference lists, an issue is that we need first to find this trustable data. They are also temporally fixed, i.e., they do not evolve over time. New, interesting types may emerge for which we do not have ready-to-use lists. Finally, both approaches (rule based, reference lists) require a computationally intensive check of each of the values within a column of a CSV and each of the rules or values in the reference data.

A possible solution to both problems (hard-coded rules and reference data) is to use a simple Machine Learning (ML) approach to deal with these issues. In this article we describe what we are trying at Etalab.

## Machine Learning Track

Finding the types of columns is not a new challenge. For example, in this (work)[https://medium.com/liveramp-engineering/using-machine-learning-to-auto-detect-column-types-in-customer-files-80413c976a1e] by M. Haggy and J. Zhang.  Our approach is very similar,  not say the same.

[add gael truc]

Still, we describe here the difficulties we found as the problem is not as simple as I actually thought. Or at least when attempting to solve it with machine learning techniques.

### What types to detect? 

To determine the types we want our system to detect I used a simple, yet questionable technique. First, I got a sample of CSVs contained in DGF. This sample was not randomly chosen, it was selected based on their popularity[really?]. It consists on around 150 CSVs files representing the most frequent resources used in DGF. 

We used the types already defined by CSV Detective





Turn Python scripts into handouts with Markdown comments and inline figures. An
alternative to Jupyter notebooks without hidden state that supports any text
editor.
"""

import handout
import matplotlib.pyplot as plt
import numpy as np

"""Start your handout with an output directory."""

doc = handout.Handout('output')

"""
## Markdown comments

Comments with triple quotes are converted to text blocks.

Text blocks support [Markdown formatting][1], for example:

- Headlines
- Hyperlinks
- Inline `code()` snippets
- **Bold** and *italic*
- LaTeX math $f(x)=x^2$

[1]: https://commonmark.org/help/
"""

"""
## Add text and variables

Write to our handout using the same syntax as Python's `print()`:
"""
for index in range(3):
  doc.add_text('Iteration', index)
doc.show()

"""
## Add Matplotlib figures

Display matplotlib figures on the handout:
"""
fig, ax = plt.subplots(figsize=(4, 3))
ax.plot(np.arange(100))
fig.tight_layout()
doc.add_figure(fig)
doc.show()  # Display figure below this line.

"""
Set the width to display multiple figures side by side:
"""

for iteration in range(3):
  fig, ax = plt.subplots(figsize=(3, 2))
  ax.plot(np.sin(np.linspace(0, 20 / (iteration + 1), 100)))
  doc.add_figure(fig, width=0.33)
doc.show()

"""
## Add images and videos

This requires the `imageio` pip package.
"""
image_a = np.random.uniform(0, 255, (200, 400, 3)).astype(np.uint8)
image_b = np.random.uniform(0, 255, (100, 200, 1)).astype(np.uint8)
doc.add_image(image_a, 'png', width=0.4)
doc.add_image(image_b, 'jpg', width=0.4)
doc.show()
video = np.random.uniform(0, 255, (100, 64, 128, 3)).astype(np.uint8)
doc.add_video(video, 'gif', fps=30, width=0.4)
doc.add_video(video, 'mp4', fps=30, width=0.4)
doc.show()

"""
## Exclude lines

Hide code from the handout with the `# handout: exclude` comment:
"""

# Invisible below:
value = 13  # handout: exclude

"""
Exclude whole ranges between `# handout: begin-exclude` and `# handout:
end-exclude` lines.
"""

"""
## View the handout

The handout is automatically saved when you call `doc.show()`. Just open
`output/index.html` in your browser.
"""
