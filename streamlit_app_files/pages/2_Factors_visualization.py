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
file_name = get_file_names(os.getcwd()+"/page2_files")

# reading in the data in the files names to a dictonary
@st.cache_data
def load_files(files):
    df_months_dict = {}
    for i in file_name:
        df_name = f"df2_{i.split('.')[0]}"
        globals()[df_name] = pd.read_parquet('page2_files/'+i)
        if df_name.endswith('_m'):
            if df_name.split('_')[2] == 'time':
                df_months_dict[('time_of_day','month')] = globals()[df_name]
            else:
                df_months_dict[(df_name.split('_')[2],'month')] = globals()[df_name]
        else:
            if df_name.split('_')[2] == 'time':
                df_months_dict[('time_of_day','all_month')] = globals()[df_name]
            else:
                df_months_dict[(df_name.split('_')[2],'all_month')] = globals()[df_name]
    return df_months_dict
df_months_dic = load_files(file_name)

# reading in taxi zones file
@st.cache_data
def taxi_zones_dict():
    zones = pd.read_csv('page2_files/ny_taxi_zones.csv')
    zone_dic = {}
    for i in range(len(zones['LocationID'])):
        zone_dic[zones['zone'].iloc[i]] = zones['LocationID'].iloc[i]
    return zone_dic
zone_dic = taxi_zones_dict()

# user inputs
form1 = st.sidebar.form(key="Options")
pickup_zone = form1.selectbox('Select your pickup zone', tuple(zone_dic.keys()))
dropoff_zone = form1.selectbox('Select your dropoff zone', tuple(zone_dic.keys()))
month = form1.selectbox('What month would you like to visualize the data for?',
                        ('All_months','January','February','March','April','May','June','July','August','September','October','November','December'))
period_of_time = form1.selectbox('What period would you like to visualize the data for?', ('day','hour','mday','time_of_day','month'))
form1.form_submit_button("Submit")

# function for plotly bar plot
def bar_plot(df,col1,col2,title):
    fig = px.bar(df,x=col1,y=col2,title=title)
    return fig

# title of the page
st.title('Visualize the factors changing through time')

# creating necessary dictonaries 
if 'month_dict' not in st.session_state:
    st.session_state.month_dict = {'All_months':0,'January':1,'Feburary':2,'March':3,'April':4,'May':5,'June':6,'July':7,'August':8,'September':9,'October':10,'November':11,'December':12}

if 'pickup_fea_dict' not in st.session_state:
    st.session_state.pickup_fea_dict = {'day':'pickup_day','hour':'pickup_hour','mday':'pickup_mday','time_of_day':'time_of_day_pickup','month':'pickup_month'}

# plotting the bar plots based on the user inputs
if month != 'All_months' and period_of_time == 'month':
    st.subheader("This is an invalid selection. Month period of time can only be selected when All_months option is choosen.")
elif month != 'All_months':
    df_choosen = df_months_dic[(period_of_time,'month')]
    df_choosen = df_choosen.loc[(df_choosen['PULocationID']==zone_dic[pickup_zone]) & (df_choosen['DOLocationID']==zone_dic[dropoff_zone]) & (df_choosen['pickup_month']==st.session_state.month_dict[month])]
    st.plotly_chart(bar_plot(df_choosen,col1=st.session_state.pickup_fea_dict[period_of_time],col2='number_of_cabs',title=f'Number_of_cabs Vs {period_of_time}'))
    st.plotly_chart(bar_plot(df_choosen,col1=st.session_state.pickup_fea_dict[period_of_time],col2='trip_distance',title=f'Average_trip_distance Vs {period_of_time}'))
    st.plotly_chart(bar_plot(df_choosen,col1=st.session_state.pickup_fea_dict[period_of_time],col2='duration',title=f'Average_duration Vs {period_of_time}'))
    st.plotly_chart(bar_plot(df_choosen,col1=st.session_state.pickup_fea_dict[period_of_time],col2='total_amount',title=f'Average_trip_amount Vs {period_of_time}'))
else:
    df_choosen = df_months_dic[(period_of_time,'all_month')]
    df_choosen = df_choosen.loc[(df_choosen['PULocationID']==zone_dic[pickup_zone]) & (df_choosen['DOLocationID']==zone_dic[dropoff_zone])]
    st.plotly_chart(bar_plot(df_choosen,col1=st.session_state.pickup_fea_dict[period_of_time],col2='number_of_cabs',title=f'Number_of_cabs Vs {period_of_time}'))
    st.plotly_chart(bar_plot(df_choosen,col1=st.session_state.pickup_fea_dict[period_of_time],col2='trip_distance',title=f'Average_trip_distance Vs {period_of_time}'))
    st.plotly_chart(bar_plot(df_choosen,col1=st.session_state.pickup_fea_dict[period_of_time],col2='duration',title=f'Average_duration Vs {period_of_time}'))
    st.plotly_chart(bar_plot(df_choosen,col1=st.session_state.pickup_fea_dict[period_of_time],col2='total_amount',title=f'Average_trip_amount Vs {period_of_time}'))