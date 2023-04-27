# importing necessary packages
import pandas as pd
import streamlit as st
import joblib
import pickle
import random
import pydeck as pdk
import json
import requests
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from catboost import CatBoostRegressor, Pool
from datetime import datetime, timedelta

# importing the creating transformer created for pre-processing user inputs
col_transform = joblib.load('page3_files/col_transform.pkl')
# importing the catboost model for price prediction
with open('page3_files/catboost_base_model.pkl', 'rb') as f:
    catboost_model = pickle.load(f)

# reading ny zones data 
if 'zones' not in st.session_state:
  st.session_state.zones = pd.read_csv('page3_files/ny_taxi_zones.csv')

# getting the polygon coordinates for pydeck plot
@st.cache_data
def polygon_coord():
    ny_zones = json.load(open('page3_files/zones.geojson','r'))
    coordinates={}
    for i in range(0,len(ny_zones['features'])):
        coordinates[ny_zones['features'][i]['properties']['LocationID']] = ny_zones['features'][i]['geometry']['coordinates'][0]
    return coordinates
coordinates = polygon_coord()

# creating LocationID dictonary for user input
@st.cache_data
def taxi_zones_dict():
    zone_dic = {}
    for i in range(len(st.session_state.zones['LocationID'])):
        zone_dic[st.session_state.zones['zone'].iloc[i]] = st.session_state.zones['LocationID'].iloc[i]
    return zone_dic
zone_dic = taxi_zones_dict()

# dictonary necesssary for interpretation of user inputs
if 'payment_methods' not in st.session_state:
  st.session_state.payment_methods = {'Credit card':1,'Cash':2,'No charge':3,'Dispute':4,'Unkown':5}

if 'congestion_zone' not in st.session_state:
    st.session_state.congestion_zone = [12,88,261,87,13,209,231,45,232,148,144,211,125,4,79,114,113,249,158,224,137,107,234,90,68,246,233,170,164,186,100,229,162,161,230,48,50,163,
                                        140,141,237,142,143,43,262,263,236,239,238]

# user inputs
form1 = st.sidebar.form(key="Options")
vendor_id = form1.radio('Select your vendor',(1,2))
passenger_count = form1.select_slider('Number of passengers',(1,2,3,4,5,6))
pickup_zone = form1.selectbox('Select your pickup zone', tuple(zone_dic.keys()))
dropoff_zone = form1.selectbox('Select your dropoff zone', tuple(zone_dic.keys()))
payment_type = form1.selectbox('Select your payment method',('Credit card','Cash','No charge','Dispute','Unkown'))
extra = form1.number_input('Extra charge amount',min_value = 0.0, max_value = 10.0)
tip_amount = form1.number_input('Tip amount',min_value=0.0, max_value = 200.0)
tolls_amount = form1.number_input('Tolls amount',min_value=0.0, max_value = 300.0)
date_of_travel = form1.date_input("Select the date of trip")
hr_of_travel = form1.number_input('Select the hour of trip',min_value=0,max_value=23)
min_of_travel = form1.number_input('Select the minute of trip',min_value=0,max_value=60)
form1.form_submit_button("Submit")

# randomly selected the value for store_and_fwd_flag based on probabilities 
store_and_fwd_flag = random.choices(['Y','N'], weights=[0.85,0.15])[0]

# getting the ratecodeID based on user input
if dropoff_zone == 'JFK Airport':
    ratecodeID = 2
elif dropoff_zone == 'Newark Airport':
    ratecodeID = 3
elif dropoff_zone == 'Nassu' or dropoff_zone == 'Westchester':
    ratecodeID = 4
elif passenger_count>2:
    ratecodeID = 6
elif payment_type == 'No charge':
    ratecodeID = 5 
else:
    ratecodeID = 1

# getting the congestion surcharge based on the information for nyc_taxi website
if zone_dic[pickup_zone] in st.session_state.congestion_zone:
    congestion_surcharge = 2.5
else:
    congestion_surcharge = 0

# getting airport fees based on user input
if pickup_zone == 'LaGuardia Airport' or pickup_zone == 'JFK Airport':
    airport_fee = 1.25
else:
    airport_fee = 0

# getting the start date and time from the user_input
start_date = datetime.combine(date_of_travel, datetime.min.time()) + timedelta(hours=hr_of_travel,minutes=min_of_travel)

# getting the distance between pickup_location & dropoff location and duration of trip based on google distance matrix API
# creating the necessary url for API call
apikey ="" # Enter API Key
url1 = "https://maps.googleapis.com/maps/api/distancematrix/json?origins="
origin = f"{pickup_zone}"
url2 = "&destinations="
destination = f"{dropoff_zone}"
url3 = f"&mode=car&departure_time={int(start_date.timestamp())}&key="
url_full = url1+origin+url2+destination+url3+apikey

# reading in the data from the url
output = requests.get(url_full).json()

# getting the trip_distance and duration from the read json file
if output['status'] == 'OK':
    trip_distance = output['rows'][0]['elements'][0]['distance']['value']*0.00062137
    duration = output['rows'][0]['elements'][0]['duration']['value']
    if trip_distance==0 & duration ==0:
        speed = 0
    else:
        speed = trip_distance/duration
else:
    url3 = "&mode=car&departure_time=now&key="
    url_full = url1+origin+url2+destination+url3+apikey
    output = requests.get(url_full).json()
    trip_distance = output['rows'][0]['elements'][0]['distance']['value']*0.00062137
    duration = output['rows'][0]['elements'][0]['duration']['value']
    if trip_distance==0 & duration ==0:
        speed = 0
    else:
        speed = trip_distance/duration

# getting other features necessary for the model based on the start date and the duration of the trip
end_date = start_date + timedelta(seconds=duration)
pickup_day = start_date.strftime("%A")
dropoff_day = end_date.strftime("%A")
pickup_hour = hr_of_travel
dropoff_hour = end_date.hour
pickup_month = start_date.month
dropoff_month = end_date.month
pickup_mday = start_date.day
dropoff_mday = end_date.day

# function to get the time of the day the trip is happening
@st.cache_data
def time_of_day(x):
    if x in range(6,12):
        return 'Morning'
    elif x in range(12,16):
        return 'Afternoon'
    elif x in range(16,22):
        return 'Evening'
    else:
        return 'Late night'
time_of_day_pickup = time_of_day(pickup_hour)
time_of_day_dropoff = time_of_day(dropoff_hour)

# creating a dataframe from the inputs to pass to the model
zones_df = pd.DataFrame(data=[[vendor_id,passenger_count,trip_distance,ratecodeID,store_and_fwd_flag,zone_dic[pickup_zone],zone_dic[dropoff_zone],st.session_state.payment_methods[payment_type],extra,tip_amount,tolls_amount,congestion_surcharge,airport_fee,pickup_day,dropoff_day,pickup_hour,dropoff_hour,pickup_month,dropoff_month,pickup_mday,dropoff_month,time_of_day_pickup,time_of_day_dropoff,duration,speed]],columns=['VendorID','passenger_count','trip_distance','RatecodeID','store_and_fwd_flag','PULocationID','DOLocationID','payment_type','extra','tip_amount','tolls_amount','congestion_surcharge','airport_fee','pickup_day','dropoff_day','pickup_hour','dropoff_hour','pickup_month','dropoff_month','pickup_mday','dropoff_mday','time_of_day_pickup','time_of_day_dropoff','duration','speed'])
# tranforming the dataframe using the col_tranformer 
zones_df = col_transform.transform(zones_df)
# predicting the price of the trip based on the model
price_pred = catboost_model.predict(zones_df)

# webpage title
st.title('Estimate Your NYC Taxi Ride Cost')

# outputting the predicted price
if pickup_zone == dropoff_zone:
    st.subheader('Please select a different pickup zone or dropoff zone to get an estimated fare.')
else:
    st.subheader(f'The predicted price of your trip is \n $ {round(price_pred[0],2)}')
st.divider()

# getting the coordinates for the selected pickup and dropoff zones
coord = []
coord.append(coordinates[zone_dic[pickup_zone]])
coord.append(coordinates[zone_dic[dropoff_zone]])

# creating a pydeck plot to visualize the pickup and dropoff location
st.pydeck_chart(pdk.Deck(
    initial_view_state = pdk.ViewState(latitude=40.730610, longitude=-73.935242, zoom=9, bearing=0, pitch=0),
    layers = [
    pdk.Layer(
        "GreatCircleLayer",
        st.session_state.zones,
        pickable=True,
        get_stroke_width=12,
        get_source_position=st.session_state.zones.loc[st.session_state.zones['zone'] == pickup_zone, 'lng_lat'].iloc[0],
        get_target_position=st.session_state.zones.loc[st.session_state.zones['zone'] == dropoff_zone, 'lng_lat'].iloc[0],
        get_source_color=[64, 255, 0],
        get_target_color=[0, 128, 200],
        auto_highlight=True,
    ),
    pdk.Layer(
        "PolygonLayer",
        coord,
        stroked=False,
        get_polygon="-",
        get_fill_color=[225,225,225],
        get_line_color=[255, 165, 0, 80],
        line_width=10,
        opacity=0.8,
        filled=True,
        extruded=True,
        wireframe=True,
    ),
    ]
    ))
