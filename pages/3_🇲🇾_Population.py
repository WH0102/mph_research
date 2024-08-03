import streamlit as st
from datetime import date
import polars as pl
import plotly.express as px
from itertools import combinations
import os
from dotenv import load_dotenv

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
    
    # Prepare some filteration method
    _filter_value = {"sex":"both", "age":"overall", "ethnicity":"overall"}
    _filter_list = list(zip(combinations(_filter_value.keys(), 2), combinations(_filter_value.values(), 2)))
    _reversed_key = list(_filter_value.keys())[::-1]

    def read_population_data():
        district_population = pl.read_parquet('https://storage.dosm.gov.my/population/population_district.parquet')\
                            .with_columns(pl.col("age").str.replace("5-9", "05-09"))
        for key, value in map._dict_district.items():
            district_population = district_population.with_columns(pl.col("district").str.replace(key, value))
        return district_population

    def read_geojson_file(file:str):
        # Import packages
        import json

        # Open the file and then load with json
        with open(file=file) as file:
            geojson_data = json.load(file)

        # Return the geojson_data
        return geojson_data

def population_analysis() -> None:
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
    st.markdown("""<p class="header">Malaysian Population Analysis</p>""", unsafe_allow_html=True)
    st.markdown(f'<p class="subheader">Last Update = {date(2024, 6, 28)}</p>', unsafe_allow_html=True)
    st.divider()

    # Population graph and poverty graph
    st.markdown("""<p class="subheader">General Malaysian Population Information</p>""", unsafe_allow_html=True)
    
    # Prepare the dataset
    district_geojson = map.read_geojson_file("./data/map/administrative_2_district.geojson")
    district_population = map.read_population_data()
    
    # To put option for choropleth plot
    col1, col2 = st.columns(2)
    with col1:
        # To allow user to choose color scheme for the map
        color_continuous_scale = st.selectbox("color_continuous_scale", options=map._color_scheme)
        
        # To select Sex
        sex = st.selectbox("Sex", options=district_population.select("district","sex").to_pandas().sort_values("sex")["sex"].unique())
        district_population = district_population.filter(pl.col("sex")==sex)

        # To select district
        district_selection = st.multiselect("Districts", options=district_population.select("district","population").to_pandas().sort_values("district")["district"].unique())
        if district_selection != []:
            district_population = district_population.filter(pl.col("district").is_in(district_selection))

    with col2:
        # To allow user to choose mapbox style
        mapbox_style = st.selectbox("Mapbox Style", options=map._mapbox_style)
        
        # To select Ethinicity
        ethnicity = st.selectbox("Ethnicity", options=district_population.select("district","ethnicity").to_pandas().sort_values("ethnicity", ascending=False)["ethnicity"].unique())
        district_population = district_population.filter(pl.col("ethnicity")==ethnicity)

        # To select Age
        age = st.selectbox("Age", options=district_population.select("district","age").to_pandas().sort_values("age", ascending=False)["age"].unique())
        district_population = district_population.filter(pl.col("age")==age)
        
    # Plot choropleth
    st.plotly_chart(px.choropleth_mapbox(district_population.to_pandas(), 
                                         geojson=district_geojson,
                                         featureidkey="properties.district",
                                         locations="district",
                                         animation_frame="date",
                                         center={"lat": 4.389059008652357, "lon": 108.65244272591418},
                                         color="population",
                                         color_continuous_scale=color_continuous_scale,
                                         mapbox_style=mapbox_style,
                                         zoom=5))

    # Restructure the DF
    district_population = map.read_population_data()

    # To allow change in value for all tabs below
    if district_selection != []:
        district_population = district_population.filter(pl.col("district").is_in(district_selection))

    # Create tabs with name
    tabs = st.tabs(["District", ] + map._reversed_key)

    # For Overall
    with tabs[0]:
        # Prepare overall df
        temp_df = district_population.filter(pl.col("sex")=="both",
                                             pl.col("age")=="overall",
                                             pl.col("ethnicity")=="overall")
        
        temp_pt = temp_df.select(pl.col("date").cast(pl.String), "district", "population").to_pandas()\
                         .pivot_table(index="district", columns="date", values="population", aggfunc=sum)

        # Calculate percentage
        for column in [column for column in temp_pt.columns if column != "population"]:
            temp_pt.loc[:,f"{column}_%"] = round(temp_pt.loc[:,column] / temp_pt.loc[:,column].sum() * 100, 2)

        # Pivot and show the dataframe
        st.dataframe(temp_pt, use_container_width=True)

    # Start looping
    for num in range(0, 3):
         # Loop through tabs
         with tabs[num+1]:
            # Pivot based on a single column but ensure other columns use overall or both
            temp_df = district_population.filter(pl.col(map._filter_list[num][0][0])==map._filter_list[num][1][0],
                                                pl.col(map._filter_list[num][0][1])==map._filter_list[num][1][1])\
                        .select(pl.col("date").cast(pl.String), "population", map._reversed_key[num]).to_pandas()\
                        .pivot_table(index=map._reversed_key[num], columns="date", values="population", aggfunc=sum)
            
            # Calculate percentage
            for column in [column for column in temp_df.columns if column != map._reversed_key[num]]:
                temp_df.loc[:,f"{column}_%"] = round(temp_df.loc[:,column] / temp_df.loc[:,column].max() * 100, 2)
            
            # Show the dataframe
            st.dataframe(temp_df, use_container_width=True)
    
if __name__ == "__main__":
    population_analysis()