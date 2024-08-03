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
    _dict_district = {
        "Cameron Highland":"Cameron Highlands",
        "Cameron Highlandss":"Cameron Highlands",
        "Sp Selatan":"Seberang Perai Selatan",
        "Sp Tengah":"Seberang Perai Tengah",
        "Sp Utara":"Seberang Perai Utara" 
    }

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
                            .with_columns(pl.col("age").str.replace("5-9", "05-09"),
                                          pl.col("date").cast(pl.Date).cast(pl.String))
        for key, value in map._dict_district.items():
            district_population = district_population.with_columns(pl.col("district").str.replace(key, value))

        population = pl.read_parquet("./data/information/str_ascii_household.parquet")

        return population, district_population
    
    def descriptive_analysis(df:pd.DataFrame) -> pd.DataFrame:
        # Import necessary packages
        from scipy.stats import skew, kurtosis, shapiro, norm, spearmanr, iqr
        from matplotlib import pyplot as plt
        import seaborn as sns
        import numpy as np
        import statsmodels.api as sm
        
        # Using pandas default describe
        descriptive_df = df.describe()

        # Calculate the skew and kurtosis
        for formula in [np.var, skew, kurtosis, iqr]:
            descriptive_df.loc[f"{formula.__name__}"] = [formula(df.loc[:,column]) 
                                                         if df.loc[:,column].dtype == int or df.loc[:,column].dtype == float 
                                                         else None 
                                                         for column in descriptive_df.columns]

        # Check for normal distribution
        # Calculate the shapiro
        shapiro_values = [shapiro(df.loc[:,column])
                          if df.loc[:,column].dtype == int or df.loc[:,column].dtype == float 
                          else None 
                          for column in descriptive_df.columns]
        
        # Put the shapiro and its p_value into the descriptive df
        descriptive_df.loc["shapiro"] = [shapiro_value[0] for shapiro_value in shapiro_values]
        descriptive_df.loc["shapiro_p_value"] = [shapiro_value[1] for shapiro_value in shapiro_values]

        # Show the dataframe
        st.dataframe(descriptive_df, use_container_width=True)

        # Divider
        st.divider()

        # Plot the graph
        for column_name in descriptive_df.columns:
            try:
                st.write(f"Descriptive Chart for {column_name}:")
                # Prepare the subplot
                fig, (ax1, ax2, ax3) = plt.subplots(nrows=1, ncols=3)

                # Histogram
                ax1.hist(df.loc[:,column_name], bins=len(df.loc[:,column_name].unique()), edgecolor='black')
                ax1.set_xlabel(column_name)
                ax1.set_ylabel('Frequency')

                # QQ plot
                sm.qqplot(df.rename_axis(None, axis=1).reset_index().loc[:,column_name], line='45', ax=ax2, fit = True)

                # Box plot
                sns.boxplot(df.loc[:,column_name], ax=ax3)

                # Show the plot
                st.pyplot(fig, use_container_width=True)
                # Put a divider
                st.divider()

            except:
                st.write("failed")
                
        # Return the descriptive_df
        return descriptive_df

def str_map_analysis() -> None:
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
    st.markdown("""<p class="header">STR Population Analysis</p>""", unsafe_allow_html=True)
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

        # Plot the density map
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
        # Prepare the dataset
        temp_pt = population.select("X","Y", "estimated_str", "state").to_pandas()

        # Plot the scatter bubbule map
        fig = px.scatter_mapbox(temp_pt, lat="Y", lon="X",
                                size="estimated_str", color="state",
                                color_continuous_scale=color_continuous_scale,
                                mapbox_style=mapbox_style,
                                opacity=opacity)

        st.plotly_chart(fig, use_container_width=True)

    elif map_selection == "District Chorepleth":
        # To pivot with percentage for STR population, using total number to prevent error of margin after filter
        temp_pt = population.to_pandas()\
                            .pivot_table(index = "district", values="estimated_str", aggfunc=sum, margins=False).reset_index()
        temp_pt.loc[:,"estimated_str_percentage"] = round(temp_pt.loc[:,"estimated_str"] / 8391149 * 100, 2)

        # For district population
        temp_df = district_population.filter(pl.col("sex")=="both",
                                            pl.col("age")=="overall",
                                            pl.col("ethnicity")=="overall")\
                                     .select(pl.col("date").cast(pl.String), "district", "population").to_pandas()\
                         .pivot_table(index="district", columns="date", values="population", aggfunc=sum, margins=False)
        
        # Merge the dataframe .drop(columns="All") if use margins --True
        merge_pt = temp_pt.merge(temp_df.reset_index(), how="outer", on="district")
        
        # To prevent error of percentage upon selection of district:
        temp_dict = {"2020-01-01":32447.1, 
                     "2021-01-01":32576.0, 
                     "2022-01-01":32698.4, 
                     "2023-01-01":33379.8}

        for column in temp_dict.keys():
            # Calculate percentage for population
            merge_pt.loc[:,f"{column}_%"] = round(merge_pt.loc[:,column] / temp_dict[column] * 100, 2)
            # Calculate the str percentage
            merge_pt.loc[:,f"{column}_str_%"] = round(merge_pt.loc[:,"estimated_str"] / (merge_pt.loc[:,column] * 1000) * 100, 2)            

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
        with st.expander("District Pivot Table"):
           st.dataframe(merge_pt, use_container_width=True, hide_index=True)
        
        # To put a divider
        st.divider()
        
        # Summary of the pivoted table
        with st.expander("Summary of District Pivot Table"):
            descriptive_df = map.descriptive_analysis(merge_pt)
        
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
    str_map_analysis()
