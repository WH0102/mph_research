import streamlit as st
from datetime import date
import polars as pl
import plotly.express as px
import geopandas as gpd
from itertools import combinations
import os
import sys
from dotenv import load_dotenv
import os

# To set the environement
load_dotenv()
px.set_mapbox_access_token(os.getenv("MAPBOX_TOKEN"))

# To ensure the function can be import
if os.path.dirname(os.getcwd()) not in sys.path:
    sys.path.append(os.path.dirname(os.getcwd()))

from .function.file import file
from .function.map import map
from .function.descriptive import descriptive

@st.cache_data
def read_data():
    # Prepare the data first, if error will prevent the code from running
    population = pl.read_parquet(os.path.join(os.path.dirname(os.getcwd()),file._file_spm_parquet))
    # parlimen_info = gpd.read_file(os.path.join(os.path.dirname(os.getcwd()),file._map_parlimen))
    district = gpd.read_file(os.path.join(os.path.dirname(os.getcwd()),file._map_district))
    parlimen = gpd.read_file(os.path.join(os.path.dirname(os.getcwd()),file._map_parlimen))
    parlimen_info = parlimen.sjoin(district.drop(columns="state"))
    return population, parlimen_info

def str_analysis() -> None:
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
    st.markdown("""<p class="header">STR Recipients Analysis</p>""", unsafe_allow_html=True)
    st.markdown(f'<p class="subheader">Last Update = {date(2024, 6, 28)}</p>', unsafe_allow_html=True)
    st.divider()

    # Population graph and poverty graph
    st.markdown("""<p class="subheader">General STR Receipients Information</p>""", unsafe_allow_html=True)

    # Prepare the data
    population, parlimen_info = read_data()

    col1, col2 = st.columns(2)
    col1.metric("Total Households", f"{8391149:,d}") #8391149 len(population.unique(subset="id_ben"))
    col2.metric("Total Beneficiaries", f"{17286912:,d}") #17286912 len(descriptive.convert_str_to_long(population))

    # Prepare the columns to be pivoted
    descriptive_columns = ["str_category", "marital_status", "work_status", "salary"]

    # To display the result with loop
    for column in descriptive_columns:
        # Prepare the information
        temp_pt = descriptive.pivot_with_percentage(df=population.unique(subset="id_ben"), 
                                                    columns=column)\
                                                        .to_pandas().round(2).sort_values(column)

        # Information on what kind of pivoted table info contain
        st.markdown(f"""<p class="subheader">Count of STR Households' {column} Information</p>""", unsafe_allow_html=True)

        # Split the display into 2 columns
        col1, col2 = st.columns(2)

        with col1:
            # To display pivot table information
            st.dataframe(temp_pt, use_container_width=True, hide_index = True)
        with col2:
            # To display the information in pie chart
            st.plotly_chart(px.pie(temp_pt, names=column, values="Number of Households")\
                              .update_traces(textinfo="label+value+percent", showlegend=False), 
                            use_container_width=True)
            
        st.divider()

    # Try Choropleth first
    population_pt = population.group_by("code_parlimen").len("STR Count").to_pandas()\
                           .merge(parlimen_info.loc[:,("code_parlimen", "parlimen", "district")], on="code_parlimen")
    
    # To put option for choropleth plot
    col1, col2 = st.columns(2)
    with col1:
        color_continuous_scale = st.selectbox("color_continuous_scale", options=map._color_scheme)
        
        # To select district
        district_selection = st.multiselect("Districts", options=population_pt.sort_values("district")["district"].unique())
        if district_selection != []:
            population_pt = population_pt.query(f"district.isin({district_selection})")
    with col2:
        mapbox_style = st.selectbox("Mapbox Style", options=map._mapbox_style)

        # To select parlimen
        parlimen = st.multiselect("Parlimen", options=population_pt.sort_values("parlimen")["parlimen"].unique())
        if parlimen != []:
            population_pt = population_pt.query(f"parlimen.isin({parlimen})")

    # To have a table displauy
    with st.expander("Show Pivoted Table"):
        st.dataframe(descriptive.pivot_with_percentage(population, columns="code_parlimen").to_pandas()\
                     .merge(parlimen_info.loc[:,("code_parlimen", "parlimen", "district")], on="code_parlimen", how="left"), 
                     use_container_width=True)

    # # Display the chorepleth
    # st.plotly_chart(map.draw_chorepleth(map_file = os.path.join(os.path.dirname(os.getcwd()),file._map_parlimen),
    #                                     df = population_pt,
    #                                     location="parlimen",
    #                                     z="STR Count",
    #                                     featureidkey="parlimen",
    #                                     text="STR Count",
    #                                     colorscale=color_continuous_scale,
    #                                     mapbox_style=mapbox_style,
    #                                     marker_line_width = 0.5,
    #                                     marker_opacity = 0.5,),
    #                 use_container_width=True)

if __name__ == "__main__":
    str_analysis()