# Cell Count Analysis Project

# How to run
- run 'make setup'
- run 'make pipeline'
- run 'make dashboard'

# Schema I used **Anything in parentheses means it is a foreign key of another table)**
Projects:
-project_id (key)
-project_name

Subjects:
-subject_id //Primary Key
-subject
-project(project_id) //Foreign Key
-condition
-age
-sex
-treatment
-response

Samples:
-sample_id //Primary Key
-sample
-Subjects(subject_id) //Foreign Key
-sample_type
-time_from_treatment_start

Cell Types:
-cell_type_id //Primary Key
-cell_name

Cell_counts:
-cell_count_id //Primary Key
-Samples(sample_id) //Foreign Key
-Cell Types(cell_type_id) //Foreign Key

# Rationale
This schema is used to reduce the repeated information and make it easier to scale the database. I had decided on this design to reduces unecessary data duplication and to make relationships more explicit and easier to read.
In terms of scalability, using separate tables allows us to grow the database vertically rather than horizontally when new information, such as Cell types, is added in the future.

# Code Structure
I separated this project into three separate files for loading the data, analysis, and the dashboard

# load_data.py
This file creates the SQLite database based on my schema shown above. It loads the information from the provided "cell-count.csv" file into a database.
-Creates the "projects", "subjects", "samples", "cell_types", and "cell_count" tables 

# analysis.py
This file connects to the "cell-count.db" created by "load_data.py" and runs SQL queries to solve the given assignments.
- Calculates total cell count per sample
- Calculates relative cell type percentages
- Creates boxplots for each cell type
- Runs a statistical analysis

# streamlit_app.py
This file uses Streamlit to make an interactive dashboard locally. It reads from generated CSV files to generate the summary metrics.
- Responder vs Non-Responder
- Cell-types boxplots
- Statistical tables

# Makefile.txt
Provides the three commands needed to run this
In terminal write:
- make setup
- make pipeline
- make dashboard

# Local host link:
http://localhost:8501/
