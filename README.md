# NYC_taxi_trip_fare_estimator

This project aims to analyze the New York yellow taxi dataset and build a regression model to predict the possible price of a trip. The model can be used to predict the fare of a taxi trip when boarding a yellow taxi by hailing on the streets of New York, where the price is not known until the trip is completed. This project also includes a web application that allows users to enter the input variables and obtain a fare prediction from the trained model. The website can be accessd using following link:
https://amarendrakancharla-nyc-taxi-fare-predictor-home-onnnsu.streamlit.app/

### Data 
The data was obtained from the website https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page. The data used for this project was “Yellow taxi trip records” from this website for all months of year 2022. The data files were separate for each month of the year and in the format of parquet files for reducing the size of the file. 

### Merging of data
Since the data for all months is in different files they must be merged before proceeding forward.  One issue was that after reading one of the files into a panda’s data frame, the memory it took in the RAM was high. So, after looking at the info about the columns it has been noticed that the columns have wrong datatypes assigned to them. So, two functions were created one for converting the discrete column to category datatype and the other to change the data type of the continuous columns to the least memory taking datatype by checking the minimum and maximum values present in the columns (for example converting from int32 to int8 or float64 to float16 etc.) [1]. After transforming the columns datatypes using these functions the memory taken by most files was reduced by almost 50% per file. Next created some functions to read the files automatically into data frame and then apply the datatype transformations. Next other another function was created to merge all the data frames together to create initial merged dataset. The initial merged dataset has about 39M rows of data.

### Initial visualization of data
To understand the dataset better initial analysis was performed. The commands info() and describe() were used to understand the total values present in each column, non-null values and the min, max, mean and other statistics about the continuous columns.  

### Feature Engineering new columns 
New columns were feature engineered to better get understand the data and outliers. From the trip start datetime and trip end datetime, column duration of trip, trip start & end day, trip start & end day of week, trip start & end month, trip start & end hour were obtained. Another column was time of the day (morning, afternoon, evening, night) based on the trip start & end hour. Speed was another column which was obtained by dividing trip distance by duration of the trip. 

### Initial EDA
Univariate analysis of each column present is the dataset was done. For categorical variables the distribution of the data in column was observed. For continuous variables boxplot and histograms were plotted to understand the distribution and identify the outliers. It was observed that there were several outliers, nan values and unwanted values specific to a column in the data. 

### Handling data
There were 1368303 nan values in the 5 columns of the dataset. And these nan values are all present in the same rows of the 5 columns. These columns cannot be handled with imputation techniques so, all the nan values were dropped. Next the duplicate rows were dropped.
From the histogram and boxplots of the continuous variables it was clear there were several outliers, some which are unusual, and some columns have values which must not be present according to the description of the dataset. This analysis is only for year 2022, but there were few trips data which were in other years, so all the rows which does not belong to year 2022 were dropped. For the trip duration column, it was observed that there were negative duration values and very large duration values (since a taxi driver can only work maximum of 12hrs per day and anything more than that on a single trip is an outlier). All the rows which stratify this condition were dropped. There were few trips where the duration was 0 or less than 60 sec, this could mean a voided trip or inaccurate data, so all the rows with 0 duration were dropped. There are very uncommon data in the trip distance column where the distance was high, and the duration was low and vice versa. So, to identify these rows the feature engineered column speed was used. Assuming that the upper limit of speed is 65 mph all the rows which have a speed greater than that and speed less than 0.5mph were dropped. Next the rows with zero trip distance or less than 0.1 mile were dropped. Next the rows which have a total trip cost less than 0 or equal to 0 were dropped, since these rows could mean a cancelled trip or correction for inaccurate data. Also, there were trips data where the fare was greater than $2000 which is unusual for a local taxi ride, so all the rows with fare > 2000 were dropped.
Further it was observed that the passenger column has rows with 0 passengers and according to the taxi services website the usual maximum number of passengers are about 6, so any rows with 0 passengers or passengers greater than 6 were dropped. According to the data description extra cost cannot be less than 0 or greater than 17, so all these rows were dropped. MTA tax levied on the trip can either be 0 or 0.5 according to data description, so all the rows with other values were dropped. Next the rows with tip amount > $200 were dropped. Similarly, the rows with tolls amount > $300 were dropped. According to data description airport fees of $1.25 is charged if the pickup zone is at JFK airport or LaGuardia airport, so all the rows with values other than 1.25 or 0 were dropped. Congestion surcharge (applied when the trip passes through certain zones of Manhattan) can either be $2.5 or 0, so rows with other values were dropped.  Similarly, improvement surcharge (which was levied on all trips from 2015 according to NYC taxi website) can only be $0.3 so the rows with all other values were dropped. In the end about 35M rows of data was left.
Next for further analysis columns pickup datetime and drop-off datetime columns were dropped since this information is captured by the feature engineered columns. There was an additional column of trip fare before adding the overhead charges this column was dropped since the total fare column is present. In addition, improvement surcharge and mta tax columns were dropped since all the values are same in this column. 

### Additional Analysis
Univariate analysis was performed again on the final cleaned dataset to check the data distribution. Bivariate analysis was performed on continuous variables to identify any underlying relations. Next correlation test was performed on the continuous variables to check if there were any highly related variables, to avoid multi-collinearity. To test for the significance of the categorical columns on target variable ANOVA test was used. The package used was statsmodels.api for overall significance and pairwise_tukeyhsd module to see if the means of one group differ from other (t-test within the groups).   
New data files for additional analysis –
Since the cleaned dataset is too big for memory, individual files for further analysis were created. 
To visualize how factors number of cabs, trip distance, trip duration and trip fare changes to pickup zones and drop off zones over the whole year or for each month based on different periods of time. So, on the cleaned dataset group by function was applied. For pickup zones the dataset was grouped by pickup zone and the respective period (hour, day of month, day of the week, time of the day or month) and the factors columns were aggregated to obtain the average. For each month data in group by month column was added the month period was removed. Similarly, it was also done for drop-off locations. In total 18 different files were obtained in parquet format.
To plot these factors on the map there is a requirement of the geojson file with polygon coordinates of the zone along with ID that matches with the ID in the factors data frame. A shapefile of zones data was obtained from the same website as data, and which has several other information about the zones along with polygon coordinates. There was also an additional csv file which has some additional information about the zones. So, after reading the shape file and csv file into a data frames, they were both merged and duplicate columns were removed. The coordinates of the geometry were not in correct CRS, so the CRS was changes to EPSG 4326. Now the merged dataframe was converted to a geojson file and a new key called id was added along with value as location ID to the geojson dictionary and was downloaded for further analysis.  The cleaned main data frame only has zone IDs for pickup and drop-off locations, but the shape file has the names and other details. So, a function was created to which group’s the original data frame based on the necessary columns and then joins the necessary columns in shape file with this data frame to obtain the finale data frame. This function was used to obtain all the 18 necessary file.
Similarly for visualization of how factors change based on the pickup and drop off zone combined 9 files were obtained grouping by pickup, drop-off, and period. 
Further, for pydeck plot latitude and longitudes of the centroid of each zone was obtained using the polygon geometry coordinates. The tuple of longitude and latitude was created and added to data frame created from shape files and downloaded as a csv file. Further for this plot the coordinates of the polygon geometry needed to be a 2D array, but they were in form of MULTIPOINT, so converted these to required form and added to the dataframe before creating a csv file.

### Plots for visualization
For the visualization of the factors on map, plotly express’s choropleth maps (kind of like a heat map but with actual geographical map as base map) was used. The plot was separate for pickup and dropoff zones. The plot also has an animation of how the selected factor is changing over the selected period. 
For visualization of the factors changes based on the start zone and end zone of the trip plotly express bar plot was used.
For the final arc layer plot along with polygon layer pydeck was used. This has a polygon layer which highlights the start and end zones of the trip along with the arc layer.

### Train & Test data
To proceed further with building the regression model to avoid any bias the data is split into train and test data, so that any transformations performed are only based on the train data. Since the data is kind of time series since it has data belonging to different periods of time, stratified split (make sures the ratio of the data in the column selected is same in train and test data) was performed. For this sklearn’s train_test_split() function was used and the column selected was pickup hour for stratified split. This make sures that the ratio of data for each hour in train and test is same. This make sure that all the necessary data is available for proper training of the model.

### Data Transformation
The continuous data columns are highly skewed data, and for the model to properly work these data must be transformed. From various data transformation options from the scikit-learn library Min-Max scaler suited best for the data. Further for the categorical columns they must one-hot encoded before inputting to the model for training. Since the final ml model is being deployed it is not to transformer every feature manually based on the datatype. To automate this process, ColumnTransformer from sklearn was used to transform each column set separately before combining them later. The created column transformer was fitted on the train data and then both train and test data were transformed. It was not fit on the test data to avoid overfitting. 

### Applying Linear model
The transformed train data was used to train a linear regression model. The LinearRegresion from sklearn was used for training. After training the model was evaluated on the test data based on r2_score, mean absolute error, mean squared error, and mean absolute percentage error. The base regression was performing good without any additional regularization parameters. The scores obtained on the test data were, 
r2_score:  0.9695919380987292
mean_absolute_error:  1.038519183284114
mean_squared_error:  2.871868310605684
mean_absolute_percentage_error:  0.05200907878426217

### Applying Non-linear model
Tree based non-linear model was used. For the model catboost regressor was selected. The transformed train data was used for training purposes and same metrics as linear model were used to evaluate the model performance on test data. The base model without hyper tuning the parameters of the model was performing better than linear regression model. The scores were,
r2_score:  0.9859112515887144
mean_absolute_error:  0.43393371455965407
mean_squared_error:  1.954818129064982
mean_absolute_percentage_error:  0.02198162680934571

### Choosing the final model
It was clear from the scores of the test data that catboost model is performing better. Further the train scores and the test scores for the catboost model were very close so the model is not overfitting the data. For this project the interpretation of the importance of each column is not very important as opposed to the final prediction, so the catboost model was selected to proceed forward. The hyper parameter tuning of parameters for the catboost model was not performed as the model is performing well and lack of computation resources for tuning.

### Downloading the transformer and model
The column transformer is downloaded as a joblib file for applying the transformation on user input data. The trained model was downloaded as a pickle file for prediction of the final fare.

### Building streamlit website
This website has 4 pages home page, NYC zones map, factors visualization and fare predictor.
The home page contains some information of the motivation of this project and what is the use of this website.
The NYC zones map contains the plotly express choropleth map with the animation of period and tool tip indicate information about each zone. Two tabs were created one for pickup zones and other for dropoff zones. There previously downloaded 18 files and geojson files were used. This page has three parameters that user can choose from factor to visualize, month and the period. A function was created to read required files into a dataframe and then store them in a dictionary with a unique key (a tuple of different elements was created for each file to uniquely identify). These files were stored in the cache of streamlit for faster access. Similarly, the geojson file of zones is also read in and stored in cache. Next a function was created to return a plotly figure when the necessary inputs were provided. Since the user inputs differ from the actual values of the dataframe (like user select a month name but the dataframe has the month as number) few other dictionaries were created and stored in the session state for faster access. Based on the user inputs the figures are created and are plotted using streamlit commands. 
On streamlit if the user changes a single parameter the whole script runs from top to bottom, so it necessary to store large files and variables created in the cache for faster access. Also, to prevent the script from running after change in one parameter and wait till all parameters are changed, streamlit form is created which has the user input option that allows the script to only run after all the parameters are changes and the submit button is clicked.
The third page contains the visualization of the factors when travelling from a particular pickup location to dropoff locations. The remaining 9 files were used for this analysis. Like previous page the function to automatically read files as dataframe and store in a dictionary was used. Also, the geojson file was read in to get the zones names as the dataframe only has the location ID. Few additional dictionaries were created to have proper connection between user input and dataframe (like users select the name of pickup and dropoff locations but to access rows in the dataframe ID are required so these dictionaries help in accessing the ID’s based on names). A plotly express bar plot was used. 
The final page is the fare predictor, which takes about 11 inputs from the user and remaining 14 inputs are handled based on the 11 user inputs. In total the model has 25 inputs. For example, the user selects the pickup and dropoff locations and in background google distance matrix API is used to fetch the distance between these two locations and the duration it takes for the trip in a car. From this speed is calculated by dividing distance/duration. The user inputs the pickup time (the API can get the duration of the trip in future time as well) and since we have the trip duration, we can get the dropoff time. From pickup time and dropoff time other feature engineered inputs like pickup & dropoff hour, month, day etc can be obtained. There are other parameters which are fixed like the congestion surcharge is applied only if the trip passes through certain zones, parameters like these are handled in the background. All the parameters are then made into a dataframe which has the same shape as original dataframe. Then the transformer is loaded, and these parameters are transformed and then the loaded model predicts the fare based on user inputs. The previously created files that has the data of the latitude and longitude of the centroid of the zone is also loaded along with the polygon coordinates in 2D array form. Next a pydeck figure is created using two layers first is a polygon layer which uses the polygon coordinates data of zones and the second is the arc layer which uses the latitude and longitudes data of zones. This figure helps to visualize the pickup and dropoff location. 	
