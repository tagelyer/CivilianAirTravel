#!/usr/bin/env python
# coding: utf-8

# In[2]:


import csv_to_sqlite
import os


# In[3]:


#Script to convert CSV to SQL
cwd = os.getcwd()
options = csv_to_sqlite.CsvOptions(typing_style="full", encoding="windows-1250") 
input_files = [cwd+"\\database\\data.csv"] # pass in a list of CSV files
csv_to_sqlite.write_csv(input_files, cwd+"\\database\\data.sqlite", options)

