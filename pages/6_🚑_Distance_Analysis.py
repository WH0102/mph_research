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
        population = pd.read_parquet("./data/information/ascii_household_and_gp.parquet")\
                       .query(f"code_state_district.isin({gp._district_code_list})")
        return gp_df, population
    
    def descriptive_analysis(df:pd.DataFrame,
                             index_name:str,
                             gp_df:pd.DataFrame,
                             show_descriptive:bool = False) -> pd.DataFrame:
        # To put the summary of the df
        answer_dict = dict(zip(map._summary_column_name[1:-1],
                               [formula(df["distance"]) for formula in map._summary_function_list[:-1]]))
        
        # Count shapiro first
        shapiro_value = shapiro(df["distance"])

        # Add shapiro to the dictionary
        answer_dict["Shapiro Stats"] = shapiro_value[0]
        answer_dict["Shapiro p value"] = shapiro_value[1]

        # To generate the number of GP in that area
        district_list = list(df.loc[:,"district"].unique())
        answer_dict["Number of GP"] = len(gp_df.query(f"district.isin({district_list})"))
        # gp_pt = gp_df.pivot_table(index="district", values="clinic_name", aggfunc=len)\
        #              .rename(columns={"clinic_name":"Number of GPs", "district":map._summary_column_name[0]})

        # Create descriptive_df
        descriptive_df = pd.DataFrame(answer_dict, index=[index_name])\
                           .reset_index().rename(columns={"index":map._summary_column_name[0]})

        # To display the histogram
        st.plotly_chart(px.histogram(df, x="distance",
                                     histnorm='probability density',
                                     labels={'distance':'Distance in km'},
                                     marginal="box",
                                     nbins=len(df)),
                                     text_auto=True, 
                        use_container_width=True)
        
        # Trial to display the dataframe based on show_descriptive
        if show_descriptive == True:
            st.dataframe(descriptive_df.round(2), use_container_width=True, hide_index=True)
            # To put a divider
            st.divider()

        
        # Return the descriptive_df
        return descriptive_df

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
    st.markdown("""<p class="header">STR And Active SPM Service Providing GPs' Distance Analysis</p>""", unsafe_allow_html=True)
    st.markdown(f'<p class="subheader">Last Update = {date(2024, 6, 28)}</p>', unsafe_allow_html=True)
    st.divider()

    # Prepare the data and return error if something goes wrong
    gp_df, population = map.read_data()

    # To divide intor 2 different section
    # 1. General
    # 2. Per District

    tabs = st.tabs(["Overview", ] + gp._district_name_list)
    
    # For 1. General
    with tabs[0]:
        st.markdown("""<p class="body_header">Summary of Distance Between Population and Active SPM Service Providing GPs According to District</p>""", unsafe_allow_html=True)
        # Perform pivot table operation
        pivot_table = population.pivot_table(
                index="district", 
                values="distance", 
                aggfunc=map._summary_function_list
            ).reset_index()

        # Flatten the MultiIndex columns
        pivot_table.columns = map._summary_column_name

        # Separate the Shapiro-Wilk test results into two columns
        for index, row in pivot_table.iterrows():
            pivot_table.loc[index, "Shapiro Stats"] = float(row["shapiro"][0])
            pivot_table.loc[index, "Shapiro p value"] = float(row["shapiro"][1])

        # To merge with len(gp_df) and drop column shapiro
        pivot_table.loc[:,"NUmber of GP"] = len(gp_df)
        
        # To display the histogram?
        descriptive_df = map.descriptive_analysis(population, index_name="10 Districts", gp_df = gp_df, show_descriptive = False)

        # To concat with descriptive_df
        pivot_table = pd.concat([descriptive_df,
                                 pivot_table.drop(columns="shapiro")], ignore_index=True)

        # Drop the original shapiro_test column then show it
        st.dataframe(pivot_table.round(2), hide_index=True, use_container_width=True)

        # For the line histogram plot
        st.plotly_chart(ff.create_distplot(hist_data=[population["distance"]],
                                           group_labels=["10 Districts",],
                                           bin_size=0.05,
                                           curve_type="kde",
                                           show_hist=False)\
                          .update_layout(title_text='Curve and Rug Plot for Distance (km) Between STR Population and Active SPM Service Providers of All 10 Districts'),
                                           use_container_width=True)

        # divider
        st.divider()

        # To display the histogram
        st.plotly_chart(px.histogram(population, x="distance",
                                     histnorm='probability density',
                                     labels={'distance':'Distance in km'},
                                     marginal="box",
                                     color="district",
                                     nbins=len(population)),
                                     text_auto=True, 
                        use_container_width=True)
        
        # divider
        st.divider()

        # test of ff
        st.plotly_chart(ff.create_distplot(hist_data=[population.query(f"district=='{district}'")["distance"] for district in gp._district_name_list],
                                           group_labels=gp._district_name_list,
                                           bin_size=0.05,
                                           curve_type="kde",
                                           show_hist=False)\
                          .update_layout(title_text='Curve and Rug Plot for Distance (km) Between STR Population and Active SPM Service Providers Among 10 Districts'),
                                           use_container_width=True)

    # For descriptive analysis of districts
    for num in range(0, len(gp._district_name_list)):
        with tabs[num+1]:
            # To confirm the district
            st.markdown(f"""<p class="body_header">Summary of Distance Between Population and Active SPM Service Providing GPs According in {gp._district_name_list[num]}</p>""", unsafe_allow_html=True)

            # Create the descriptive analysis for each district, along with histogram
            descriptive_df = map.descriptive_analysis(population.query(f"district == '{gp._district_name_list[num]}'"),
                                                      index_name = gp._district_name_list[num],
                                                      gp_df = gp_df,
                                                      show_descriptive = True)

if __name__ == "__main__":
    overlay_analysis()