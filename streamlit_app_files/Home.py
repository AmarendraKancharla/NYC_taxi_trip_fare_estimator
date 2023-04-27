# importing necessary packages
import streamlit as st
from PIL import Image

# title of the page
st.title('NYC Yellow taxi')

# reading in an image
image = Image.open('taxi_hailing.png')
st.image(image,width=700)
st.divider()

# some text about the website
st.write(''' Welcome to this website, where you can explore the fascinating world of New York City's yellow taxis! These iconic cabs have been a fixture of the city's streets for over a century, and they continue to provide a vital transportation service to millions of residents and visitors every year.

The interactive visualizations on this website allow you to see how key factors like the number of cabs on the road, the average distance and duration of trips, and the total fare of each ride have evolved over time. Whether you're interested in tracking long-term trends or exploring the impact of specific events on the taxi industry, the tools on this website make it easy to dive deep into the data.

But that's not all! Taking a yellow cab in NYC can be challenging because you don't always know how much your trip will cost ahead of time. That's why a machine learning model has been developed that can predict the likely fare for any given ride, based on historical data from the NYC Taxi and Limousine Commission. Enter your pickup, dropoff locations and few other factors like tips etc, and the model will provide you with an estimate of what you can expect to pay.

Whether you're a seasoned New Yorker or a first-time visitor, this website is designed to help you better understand and navigate the world of yellow taxis in NYC. Explore the visualizations and try out the fare estimator! ''')