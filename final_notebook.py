# -*- coding: utf-8 -*-
"""final_notebook.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_W1rVPvjDTXpAoxkwm_zVycvFh_Ch3gK
"""

!unzip /content/drive/MyDrive/HomeWork02/nyc_taxi_data.zip -d data

import dask.dataframe as dd
from dask.distributed import Client
from dask.cache import Cache
import gc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

layout_options = {
    'paper_bgcolor':"#383838",
    'plot_bgcolor':'#383838',
    'title_font': dict(color='white'),
    'legend_font': dict(color='white'),
    'yaxis':dict(color="white"),
    'xaxis':dict(color="white")
    }

from google.colab import drive
drive.mount('/content/drive/')

PATH = '/content/drive/MyDrive/pre_data'
naming = lambda x: f'part-{x}.parquet'
TEMP_PATH = '/content/temp'
TS_PATH = '/content/drive/MyDrive/'

import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller

def test_stationarity(timeseries,i):

    # Extract the column you want to test for stationarity
    column_name = timeseries.columns[i]
    timeseries = timeseries[column_name]

    #Determing rolling statistics
    rolmean = timeseries.rolling(window=12).mean()
    rolstd = timeseries.rolling(window=12).std()

    # Plot rolling statistics:
    orig = plt.plot(timeseries, color='blue',label='Original')
    mean = plt.plot(rolmean, color='red', label='Rolling Mean')
    std = plt.plot(rolstd, color='black', label = 'Rolling Std')
    plt.legend(loc='best')
    plt.title('Rolling Mean & Standard Deviation')
    plt.show(block=False)
    # trace_orig = go.Scatter(x=timeseries.index, y=timeseries, mode='lines', name=column_name)
    # trace_mean = go.Scatter(x=rolmean.index, y=rolmean, mode='lines', name='Rolling Mean')
    # trace_std = go.Scatter(x=rolstd.index, y=rolstd, mode='lines', name='Rolling Std')
    # data = [trace_orig, trace_mean, trace_std]


    # Create the layout
    # layout = go.Layout(title='Rolling Mean & Standard Deviation',height=400, **layout_options)


    # Create the figure
  #  fig = go.Figure(data=data, layout=layout)

    # Show the figure
    # fig.show()
    #Perform Dickey-Fuller test:
    print('Results of Dickey-Fuller Test:')
    dftest = adfuller(timeseries, autolag='AIC')
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
    for key,value in dftest[4].items():
        dfoutput['Critical Value (%s)'%key] = value
    print(dfoutput)

df = dd.read_parquet('/content/data/nyc_taxi_alt/')

df.head()

df.tail()

df.isna().sum().compute()

df["airport_fee"] = df["airport_fee"].fillna(0)
df["congestion_surcharge"] = df["congestion_surcharge"].fillna(0)

df = df.dropna()

df.sample(frac=0.1, replace=False).compute()

df.columns

def get_bounds(df, col, upper_bound, lower_bound):
  return df[(df[col] > lower_bound) & (df[col] < upper_bound)]

df = get_bounds(df, "total_amount", 100, 5)

df.to_parquet(PATH, name_function=naming)

df = dd.read_parquet(PATH)

df = df[((df["tpep_pickup_datetime"].dt.year <= 2022) & (df["tpep_pickup_datetime"].dt.year >= 2019))|((df["tpep_dropoff_datetime"].dt.year <= 2022)&(df["tpep_dropoff_datetime"].dt.year >= 2019))]

df = df[df["tpep_dropoff_datetime"] > df["tpep_pickup_datetime"]]

df.shape[0].compute()

df["passenger_count"].max().compute()

df = df[(df["passenger_count"] > 0) & (df["passenger_count"] < 10)]

df.shape[0].compute()

df.to_parquet(PATH, name_function=naming)

"""##Build Time Series"""

df = dd.read_parquet(PATH)

temp_serie = df.sample(frac=0.3, replace=False)

# temp_serie['hour'] = temp_serie["tpep_pickup_datetime"].dt.hour
# temp_serie["day"] = temp_serie["tpep_pickup_datetime"].dt.dayofweek
# temp_serie["year"] = temp_serie["tpep_pickup_datetime"].dt.year
temp_serie['tpep_pickup_hour'] = temp_serie["tpep_pickup_datetime"].dt.floor(freq="H")

ts = temp_serie.groupby(by=['tpep_pickup_hour', 'VendorID'])
ts = ts.agg({'trip_distance': 'count', 'total_amount': 'sum'})
ts = ts.sort_values(by=['tpep_pickup_hour', 'VendorID'])
ts = ts.reset_index()
ts = ts.rename(columns={'trip_distance': 'trips_count'})

ts_df = ts.compute()

del df
del ts

ts_df.to_csv('/content/drive/MyDrive/Vendors/ts.csv', index=False)

ts_df = ts_df.set_index('tpep_pickup_hour')

vendor1 = ts_df[ts_df['VendorID']==1].last('W')
vendor2 = ts_df[ts_df['VendorID']==2].last('W')
vendor1 = vendor1.reset_index()
vendor2 = vendor1.reset_index()

vendor1.columns

values_column = 'total_amount'
fig = px.line(ts_df, x=vendor1['tpep_pickup_hour'], y=vendor1[values_column])
fig.add_scatter(x=vendor1['tpep_pickup_hour'], y=vendor1[values_column])
fig.update_layout(height=400, title='Total Amount',**layout_options)
fig.show()

fig = px.line(ts_df, x=vendor2['tpep_pickup_hour'], y=vendor2[values_column])
fig.add_scatter(x=vendor1['tpep_pickup_hour'], y=vendor1[values_column])
fig.add_scatter(x=vendor2['tpep_pickup_hour'], y=vendor2[values_column])
fig.update_layout(height=400, title='Total Amount',**layout_options)
fig.show()

"""#Stationarity for Vendor1

##Trips_count
"""

vendor1.columns

test_stationarity(vendor1,3)

"""## Travel Counts"""

test_stationarity(vendor1,3)

"""**Result**

This TS is *Stationary* because the test Statistic value is less than the critical value in both, so we reject the null hypothis and we say that this TS is *Stationary*

#Stationary test for Vendor2

##Total Revenue
"""

test_stationarity(vendor2 , 2)

"""##Travels Count"""

test_stationarity(vendor2 , 3)

"""**Result**

This TS is *Stationary* because the test Statistic value is less than the critical value in both, so we reject the null hypothis and we say that this TS is *Stationary*
"""

vendor1.columns

# /content/drive/MyDrive/Vendors
vendor1.to_csv('/content/drive/MyDrive/Vendors/vendor1.csv', index=False)

vendor2.to_csv('/content/drive/MyDrive/Vendors/vendor2.csv', index=False)



import dask.dataframe as dd
import pandas as pd

from google.colab import drive
drive.mount('/content/drive')

data1 = dd.read_parquet('/content/drive/MyDrive/pre_data')

data1.shape[1]

"""data1.head()"""

ddff = dd.read_csv('/content/drive/MyDrive/HomeWork02/taxi_zone_lookup.csv')

data1 = data1.rename(columns={"PULocationID": "LocationID"})

data2 = dd.merge(data1 ,ddff[["LocationID","Zone"]], on="LocationID")

data2 = data2.drop("LocationID", axis=1)

data2 = data2.rename(columns={"Zone": "source_zone","DOLocationID": "LocationID"})

data2 = dd.merge(data2 ,ddff[["LocationID","Zone"]], on="LocationID")

data2 = data2.drop("LocationID", axis=1)
data2 = data2.rename(columns={"Zone": "destination_zone"})

data2 = data2.rename(columns={"source_zone": "Zone"})

data2 = dd.merge(data2 ,ddff[["Zone","Borough"]], on="Zone")
data2

data2 = data2.rename(columns={"Zone": "source_zone","Borough":"source_borough"})

data2 = data2.rename(columns={"destination_zone": "Zone"})

data2 = dd.merge(data2 ,ddff[["Zone","Borough"]], on="Zone")
data2

data2 = data2.rename(columns={"Zone": "destination_zone","Borough":"destination_borough"})

data2.to_parquet('/content/Temp/', name_function=lambda x: f'part-{x}.parquet' )

data2 = dd.read_parquet('/content/Temp/')

data2['location_pairs'] = data2.map_partitions(lambda partition:
    [" -> ".join(sorted([row.source_zone, row.destination_zone])) for row in partition.itertuples()], meta=('location_pairs', 'object'))

data2.to_parquet('/content/drive/MyDrive/TT', name_function=lambda x: f'part-{x}.parquet' )

data2 = dd.read_parquet('/content/drive/MyDrive/TT')

payment_type_name = {
      1: "Credit card",
      2: "Cash",
      3: "No charge",
      4: "Dispute",
      5: "Unknown",
      6: "Voided trip"
}

data2["payment_type_name"] = data2["payment_type"].map(payment_type_name)

vendor = {
    1: "Creative Mobile Technologies, LLC",
    2: "VeriFone Inc"
}

data2["vendor"] = data2["VendorID"].map(vendor)

rate_code = {
    1: "Standard rate",
    2: "JFK",
    3: "Newark",
    4: "Nassau or Westchester",
    5: "Negotiated fare",
    6: "Group ride"
}

data2["rate_code"] = data2["RatecodeID"].map(rate_code)

data2['trip'] = (data2['tpep_dropoff_datetime'] - data2['tpep_pickup_datetime']).astype('timedelta64[s]')
data2['trip_duration'] = data2['trip']/60

data2['trip_distance'] = data2['trip_distance']* 1.609344

data2.to_parquet('/content/drive/MyDrive/Temp', name_function=lambda x: f'part-{x}.parquet' )

data2 = dd.read_parquet('/content/drive/MyDrive/Temp')

freq = data2["location_pairs"].value_counts().compute()

freq1 = freq.reset_index()

freq1

def freq_cal(x):
    if x >= freq["location_pairs"].quantile(0.9):
        return 'more_common'
    elif x >= freq["location_pairs"].quantile(0.5):
        return 'common'
    elif x >= freq["location_pairs"].quantile(0.3):
        return 'less_common'
    else:
      return "rare"

freq1.columns = ['location_pairs', 'count']
freq1['count']

bins = [0, freq1['count'].quantile(0.3),freq1['count'].quantile(0.5) , freq1['count'].quantile(0.9), freq1['count'].max()]
labels = ['rare' ,'less_common', 'common', 'more_common']
freq1['class'] = pd.cut(freq1['count'], bins=bins, labels=labels, include_lowest=True)

data2 = data2.merge(freq1[["location_pairs", "class"]], on="location_pairs")

data2 = data2.rename(columns={"class": "trip_class"})

data2["trip_class"].head()

data2.to_parquet('/content/drive/MyDrive/TT', name_function=lambda x: f'part-{x}.parquet' )

"""#Exploration And Analysis


"""

import dask.dataframe as dd
import pandas as pd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

data2 = dd.read_parquet('/content/drive/MyDrive/New folder/TT')

data2

"""##A

###1
"""

revenue_by_vendor = data2.groupby('vendor')['total_amount'].sum()

revenue_by_vendor_pandas = revenue_by_vendor.compute()

revenue_by_vendor_pandas = revenue_by_vendor_pandas.reset_index()
revenue_by_vendor_pandas.head()

layout_options = {
    'paper_bgcolor':"#383838",
    'plot_bgcolor':'#383838',
    'title_font': dict(color='white'),
    'legend_font': dict(color='white'),
    'yaxis':dict(color="white"),
    'xaxis':dict(color="white")
    }

import plotly.graph_objects as go
fig = go.Figure(data=[go.Pie(labels=revenue_by_vendor_pandas['vendor'], values=revenue_by_vendor_pandas['total_amount'])])
fig.update_layout(**layout_options)
fig.show()

"""###2"""

revenue_by_borough =  data2.groupby('source_borough')['total_amount'].sum()

revenue_by_borough_panda = revenue_by_borough.compute()

revenue_by_borough_panda = revenue_by_borough_panda.reset_index()
revenue_by_borough_panda.head()

import plotly.graph_objects as go
fig = go.Figure(data=[go.Pie(labels=revenue_by_borough_panda['source_borough'], values=revenue_by_borough_panda['total_amount'])])
fig.update_layout(**layout_options)
fig.show()

"""###3"""

revenue_by_payment = data2['payment_type_name'].value_counts()

revenue_by_payment_pandas = revenue_by_payment.compute()

revenue_by_payment_pandas = revenue_by_payment_pandas.reset_index()
revenue_by_payment_pandas = revenue_by_payment_pandas.rename(columns={"payment_type_name":"total","index":"name"})
revenue_by_payment_pandas.head()

fig = px.bar(revenue_by_payment_pandas, y="total", x="name", title="")
fig.update_layout(**layout_options)
fig.show()

"""###4"""

data2 = dd.read_parquet('/content/drive/MyDrive/New folder/TT')

revenue_by_class = data2.groupby('payment_type_name')['trip_class'].count()

revenue_by_class_pandas = revenue_by_class.compute()

revenue_by_class_pandas = revenue_by_class_pandas.reset_index()
revenue_by_class_pandas.head()

fig = px.sunburst(revenue_by_class_pandas, path=['payment_type_name'], values='trip_class')
fig.update_layout(**layout_options)
fig.show()

"""###5"""

data3 = data2[['tip_amount','total_amount','passenger_count','trip_distance','fare_amount','tolls_amount']]

popo = data3.corr()
popo.head()

"""نلاحظ إرتباط قوي بين المسافة المقطوعة والكلفة،  بالإضافة إلى ارتباط جيد بين الإكرامية والكلفة الكلية

###6
"""

data4 = data2[['trip_class','total_amount','trip_duration','trip_distance']]

mean1 = data4.groupby('trip_class')['total_amount'].mean()

mean1_pandas = mean1.compute()

deviation1 = data4.groupby('trip_class')['total_amount'].std()

deviation1_pandas = deviation1.compute()

total_amount_data = {
    'mean_total_amount' : mean1_pandas,
    'deviation_total_amount' :deviation1_pandas
}

df = pd.DataFrame(total_amount_data)
df

fig = px.bar(df,title='total_amount')
fig.update_layout(**layout_options)
fig.show()

mean2 = data4.groupby('trip_class')['trip_duration'].mean()

mean2_pandas = mean2.compute()

deviation2 = data4.groupby('trip_class')['trip_duration'].std()

deviation2_pandas = deviation2.compute()

trip_duration_data = {
    'mean_trip_duration' : mean2_pandas,
    'deviation_trip_duration' :deviation2_pandas
}

df1 = pd.DataFrame(trip_duration_data)
df1

fig = px.bar(df1,title='trip_duration')
fig.update_layout(**layout_options)
fig.show()

mean3 = data4.groupby('trip_class')['trip_distance'].mean()

mean3_pandas = mean3.compute()

deviation3 = data4.groupby('trip_class')['trip_distance'].std()

deviation3_pandas = deviation3.compute()

trip_distance_data = {
    'mean_trip_duration' : mean3_pandas,
    'deviation_trip_duration' :deviation3_pandas
}

df2 = pd.DataFrame(trip_distance_data)
df2

fig = px.bar(df1,title='trip_distance')
fig.update_layout(**layout_options)
fig.show()

"""###7"""

vendor1 = pd.read_csv('/content/drive/MyDrive/New folder/Vendors/vendor1.csv')
vendor2 = pd.read_csv('/content/drive/MyDrive/New folder/Vendors/vendor2.csv')

"""vendor 1

total amount
"""

total_revenue1  = vendor1['total_amount']
plot_acf(total_revenue1, lags=50);
plt.tight_layout()

"""trips count"""

travels_count1  = vendor1['trips_count']
plot_acf(travels_count1, lags=50);
plt.tight_layout()

"""vendor2

total amount
"""

total_revenue2  = vendor2['total_amount']
plot_acf(total_revenue2, lags=50);
plt.tight_layout()

"""trips count"""

travels_count2  = vendor2['trips_count']
plot_acf(travels_count2, lags=50);
plt.tight_layout()

"""###8"""



rolling_mean1 = vendor1[['trips_count' , 'total_amount']].rolling(window=7).mean()

rolling_mean2 = vendor2[['trips_count' , 'total_amount']].rolling(window=7).mean()

import plotly.graph_objects as go

x = vendor1.index
y1 = vendor1['trips_count']
y2 = rolling_mean1['trips_count']
fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y1, mode='lines', name='Original Time Series'))
fig.add_trace(go.Scatter(x=x, y=y2, mode='lines', name='Rolling Mean'))
fig.update_layout(title='Line Chart', xaxis_title='X Axis', yaxis_title='Y Axis')
fig.show()

import plotly.graph_objects as go

x = vendor2.index
y1 = vendor2['trips_count']
y2 = rolling_mean2['trips_count']
fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y1, mode='lines', name='Original Time Series'))
fig.add_trace(go.Scatter(x=x, y=y2, mode='lines', name='Rolling Mean'))
fig.update_layout(title='Line Chart', xaxis_title='X Axis', yaxis_title='Y Axis')
fig.show()

"""## B"""

pp = pd.read_csv('/content/drive/MyDrive/New folder/ts.csv')

from prophet import Prophet
from prophet.plot import (plot_plotly, plot_components_plotly,
                          plot_seasonality_plotly,
                          plot_forecast_component_plotly)

pp

pp = pp.rename(columns={'tpep_pickup_hour': 'ds', 'trips_count': 'y'})

fig = px.line(pp, x='ds', y='y', width=700, height=400)
fig.update_layout(**layout_options)
fig.show()

model_a = Prophet(seasonality_mode='additive',yearly_seasonality=4)
model_a.fit(pp)
forecast_a = model_a.predict()

fig = plot_plotly(model_a, forecast_a, xlabel='Date',
                  figsize=(700, 550))
fig.update_layout(title='additive seasonality',
                 **layout_options)
fig.show()

model_m = Prophet(seasonality_mode='multiplicative',
                  yearly_seasonality=4)
model_m.fit(pp)
forecast_m = model_m.predict()

fig = plot_plotly(model_m, forecast_m, xlabel='Date',
                  figsize=(700, 550))
fig.update_layout(title=' multiplicative seasonality',
                  **layout_options)
fig.show()

"""نلاحظ الانخفاض الكبير في عدد الطلبات هي مابين عامين 2020 و 2021 وهي فترة ذروة انتشار وباء COVID19 وحالة الحجر الصحي"""

