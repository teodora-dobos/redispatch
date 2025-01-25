import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd
import numpy as np

df_redispatch = pd.read_csv('data/output/geo_redispatch_data.csv')

df_redispatch = df_redispatch[df_redispatch['GRUND_DER_MASSNAHME'] == 'Strombedingter Redispatch']

df_redispatch['BEGINN_DATUM'] = pd.to_datetime(df_redispatch['BEGINN_DATUM'])
df_redispatch_2024 = df_redispatch[df_redispatch['BEGINN_DATUM'].dt.year == 2024]

min_date = df_redispatch_2024['BEGINN_DATUM'].min()
max_date = df_redispatch_2024['BEGINN_DATUM'].max()

translation = {
    'Wirkleistungseinspeisung reduzieren': 'downward',
    'Wirkleistungseinspeisung erhöhen': 'upward',
    'Wirkleistungseinspeisung erh¿hen': 'upward',
    'Erneuerbar': 'RES',
    'Konventionell': 'conventional',
    'Sonstiges': 'others'
}

# Streamlit app configuration
st.set_page_config(layout="wide", page_title="Redispatch Map", page_icon="🌍")

# Header
st.header('Redispatch Data')

# Sidebar: calendar widget
today = pd.to_datetime('today')
value_date = today.replace(year=2024)

selected_date = st.sidebar.date_input(
    "📅 **Date**",
    value=value_date,
    min_value=min_date,
    max_value=max_date,
    help='Select a date from the calendar to view redispatch data for that specific day.'
)

view_selection = st.sidebar.selectbox("📊 **View**", ["Unit Type", "Direction"], help='Select the view for the data visualization. Option *Unit Type* highlights the type of the redispatched units, while option *Direction* indicates whether the units are upward or downward redispatched.')

unit_type_selection = st.sidebar.selectbox("⚡ **Unit Type**", ["All Types", "RES", "Conventional"], help='Select the type of units to display.')

direction_selection = st.sidebar.selectbox("↕️ **Direction**", ["All Directions", "Upward", "Downward"], help='Select the direction for the redispatch measures.')

# Filter data for the selected day
df_day = df_redispatch[(df_redispatch['BEGINN_DATUM'] == pd.Timestamp(selected_date)) & (~df_redispatch['Latitude'].isna()) & (~df_redispatch['Longitude'].isna())]

if unit_type_selection == 'RES':
    df_day = df_day[df_day['PRIMAERENERGIEART'] == 'Erneuerbar']
elif unit_type_selection == 'Conventional':
    df_day = df_day[df_day['PRIMAERENERGIEART'] == 'Konventionell']

if direction_selection == 'Downward':
    df_day = df_day[df_day['RICHTUNG'] == 'Wirkleistungseinspeisung reduzieren']
elif direction_selection == 'Upward':
    df_day = df_day[df_day['RICHTUNG'].isin(['Wirkleistungseinspeisung erhöhen', 'Wirkleistungseinspeisung erh¿hen'])]

locations = [
    {
        "name": row["BETROFFENE_ANLAGE"],
        "Latitude": row["Latitude"],
        "Longitude": row["Longitude"],
        "Richtung": row["RICHTUNG"],
        "GESAMTE_ARBEIT_MWH": row["GESAMTE_ARBEIT_MWH"],
        "PRIMAERENERGIEART": row["PRIMAERENERGIEART"],
    }
    for _, row in df_day.iterrows()
]

# Daily Statistics
df_statistics = df_redispatch[df_redispatch['BEGINN_DATUM'] == pd.Timestamp(selected_date)]

if unit_type_selection == 'RES':
    df_statistics = df_statistics[df_statistics['PRIMAERENERGIEART'] == 'Erneuerbar']
elif unit_type_selection == 'Conventional':
    df_statistics = df_statistics[df_statistics['PRIMAERENERGIEART'] == 'Konventionell']

if direction_selection == 'Downward':
    df_statistics = df_statistics[df_statistics['RICHTUNG'] == 'Wirkleistungseinspeisung reduzieren']
elif direction_selection == 'Upward':
    df_statistics = df_statistics[df_statistics['RICHTUNG'].isin(['Wirkleistungseinspeisung erhöhen', 'Wirkleistungseinspeisung erh¿hen'])]

df_statistics['GESAMTE_ARBEIT_MWH'] = pd.to_numeric(
    df_statistics['GESAMTE_ARBEIT_MWH'].apply(lambda x: str(x).replace(',', '.') if isinstance(x, str) else x),
    errors='coerce'
)

total_volume_day = df_statistics['GESAMTE_ARBEIT_MWH'].sum()
formatted_total_volume_day = f"{total_volume_day:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
if formatted_total_volume_day.endswith(",00"):
    formatted_total_volume_day = formatted_total_volume_day[:-3]

total_units_day = len(df_statistics['BETROFFENE_ANLAGE'].unique().tolist())
total_measures_day = len(df_statistics)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Redispatch volume", value=f"{formatted_total_volume_day} MWh", help='The sum of the total work values corresponding to the redispatched units for the selected date.')
with col2:
    st.metric(label="Redispatched units", value=f"{total_units_day}", help='Number of redispatched units for the selected date.')
with col3:
    st.metric(label="Redispatch measures", value=f"{total_measures_day}", help='Number of redispatched measures for the selected date.')

# Create the map
germany_map = folium.Map(location=[51.1657, 10.4515], zoom_start=6)

values = [float(loc['GESAMTE_ARBEIT_MWH'].replace(',', '.')) for loc in locations]
min_val, max_val = 0, 0
if len(values) > 0:
    min_val, max_val = np.min(values), np.max(values)

def prepare(loc):
    gesamt_arbeit = float(loc['GESAMTE_ARBEIT_MWH'].replace(',', '.'))  
    radius = 10
    if max_val != min_val:
        radius = 5 + (gesamt_arbeit - min_val) / (max_val - min_val) * (20 - 5)
    return radius

if view_selection == 'Unit Type':
    for loc in locations:
        radius = prepare(loc)
        tooltip_content = f"Unit: {loc['name']}<br>Direction: {translation.get(loc['Richtung'], loc['Richtung'])}<br>Quantity: {translation.get(loc['GESAMTE_ARBEIT_MWH'], loc['GESAMTE_ARBEIT_MWH'])} MWh<br>Type: {translation.get(loc['PRIMAERENERGIEART'], loc['PRIMAERENERGIEART'])}"
        folium.CircleMarker(
            location=[loc["Latitude"], loc["Longitude"]],
            radius=radius,
            color="green" if loc['PRIMAERENERGIEART'] == "Erneuerbar" else "red" if loc['PRIMAERENERGIEART'] == "Konventionell" else 'yellow',
            fill=True,
            fill_opacity=0.7,
            tooltip=tooltip_content
        ).add_to(germany_map)

elif view_selection == 'Direction':
    for loc in locations:
        radius = prepare(loc)
        tooltip_content = f"Unit: {loc['name']}<br>Direction: {translation.get(loc['Richtung'], loc['Richtung'])}<br>Quantity: {translation.get(loc['GESAMTE_ARBEIT_MWH'], loc['GESAMTE_ARBEIT_MWH'])} MWh<br>Type: {translation.get(loc['PRIMAERENERGIEART'], loc['PRIMAERENERGIEART'])}"
        folium.CircleMarker(
            location=[loc["Latitude"], loc["Longitude"]],
            radius=radius,
            color="orange" if loc['Richtung'] in ['Wirkleistungseinspeisung erhöhen', 'Wirkleistungseinspeisung erh¿hen'] else "blue",
            fill=True,
            fill_opacity=0.7,
            tooltip=tooltip_content 
        ).add_to(germany_map)

st_folium(germany_map, width=1200, height=600)
