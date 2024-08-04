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

# To set the environement
load_dotenv()
px.set_mapbox_access_token(os.getenv("MAPBOX_TOKEN"))

class gp:
    _district_code_list = ['14_1', '13_1', '12_7', '10_8', '10_1', '10_5', '10_2', '8_3', '7_4', '1_2']
    _state_code_list = [14, 13, 12, 10, 8, 7, 1]
    _district_name_list = [
        'Gombak', 'Johor Bahru', 'Kinta', 'Klang', 'Kota Kinabalu',
        'Kuching', 'Petaling', 'Timur Laut', 'Ulu Langat', 'W.P. Kuala Lumpur'
    ]

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
    _dict_district = {
        "Cameron Highland":"Cameron Highlands",
        "Cameron Highlandss":"Cameron Highlands",
        "Sp Selatan":"Seberang Perai Selatan",
        "Sp Tengah":"Seberang Perai Tengah",
        "Sp Utara":"Seberang Perai Utara" 
    }

    _summary_column_name = ["District Name", "Count of Points", "Mean", "Standard Deviation", "Min", "Max", "Median", "Inter-Quarter Range", "Skew", "Kurtosis", "shapiro"]
    _summary_function_list = [len, np.mean, np.std, min, max, np.median, iqr, skew, kurtosis, shapiro]

    def read_data():
        gp_df = pd.read_excel("./data/information/gp_list.xlsx")
        population = pd.read_parquet("./data/information/ascii_household_and_gp.parquet")
        return gp_df, population

def overlay_analysis():
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
    st.markdown("""<p class="header">STR Overlay GP Analysis</p>""", unsafe_allow_html=True)
    st.markdown(f'<p class="subheader">Last Update = {date(2024, 6, 28)}</p>', unsafe_allow_html=True)
    st.divider()

    # Prepare the data and return error if something goes wrong
    gp_df, population = map.read_data()

    # To divide intor 2 different section
    # 1. General
    # 2. Per District

    tabs = st.tabs(["Overview", ] + gp._district_name_list)

    with tabs[0]:
        st.markdown("""<p class="body_header">Summary of Distance Between Population and Active SPM Service Providing GPs According to District</p>""", unsafe_allow_html=True)
        # Perform pivot table operation
        pivot_table = population.query(f"code_state_district.isin({gp._district_code_list})")\
            .pivot_table(
                index="district", 
                values="distance", 
                aggfunc=map._summary_function_list
            ).reset_index()

        # Flatten the MultiIndex columns
        pivot_table.columns = map._summary_column_name

        # Separate the Shapiro-Wilk test results into two columns
        for index, row in pivot_table.iterrows():
            pivot_table.loc[index, "Shapiro_stats"] = float(row["shapiro"][0])
            pivot_table.loc[index, "Shapiro_p_value"] = float(row["shapiro"][1])

        # Drop the original shapiro_test column then show it
        st.dataframe(pivot_table.drop(columns="shapiro").round(2), 
                     hide_index=True, use_container_width=True)
        
        # To display information
        columns = st.columns(len(map._summary_function_list))
        for num in range(0, len(columns)):
            columns[num].metric(map._summary_column_name[num], 
                                f"{map._summary_function_list[num](population.query(f"code_state_district.isin({gp._district_code_list})")["distance"]):,s}")
        
        # To display the histogram?
        st.plotly_chart(px.histogram(population.query(f"code_state_district.isin({gp._district_code_list})"),
                                     x="distance",
                                     nbins=len(population.query(f"code_state_district.isin({gp._district_code_list})"))),
                        use_container_width=True)

if __name__ == "__main__":
    overlay_analysis()