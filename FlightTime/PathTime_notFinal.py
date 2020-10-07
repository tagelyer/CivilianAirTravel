import pandas as pd
import numpy as np
import math
import haversine as hs
from haversine import Unit
import requests
import json

# import tracks from csv
try:
    df_1 = pd.read_csv('track1.csv')
    df_2 = pd.read_csv('track2.csv')
    df_airSpeed = pd.read_csv('air_speed.csv')
except OSError:
    print("Could not connect to database...")


def creat_list_from_csv(df, lat_point, lon_point, high_point):
    lat = pd.DataFrame(df[lat_point])
    lon = pd.DataFrame(df[lon_point])
    high = pd.DataFrame(df[high_point])
    x, y, z = lat.to_numpy(), lon.to_numpy(), high.to_numpy()
    temp_list = np.append(x, y, axis=1)  # add col
    points_list = np.append(temp_list, z, axis=1)
    return points_list


# form= list[lat, lon, high]
path1_Alist = creat_list_from_csv(df_1, 'lat_a', 'lat_a', 'hight_a(m)')  # points a in track 1
path1_Blist = creat_list_from_csv(df_1, 'lat_b', 'lat_b', 'hight_b(m)')  # points b in track 1
path2_Alist = creat_list_from_csv(df_2, 'lat_a', 'lat_a', 'hight_a(m)')  # points a in track 2
path2_Blist = creat_list_from_csv(df_2, 'lat_b', 'lat_b', 'hight_b(m)')  # points b in track 2
#print(path1_Alist)


def clc_dist_between_2points(lat1, lon1, lat2, lon2):
    coordinate1 = (lat1, lon1)
    coordinate2 = (lat2, lon2)
    # dist_mil= hs.haversine(coordinate1,coordinate2,unit=Unit.MILES)
    dist_metre = hs.haversine(coordinate1, coordinate2, unit=Unit.METERS)
    #print('dist meter', dist_metre )
    return dist_metre


def clc_azimuth(lat1, lon1, lat2, lon2):
    dL = lon2 - lon1
    X = math.cos(lat2) * math.sin(dL)
    Y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dL)
    bearing_rad = np.arctan2(X, Y)  # radian
    bearing_deg = ((np.degrees(bearing_rad) + 360) % 360)  # degrees
    return bearing_deg


# air speed from csv
def get_Aspeed(weight):
    w = pd.DataFrame(df_airSpeed['weight'])
    weight_list = w.to_numpy()
    s = pd.DataFrame(df_airSpeed['air speed'])
    Aspeed_list = s.to_numpy()
    weight_mod = weight - (weight % 50)  # rounding down
    for i in range(len(s)):
        if weight_mod == weight_list[i]:
            break
        else:
            continue
    #print(Aspeed_list[i])
    return Aspeed_list[i]


def get_weather(lat, lon, request):
    api_key = "c80b790a2fd8650bc690c41a4c001f0a"
    url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=metric" % (lat, lon, api_key)
    response = requests.get(url)
    data = json.loads(response.text)
    weather_request = data["current"][request]
    return weather_request


def clc_Gspeed(az, wind_speed, wind_deg, Aspeed):
    Gspeed = Aspeed + wind_speed * math.cos((wind_deg + 180) - az)  # ?need to confirm?
    return Gspeed
# add yaw


# main func- clc time and fuel weist in each leg
def clc_leg_FlightTime_FuelWeist(lat1, lon1, lat2, lon2, h1, h2, wind_ref_point, avgROC, av_feul_climb, av_feul_str, start_fuel):
    distance = clc_dist_between_2points(lat1, lon1, lat2, lon2)
    high_diff = h2 - h1
    az = clc_azimuth(lat1, lon1, lat2, lon2)
    if wind_ref_point == 'start':  # option for later
        wind_speed = get_weather(lat1, lon1, "wind_speed")
        wind_deg = get_weather(lat1, lon1, "wind_deg")
    else:
        wind_speed = get_weather(lat1, lon1, "wind_speed")
        wind_deg = get_weather(lat1, lon1, "wind_deg")
    Aspeed = get_Aspeed(aircraft_weight + start_fuel)
    Gspeed = clc_Gspeed(az, wind_speed, wind_deg, Aspeed)
    # How long did it take
    time_dist = (distance / Gspeed) * 100 / 6  # 6min/100 -- time of flight from point a to b
    time_climb = high_diff / avgROC  # min -- time to climb from point 1 to point b
    time_of_leg = max(time_dist, time_climb)
    # Fuel consumption
    if time_of_leg == time_climb:
        fuel_decrease = av_feul_climb * time_of_leg
    elif time_of_leg == time_dist:
        fuel_decrease = av_feul_climb * time_climb
        fuel_decrease += av_feul_str * (time_dist - time_climb)
    current_fuel = start_fuel - fuel_decrease

    return time_of_leg, current_fuel


leg_time_list = []
leg_fuel_list = []
num_legs = int(len(df_1['lat_a']))
wind_ref_point = 'start'
leg_fuel_list += [500]  # ?start fuel?
aircraftType = "Airbus"  # ?temporary?
aircraft_weight = 0  # ?temporary?

# ------- path 1 only-------
for i in range(num_legs):
    weight_tot = leg_fuel_list[i] + aircraft_weight
    startTemp, endTemp = get_weather(path1_Alist[i][0], path1_Alist[i][1], "temp"), get_weather(path1_Blist[i][0], path1_Blist[i][1], "temp")
    # func in-- getFlightData.ipynb
    # avgROC, avgFC = getFlightLegData(aircraftType, flightPattern, weight_tot, leg_fuel_list[i], startTemp, endTemp, path1_Alist[i][2], path1_Blist[i][2])
    av_feul_str = 0.002  # ?missing func?
    avgROC, avgFC = 500, 0.0019# - for check, delete when marge codes
    leg_time, fuel_weist = clc_leg_FlightTime_FuelWeist(path1_Alist[i][0], path1_Alist[i][1], path1_Blist[i][0], path1_Blist[i][1], path1_Alist[i][2], path1_Blist[i][2], wind_ref_point, avgROC, avgFC, av_feul_str, leg_fuel_list[i])
    leg_time_list.append(leg_time)
    leg_fuel_list.append(fuel_weist)
    print('leg time ', i, leg_time, 'fuel leg', fuel_weist)

total_time = sum(leg_time_list)
total_fuel_weist = leg_fuel_list[0] - leg_fuel_list[num_legs - 1]
# ---------------------------
print('total', total_time)

# add another path and compare
# yaw (wind)
# av_feul_str missing func
# start fuel, aircraftType,aircraft_weight - add a csv file
# average feul weist while waiting missing func
# verify units between all codes
