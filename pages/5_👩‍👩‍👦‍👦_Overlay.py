import streamlit as st
from datetime import date
import polars as pl
import pandas as pd
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

# To ensure the function can be import
if os.path.dirname(os.getcwd()) not in sys.path:
    sys.path.append(os.path.dirname(os.getcwd()))

from mph.geo_project.streamlit.function.file import file
from mph.geo_project.streamlit.function.map import map

@st.cache_data
def read_data():
    gp = pd.read_hdf(os.path.join(os.path.dirname(os.getcwd()), "data/gp/gp.h5"))
    population = pl.read_parquet(os.path.join(os.path.dirname(os.getcwd()), file._population_str_ascii_households))
    return gp, population

def overlay_analysis() -> None:
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
    st.markdown("""<p class="header">Overlay Analysis</p>""", unsafe_allow_html=True)
    st.markdown(f'<p class="subheader">Last Update = {date(2024, 6, 28)}</p>', unsafe_allow_html=True)
    st.divider()

    # Load the data
    gp, population = read_data()

    # To put option for choropleth plot
    col1, col2 = st.columns(2)
    with col1:
        color_continuous_scale = st.selectbox("color_continuous_scale", options=map._color_scheme)

        # To select district
        district_selection = st.multiselect("Districts", options=population.sort("district").select("district").to_pandas()["district"].unique())
        if district_selection != []:
            population = population.filter(pl.col("district").is_in(district_selection))

        # For density map radius
        radius = st.slider("Radius in Density Map", min_value=1, max_value=100, value=20)

    with col2:
        mapbox_style = st.selectbox("Mapbox Style", options=map._mapbox_style)

        # To select parlimen
        parlimen = st.multiselect("Parlimen", options=population.sort("parlimen").select("parlimen").to_pandas()["parlimen"].unique())
        if parlimen != []:
            population = population.filter(pl.col("parlimen").is_in(parlimen))

        # To select opacity for density map
        opacity = st.slider("Opacity for Density Map", min_value=0.1, max_value=1.0, value=0.5, step=0.05)

    # To allow user to select which type of map to present
    map_selection = st.radio("Select Type of Map to display", 
                             options=["District Chorepleth", "Parlimen Chorepleth", "Density Map", "Overlay Map"],
                             horizontal=True)
    
    if map_selection == "Density Map" or map_selection == "Overlay Map":
        # Prepare the dataset
        temp_pt = population.select("X","Y", "estimated_str").to_pandas()
        fig = go.Figure(go.Densitymapbox(lat=temp_pt["Y"], lon=temp_pt["X"], z=temp_pt.loc[:,"estimated_str"],
                                 radius=radius,
                                 autocolorscale = False, 
                                 colorscale=color_continuous_scale,
                                 colorbar_title="Estimated STR Population",
                                 opacity=opacity,
                                 showlegend=False,
                                 text=None,
                                 zmin=temp_pt.loc[:,"estimated_str"].min(), zmax=temp_pt.loc[:,"estimated_str"].max()))
        fig.update_layout(mapbox_style=mapbox_style, 
                          mapbox_accesstoken=os.getenv("MAPBOX_TOKEN"),
                          mapbox_zoom=5, 
                          mapbox_center={"lat": 4.389059008652357, "lon": 108.65244272591418})
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

        # Trial to present the map based on selection
        if map_selection == "Density Map":
            st.plotly_chart(fig, use_container_width=True)

        elif map_selection == "Overlay Map":
            # fig.add_trace()

            st.plotly_chart(fig, use_container_width=True)
    elif map_selection == "District Chorepleth":
        temp_pt = population.group_by("district").agg(pl.col("estimated_str").sum())
        # DDisplay the chorepleth map
        st.plotly_chart(map.draw_chorepleth(map_file = os.path.join(os.path.dirname(os.getcwd()),file._map_district),
                                            df = temp_pt.to_pandas(),
                                            location="district",
                                            z="estimated_str",
                                            featureidkey="district",
                                            text="estimated_str",
                                            colorscale=color_continuous_scale,
                                            mapbox_style=mapbox_style,
                                            marker_line_width = 0.5,
                                            marker_opacity = 0.5,),
                        use_container_width=True)
        # Show the pivoted table 
        st.dataframe(temp_pt.with_columns((pl.col("estimated_str")/pl.col("estimated_str").sum() * 100).alias("Percentage")).to_pandas(), use_container_width=True)
        
        
    elif map_selection == "Parlimen Chorepleth":
        temp_pt = population.group_by("parlimen").agg(pl.col("estimated_str").sum())
        # Show the chorepleth first
        st.plotly_chart(map.draw_chorepleth(map_file = os.path.join(os.path.dirname(os.getcwd()),file._map_parlimen),
                                            df = temp_pt.to_pandas(),
                                            location="parlimen",
                                            z="estimated_str",
                                            featureidkey="parlimen",
                                            text="estimated_str",
                                            colorscale=color_continuous_scale,
                                            mapbox_style=mapbox_style,
                                            marker_line_width = 0.5,
                                            marker_opacity = 0.5,),
                        use_container_width=True)
        #Show the pivoted table
        st.dataframe(temp_pt.with_columns((pl.col("estimated_str")/pl.col("estimated_str").sum() * 100).alias("Percentage")).to_pandas(), use_container_width=True)

    # Provide divider and then allow expansion for original dataframe
    st.divider()
    with st.expander("Original DataFrame"):
        st.dataframe(population)

if __name__ == "__main__":
    overlay_analysis()
