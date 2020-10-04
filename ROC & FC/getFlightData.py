#!/usr/bin/env python
# coding: utf-8

# In[31]:


import sqlite3 as sql
import os


# In[32]:


##gets ROC & Average Fuel consumption, based on aircraft weight, outside air temp & altitude
def getFlightPointData(cursor, weight, temp, altitude):
    sqlite_select_query = """SELECT * from data where weight=? AND temp=? AND altitude=?"""
    cursor.execute(sqlite_select_query,(weight,temp,altitude))
    return cursor.fetchall()


# In[54]:


##gets averaged data, based on flight pattern, weight, fuel, starting parameters
def getFlightData( aircraftType, flightPattern, weight, fuel, startTemp, endTemp,startAlt, endAlt):
    cwd = os.getcwd()
    try:
        conn=sql.connect(cwd+"\\database\\"+aircraftType+"."+flightPattern+".sqlite")
    except Error as e:
        print("Could not connect to database...")
    
    cursor = conn.cursor()
    totalWeight=weight+fuel
    startRecords = getFlightPointData(cursor,totalWeight,startTemp,startAlt)
    endRecords= getFlightPointData(cursor,totalWeight,endTemp,endAlt)
    cursor.close()
    avgROC=(startRecords[0][3]+endRecords[0][3])/2
    avgFC=(startRecords[0][4]+endRecords[0][4])/2
    return [avgROC,avgFC]


# In[55]:


def getFlightLegData( aircraftType, flightPattern, weight, fuel, startTemp, endTemp,startAlt, endAlt):
    for pattern in flightPattern:
        avgROC, avgFC = getFlightData(aircraftType, pattern, weight, fuel, startTemp, endTemp,startAlt, endAlt)
    return [avgROC,avgFC]


# In[56]:


avgRoc, avgFC = getFlightLegData("Airbus",["Climb"],14,14,40,40,13,13)
print(avgRoc)
print(avgFC)

