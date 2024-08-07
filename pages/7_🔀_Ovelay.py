import streamlit as st
from datetime import date
import polars as pl
import pandas as pd
import numpy as np
from scipy.stats import skew, kurtosis, shapiro, norm, spearmanr, iqr
import plotly.express as px
import plotly.graph_objects as go
from itertools import combinations
import os
import sys
from dotenv import load_dotenv
import os
import plotly.figure_factory as ff

# To set the environement
load_dotenv()
px.set_mapbox_access_token(os.getenv("MAPBOX_TOKEN"))

class map:
    # Options
    # Allowed values which do not require a Mapbox API token are 
        # 'open-street-map', 'white-bg', 'carto-positron', 'carto-darkmatter', 'stamen- terrain', 'stamen-toner', 'stamen-watercolor'. 
        # Allowed values which do require a Mapbox API token are 
        # 'basic', 'streets', 'outdoors', 'light', 'dark', 'satellite', 'satellite- streets'.
    _mapbox_style = [
        'basic', 'streets', 'outdoors', 'light', 'dark', 'satellite', 'satellite- streets',
        'open-street-map', 'white-bg', 'carto-positron', 'carto-darkmatter', 'stamen-terrain', 'stamen-toner', 'stamen-watercolor'
    ]
    _color_scheme = [
        'blues', 'aggrnyl', 'agsunset', 'algae', 'amp', 'armyrose', 
        'balance', 'blackbody', 'bluered', 'blugrn', 'bluyl', 'brbg',
        'brwnyl', 'bugn', 'bupu', 'burg', 'burgyl', 'cividis', 'curl',
        'darkmint', 'deep', 'delta', 'dense', 'earth', 'edge', 'electric',
        'emrld', 'fall', 'geyser', 'gnbu', 'gray', 'greens', 'greys',
        'haline', 'hot', 'hsv', 'ice', 'icefire', 'inferno', 'jet',
        'magenta', 'magma', 'matter', 'mint', 'mrybm', 'mygbm', 'oranges',
        'orrd', 'oryel', 'oxy', 'peach', 'phase', 'picnic', 'pinkyl',
        'piyg', 'plasma', 'plotly3', 'portland', 'prgn', 'pubu', 'pubugn',
        'puor', 'purd', 'purp', 'purples', 'purpor', 'rainbow', 'rdbu',
        'rdgy', 'rdpu', 'rdylbu', 'rdylgn', 'redor', 'reds', 'solar',
        'spectral', 'speed', 'sunset', 'sunsetdark', 'teal', 'tealgrn',
        'tealrose', 'tempo', 'temps', 'thermal', 'tropic', 'turbid',
        'turbo', 'twilight', 'viridis', 'ylgn', 'ylgnbu', 'ylorbr', 'ylorrd'
    ]
    _district_code_list = ['14_1', '13_1', '12_7', '10_8', '10_1', '10_5', '10_2', '8_3', '7_4', '1_2']
    _state_code_list = [14, 13, 12, 10, 8, 7, 1]
    _district_name_list = [
        'Gombak', 'Johor Bahru', 'Kinta', 'Klang', 'Kota Kinabalu',
        'Kuching', 'Petaling', 'Timur Laut', 'Ulu Langat', 'W.P. Kuala Lumpur'
    ]

    def read_data():
        gp_df = pl.read_parquet("./data/information/gp_list.parquet")

        population = pl.read_parquet("./data/information/ascii_household_and_gp.parquet")\
                        .filter(pl.col("code_state_district").is_in(map._district_code_list))

        return population, gp_df

def str_overlay_analysis() -> None:
    # Header of the page
    st.markdown(""" <style> .header {font-size:40px; text-transform: capitalize; font-variant: small-caps; text-align: center; background-color: #FF0000}
                            .subheader {font-size:20px; text-transform: capitalize; font-variant: small-caps; text-align: center}
                            .body_header {font-size:20px; text-transform: capitalize; font-variant: small-caps; text-align: center; background-color: #87CEEB}
                            .red_header {font-size:20px; text-transform: capitalize; font-variant: small-caps; text-align: center; background-color: #87CEEB}
                            .stProgress .st-bo {background-color: #87CEEB} 
                            .streamlit-expanderHeader {font-size:16px; text-align: center; background-color: #87CEEB}
                    </style> """, unsafe_allow_html = True)

    # Title
    st.divider()
    st.markdown("""<p class="header">STR Population and SPM GPs Overlay Analysis</p>""", unsafe_allow_html=True)
    st.markdown(f'<p class="subheader">Last Update = {date(2024, 6, 28)}</p>', unsafe_allow_html=True)
    st.divider()

    # Load the data
    population, gp_df = map.read_data()

    # To put option for choropleth plot
    col1, col2 = st.columns(2)
    with col1:
        color_continuous_scale = st.selectbox("color_continuous_scale", options=map._color_scheme)

        # To select district
        district_selection = st.multiselect("Districts", options=population.sort("district").select("district").to_pandas()["district"].unique())
        if district_selection != []:
            population = population.filter(pl.col("district").is_in(district_selection))
            gp_df = gp_df.filter(pl.col("district").is_in(district_selection))

        # For density map radius
        marker = st.slider("To change to Marker", min_value=1, max_value=100, value=20)

        # For Hexagon
        nx_hexagon = st.slider("N Hexagon", min_value = 100, max_value=10000, value = 1500)

    with col2:
        mapbox_style = st.selectbox("Mapbox Style", options=map._mapbox_style)

        # To select parlimen
        parlimen = st.multiselect("Parlimen", options=population.sort("parlimen").select("parlimen").to_pandas()["parlimen"].unique())
        if parlimen != []:
            population = population.filter(pl.col("parlimen").is_in(parlimen))

        # To select opacity for density map
        opacity = st.slider("Opacity for Density Map/ Hexbin Map", min_value=0.1, max_value=1.0, value=0.5, step=0.05)

        # Marker size
        marker_size = st.slider("Marker Size", min_value = 1, max_value = 50, value = 20)

    gp_df = gp_df.to_pandas()

    population_fig = ff.create_hexbin_mapbox(
        data_frame=population.select("lat", "lon", "estimated_str").to_pandas(),
        lat="lat", 
        lon="lon",
        agg_func=np.sum,
        color = "estimated_str",
        color_continuous_scale=color_continuous_scale,
        mapbox_style = mapbox_style,
        nx_hexagon=nx_hexagon, 
        opacity=opacity, 
        min_count=1, 
        show_original_data=False,
    )
    
    # gp_fig = go.Figure(go.Scattermapbox(
    #     mode = "markers+text",
    #     lon = gp_df["Longitude"], lat = gp_df["Latitude"],
    #     marker = {'size':marker_size, 'symbol': "marker"},
    #     text = gp_df["clinic_name"],
    #     ))

    gp_fig = px.scatter_mapbox(gp_df, lat="Latitude", lon="Longitude", 
                          color="district", 
                          text="clinic_name")

    population_fig.add_trace(gp_fig.data[0])

    population_fig.update_layout(
        mapbox = {
            'accesstoken': os.getenv("MAPBOX_TOKEN"),
            'style': mapbox_style, 'zoom': 5,
            "center":{"lat": 4.389059008652357, "lon": 108.65244272591418}},
        showlegend = False,)

    st.plotly_chart(population_fig, use_container_width=True)
    

if __name__ == "__main__":
    str_overlay_analysis()