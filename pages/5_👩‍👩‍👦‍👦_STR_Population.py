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
    _dict_district = {"Cameron Highland":"Cameron Highlands",
                      "Sp Selatan":"Seberang Perai Selatan",
                      "Sp Tengah":"Seberang Perai Tengah",
                      "Sp Utara":"Seberang Perai Utara"}

    def read_geojson_file(file:str):
        # Import packages
        import json

        # Open the file and then load with json
        with open(file=file) as file:
            geojson_data = json.load(file)

        # Return the geojson_data
        return geojson_data

    def draw_chorepleth(map_file:str,
                        df:pd.DataFrame,
                        location:str,
                        z:str,
                        featureidkey:str,
                        autocolorscale:bool = False,
                        colorscale:str = "rainbow",
                        colorbar_title:str = "STR Population Density",
                        mapbox_center:dict = {"lat": 4.389059008652357, "lon": 108.65244272591418},
                        mapbox_style:str = "basic",
                        mapbox_zoom:int|float = 5,
                        marker_line_width:float = 0.5,
                        marker_opacity:float = 0.5,
                        showlegend:bool = True,
                        text:tuple|None = None):
        # Import necessary packages
        import plotly.graph_objects as go
        import os

        # use json to load the choropleth file
        geojson_data = map.read_geojson_file(map_file)

        if text!=None:
            text=df.loc[:,text]

        # Prepare to plot the choropleth
        fig = go.Figure(go.Choroplethmapbox(geojson=geojson_data,
                                            locations=df.loc[:,location], 
                                            z=df.loc[:,z],
                                            featureidkey=f"properties.{featureidkey}",
                                            autocolorscale = autocolorscale, 
                                            colorscale=colorscale,
                                            colorbar_title=colorbar_title,
                                            marker_opacity=marker_opacity, 
                                            marker_line_width=marker_line_width,
                                            showlegend=showlegend,
                                            text=text,
                                            zmin=df.loc[:,z].min(), zmax=df.loc[:,z].max(), ))
        fig.update_layout(mapbox_style=mapbox_style, 
                          mapbox_accesstoken=os.getenv("MAPBOX_TOKEN"),
                          mapbox_zoom=mapbox_zoom, 
                          mapbox_center=mapbox_center,
                          )
        # fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        
        # Return fig
        return fig

    def read_data():
        

        district_population = pl.read_parquet('https://storage.dosm.gov.my/population/population_district.parquet')\
                            .with_columns(pl.col("age").str.replace("5-9", "05-09"))
        for key, value in map._dict_district.items():
            district_population = district_population.with_columns(pl.col("district").str.replace(key, value))

        population = pl.read_parquet("./data/population/str_ascii_household.parquet")

        return population, district_population

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
    population, district_population = map.read_data()

    # To put option for choropleth plot
    col1, col2 = st.columns(2)
    with col1:
        color_continuous_scale = st.selectbox("color_continuous_scale", options=map._color_scheme)

        # To select district
        district_selection = st.multiselect("Districts", options=population.sort("district").select("district").to_pandas()["district"].unique())
        if district_selection != []:
            population = population.filter(pl.col("district").is_in(district_selection))
            district_population = district_population.filter(pl.col("district").is_in(district_selection))

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
                             options=["District Chorepleth", "Parlimen Chorepleth", "Density Map", "Scatter Buble Map"],
                             horizontal=True)

    if map_selection == "Density Map":
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
        # fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        # Display the figure    
        st.plotly_chart(fig, use_container_width=True)

    elif map_selection == "Scatter Buble Map":
        # st.write("Under Construction")
        fig = px.scatter_mapbox(temp_pt, lat="Y", lon="X",
                                size="estimated_str", color="state",
                                color_continuous_scale=color_continuous_scale,
                                mapbox_style=mapbox_style,
                                opacity=opacity)

        st.plotly_chart(fig, use_container_width=True)

    elif map_selection == "District Chorepleth":
        # To pivot with percentage
        temp_pt = population.group_by("district").agg(pl.col("estimated_str").sum())\
                            .with_columns((pl.col("estimated_str")/pl.col("estimated_str").sum() * 100).alias("Percentage")).to_pandas()
        temp_district = district_population.to_pandas()\
                            .pivot_table(index = "district", columns="date", values="population", aggfunc=sum)
        # Calculate percentage
        for column in [column for column in temp_district.columns if column != "district"]:
            temp_district.loc[:,f"{column}_%"] = round(temp_district.loc[:,column] / temp_district.loc[:,column].max() * 100, 2)
        
        # Display the chorepleth map
        st.plotly_chart(map.draw_chorepleth(map_file = "./data/map/administrative_2_district.geojson",
                                            df = temp_pt,
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
        st.dataframe(temp_pt.merge(temp_district.reset_index(), how="outer", on="district"), 
                     use_container_width=True, hide_index=True)
        
    elif map_selection == "Parlimen Chorepleth":
        # TO pivot with percentage
        temp_pt = population.group_by("parlimen").agg(pl.col("estimated_str").sum())\
                            .with_columns((pl.col("estimated_str")/pl.col("estimated_str").sum() * 100).alias("Percentage")).to_pandas()
        
        # Display the chorepleth map
        st.plotly_chart(map.draw_chorepleth(map_file = "./data/map/electoral_0_parlimen.geojson",
                                            df = temp_pt,
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
        st.dataframe(temp_pt, use_container_width=True)

    # Provide divider and then allow expansion for original dataframe
    # st.divider()
    # with st.expander("Original DataFrame"):
    #     st.dataframe(population)

if __name__ == "__main__":
    overlay_analysis()
