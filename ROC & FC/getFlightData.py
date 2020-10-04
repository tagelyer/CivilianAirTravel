#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sqlite3 as sql
import csv_to_sqlite


# In[37]:


##Script to convert CSV to SQL
##options = csv_to_sqlite.CsvOptions(typing_style="full", encoding="windows-1250") 
##input_files = ["C:\\Users\divin\\Documents\\Self studies\\Pizzas\\data.csv"] # pass in a list of CSV files
##csv_to_sqlite.write_csv(input_files, "C:\\Users\divin\\Documents\\Self studies\\Pizzas\\data.sqlite", options)


# In[27]:


##gets ROC & Average Fuel consumption, based on aircraft weight, outside air temp & altitude
def getFlightData(cursor, weight, temp, altitude):
    sqlite_select_query = """SELECT * from data where weight=? AND temp=? AND altitude=?"""
    cursor.execute(sqlite_select_query,(weight,temp,altitude))
    return cursor.fetchall()


# In[43]:


##gets averaged data, based on flight pattern, weight, fuel, starting parameters
def getData( aircraftType, flightPattern, weight, fuel, startTemp, endTemp,startAlt, endAlt):
    try:
        conn=sql.connect("C:\\Users\divin\\Documents\\Self studies\\Pizzas\\"+aircraftType+"."+flightPattern+".sqlite")
    except Error as e:
        print("Could not connect to database...")
    
    cursor = conn.cursor()
    totalWeight=weight+fuel
    startRecords = getFlightData(cursor,totalWeight,startTemp,startAlt)
    endRecords= getFlightData(cursor,totalWeight,endTemp,endAlt)
    cursor.close()
    avgROC=(startRecords[0][3]+endRecords[0][3])/2
    avgFC=(startRecords[0][4]+endRecords[0][4])/2
    return [avgROC,avgFC]


# In[44]:


avgRoc, avgFC = getData("Airbus","Climb",14,14,40,40,13,13)
print(avgRoc)
print(avgFC)

