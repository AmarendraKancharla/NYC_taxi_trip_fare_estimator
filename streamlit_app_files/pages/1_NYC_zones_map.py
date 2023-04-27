# importing necessary packages
import pandas as pd
import streamlit as st
import glob
import math
import json
import os
import plotly.express as px

# getting all the necessary file names
@st.cache_data
def get_file_names(path):
    file_names = glob.glob(path + "/*.parquet")
    filename_list = [os.path.basename(file) for file in file_names]
    return filename_list
file_name = get_file_names(os.getcwd()+"/page1_files")

# reading in the data to a dictionary in the file names
@st.cache_data
def load_files(files):
    df_months_dict = {}
    for i in files:
        df_name = f"df2_{i.split('.')[0]}"
        globals()[df_name] = pd.read_parquet('page1_files/'+i)
        if df_name.endswith('_m'):
            if 'pickups' in df_name:
                if df_name.split('_')[-2] == 'time':
                    df_months_dict[('pickup','time_of_day','month')] = globals()[df_name]
                else:
                    df_months_dict[('pickup',df_name.split('_')[-2],'month')] = globals()[df_name]
            elif 'dropoffs' in df_name:
                if df_name.split('_')[-2] == 'time':
                    df_months_dict[('dropoff','time_of_day','month')] = globals()[df_name]
                else:
                    df_months_dict[('dropoff',df_name.split('_')[-2],'month')] = globals()[df_name]
        else:
            if 'pickups' in df_name:
                if df_name.split('_')[-1] == 'time':
                    df_months_dict[('pickup','time_of_day','all_month')] = globals()[df_name]
                else:
                    df_months_dict[('pickup',df_name.split('_')[-1],'all_month')] = globals()[df_name]
            elif 'dropoffs' in df_name:
                if df_name.split('_')[-1] == 'time':
                    df_months_dict[('dropoff','time_of_day','all_month')] = globals()[df_name]
                else:
                    df_months_dict[('dropoff',df_name.split('_')[-1],'all_month')] = globals()[df_name]
    return df_months_dict
df_months_dic = load_files(file_name)

# loading the geojson file
@st.cache_data
def load_json():
    ny_zones = json.load(open('page1_files/zones.geojson','r'))
    for feature in ny_zones['features']:
        feature['id'] = feature['properties']['LocationID']
    return  ny_zones
ny_zones = load_json()

# creating the necessary dictonaries for the data visualization
if 'pickup_fea_dict' not in st.session_state:
  st.session_state.pickup_fea_dict = {'day':'pickup_day','hour':'pickup_hour','mday':'pickup_mday','time_of_day':'time_of_day_pickup','month':'pickup_month'}

if 'dropoff_fea_dict' not in st.session_state:
  st.session_state.dropoff_fea_dict = {'day':'dropoff_day','hour':'dropoff_hour','mday':'dropoff_mday','time_of_day':'time_of_day_dropoff','month':'dropoff_month'}

if 'anim_dict' not in st.session_state:
  st.session_state.anim_dict = {'pickup_day':['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],'pickup_hour':list(range(0,24)),'pickup_mday':list(range(1,32)),'time_of_day_pickup':['Morning', 'Afternoon', 'Evening', 'Late night'],'pickup_month':list(range(1,13))
                                  ,'dropoff_day':['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],'dropoff_hour':list(range(0,24)),'dropoff_mday':list(range(1,32)),'time_of_day_dropoff':['Morning', 'Afternoon', 'Evening', 'Late night'],'dropoff_month':list(range(1,13))}

if 'fea_dict' not in st.session_state:
  st.session_state.fea_dict = {'number_of_cabs':'avg_number_of_cabs','trip_distance':'avg_trip_distance','duration':'avg_trip_duration','total_amount':'avg_trip_cost'}

if 'month_dict' not in st.session_state:
  st.session_state.month_dict = {'All_months':0,'January':1,'Feburary':2,'March':3,'April':4,'May':5,'June':6,'July':7,'August':8,'September':9,'October':10,'November':11,'December':12}

if 'list_of_params' not in st.session_state:
  st.session_state.list_of_params = ['number_of_cabs','trip_distance','duration','total_amount']

# function to create a plotly choropleth_map figure
def choropleth_map(df, col, anim_col,month = 'All_months'):
    cs_min = math.floor(min(df[col]))
    cs_max = math.ceil(max(df[col]))
    if month == 'All_months':
        df = df
    else:
        df = df[df['pickup_month'] == st.session_state.month_dict[month]]
    fig = px.choropleth_mapbox(df, geojson=ny_zones, locations='LocationID', color=col,
                            color_continuous_scale="plasma",
                            range_color=(cs_min, cs_max),
                            mapbox_style="carto-positron",
                            zoom=9.5, center = {"lat": 40.730610, "lon": -73.935242},
                            opacity=0.5,
                            hover_name='zone',
                            hover_data=['borough','service_zone'],
                            labels={col:st.session_state.fea_dict[col]},
                            animation_frame = anim_col,
                            category_orders={anim_col:st.session_state.anim_dict[anim_col]}
                            )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                    coloraxis_colorbar_thickness=23,
                    transition = {'duration': 3000},
                    height = 600,
                    width = 1000)
    return fig

# user inputs
form1 = st.sidebar.form(key="Options")
data_col = form1.selectbox('What do you want to visualize?',
    ('number_of_cabs','trip_distance','duration','total_amount'))
month = form1.selectbox('What month would you like to visualize the data for?',
    ('All_months','January','February','March','April','May','June','July','August','September','October','November','December'))
period_of_time = form1.selectbox('What period would you like to visualize the data for?', ('day','hour','mday','time_of_day','month'))
form1.form_submit_button("Submit")

# title of the page
st.header('Visualize the factors change on a map through different periods of time based on pickup and dropoff locations')

# Initializing tabs on the web page
tab1, tab2 = st.tabs(["Pickup_locations", "Dropoff_locations"])

# plot in the pickup tab
with tab1:
    if month == 'All_months':
        st.plotly_chart(choropleth_map(df_months_dic[('pickup',period_of_time,'all_month')],data_col,st.session_state.pickup_fea_dict[period_of_time]),use_container_width=True,height=600,width=1000)
    elif month != 'All_months' and period_of_time == 'month':
        st.write("This is an invalid selection. Month period of time can only be selected when All_months option is choosen.")
    else:
        st.plotly_chart(choropleth_map(df_months_dic[('pickup',period_of_time,'month')],data_col,st.session_state.pickup_fea_dict[period_of_time],month),use_container_width=True,height=600,width=1000)

# plot in the dropoff tab
with tab2:
    if month == 'All_months':
        st.plotly_chart(choropleth_map(df_months_dic[('dropoff',period_of_time,'all_month')],data_col,st.session_state.dropoff_fea_dict[period_of_time]),use_container_width=True,height=600,width=1000)
    elif month != 'All_months' and period_of_time == 'month':
        st.write("This is an invalid selection. Month period of time can only be selected when All_months option is choosen.")
    else:
        st.plotly_chart(choropleth_map(df_months_dic[('dropoff',period_of_time,'month')],data_col,st.session_state.dropoff_fea_dict[period_of_time],month),use_container_width=True,height=600,width=1000)