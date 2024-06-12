# Project 2

import streamlit as st
st.set_page_config(layout='wide')
import altair as alt
import pandas as pd
#import geopandas as gpd

# The first part of the code focuses on loading, preprocessing, and merging datasets, 
# introducing geospatial information for visualizations.

alt.data_transformers.disable_max_rows()
crash = pd.read_csv('data-collisions-vehicles-proj2.csv')

crash['CRASH DATE'] = pd.to_datetime(crash['CRASH DATE'], format='%Y-%m-%dT%H:%M:%SZ')
crash['Month'] = crash['CRASH DATE'].dt.strftime('%B')
crash['Weekday'] = crash['CRASH DATE'].dt.day_name()

weather = pd.read_csv('weather2018.csv')

selected_columns = ['datetime', 'icon']
weather_subset = weather[selected_columns]
weather_subset['datetime'] = pd.to_datetime(weather_subset['datetime'], format='%Y-%m-%d')

crash_w = pd.merge(crash, weather_subset, left_on='CRASH DATE', right_on='datetime', how='left')
crash_w = crash_w.drop(columns='datetime')
crash_w.rename(columns={'icon': 'weather'}, inplace=True)

options = ['June', 'July', 'August', 'September']
labels = [option + ' ' for option in options]

crash_bor = crash_w.dropna(subset=['BOROUGH']).copy()
crash_bor['DayMonth'] = crash_bor['CRASH DATE'].dt.strftime('%d-%m')
crash_bor['Hour'] = pd.to_datetime(crash_bor['CRASH TIME'], format='%H:%M', errors='coerce').dt.hour

borough_monthly_crash = crash_bor.groupby(['BOROUGH', 'Month', 'weather']).size().reset_index(name='total_crashes')

borough_mapping = {
    'Staten Island': 5,
    'Queens': 4,
    'Brooklyn': 3,
    'Manhattan': 1,
    'Bronx': 2
}

borough_monthly_crash['boro_code'] = borough_monthly_crash['BOROUGH'].map(borough_mapping)

# The second part summarizes the visualization and links charts together using prepared selections. 
# The plots addressing the first and second questions dynamically respond to changes in months. 
# The graph prepared for the third question is updated through a heatmap and changing the hour on the second chart. 
# Finally, the plot answering the fourth question reacts to clicking on the heatmap. 
# I set matching and consistent color palettes for all charts to create a cohesive whole visualization.

options = ['June', 'July', 'August', 'September']
labels = [option + ' ' for option in options]

input_dropdown = alt.binding_radio(
    options=options + [None],
    labels=labels + ['All'],
    name='Month: '
)
selection = alt.selection_point(
    fields=['Month'],
    bind=input_dropdown,
)

selection2 = alt.selection_point(fields=['Month', 'weather'])

legend = alt.Chart(crash_bor).mark_rect().encode(
    alt.Y('Month:N').axis(orient='left'),
    x='weather:O',
    color=alt.Color('count()', scale=alt.Scale(scheme='oranges', type='log')),
    tooltip=['Month', 'weather', 'count()']
).properties(
    width=350,
    height=300,
    title='Weather Summary during each Month'
).add_params(
    selection2
)

brush = alt.selection_interval(encodings=['x'])

q1 = alt.Chart(crash_w).mark_rect().encode(
    x='weather:O',
    y='VEHICLE TYPE CODE 1:O',
    color=alt.Color('count()', scale=alt.Scale(scheme='tealblues', type='log')),
    tooltip=['weather:O', 'VEHICLE TYPE CODE 1:O', 'count()']
).properties(
    width=350,
    height=300,
).add_params(
    selection
).transform_filter(
    selection
)

q2 = alt.Chart(crash_bor).mark_line(point=True).encode(
    x=alt.X('Hour:O', title='Hour'),
    y=alt.Y('count()', title='Number of Accidents'),
    color=alt.Color('BOROUGH:N', title='Area' , scale=alt.Scale(scheme='tableau10')),
    tooltip=['Hour', 'BOROUGH', 'count()']
).properties(
    width=900,
    height=300,
    title='Line Plot of Accidents by Hour and Borough'
).add_params(
    selection,
    brush
).transform_filter(
    selection
)

q3_bar = alt.Chart(crash_bor).mark_bar().encode(
    x=alt.X('BOROUGH:N', title='Borough'),
    color='BOROUGH:N',
    y=alt.Y('count()', title='Number of Observations'),
    column='Weekday:N'
).properties(
    width=150,
    height=400
).add_params(
    selection2
).transform_filter(
    selection2 & brush
)

q4 = alt.Chart(crash_bor).mark_line(point=True).encode(
    x=alt.X('DayMonth:O', title='Hour'),
    y=alt.Y('count()', title='Number of Accidents'),
    color=alt.Color('BOROUGH:N', title='Area' , scale=alt.Scale(scheme='tableau10')),
    tooltip=['BOROUGH:N', 'count()', 'DayMonth', 'weather']
).properties(
    width=850,
    height=400,
    title='Line Plot of Accidents by Hour and Borough'
).add_params(
    selection2
).transform_filter(
    selection2
)

st.title('Information visualization')

(q1 | q2 | legend) & ( q4 | q3_bar)