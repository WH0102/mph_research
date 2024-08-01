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
# To ensure the function can be import
# if os.path.dirname(os.getcwd()) not in sys.path:
#     sys.path.append(os.path.dirname(os.getcwd()))

# from mph.geo_project.streamlit.function.file import file
# from mph.geo_project.streamlit.function.map import map

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
    district_geojson = read_geojson_file("./data/map/administrative_2_district.geojson")
    district_population = pl.read_parquet('https://storage.dosm.gov.my/population/population_district.parquet')\
                            .with_columns(pl.col("age").str.replace("5-9", "05-09"))
    for key, value in _dict_district.items():
        district_population = district_population.with_columns(pl.col("district").str.replace(key, value))
    
    # Prepare some filteration method
    filter_value = {"sex":"both", "age":"overall", "ethnicity":"overall"}
    filter_list = list(zip(combinations(filter_value.keys(), 2), combinations(filter_value.values(), 2)))
    reversed_key = list(filter_value.keys())[::-1]

    # To put option for choropleth plot
    col1, col2 = st.columns(2)
    with col1:
        color_continuous_scale = st.selectbox("color_continuous_scale", options=map._color_scheme)
        # To select Year
        year_selection = st.selectbox("Year for Population", options=district_population.select(pl.col("date").cast(pl.String),"district").to_pandas().sort_values("date", ascending=False)["date"].unique())
        district_population = district_population.filter(pl.col("date").cast(pl.String)==year_selection)
        
        # To select Sex
        sex = st.selectbox("Sex", options=district_population.select("district","sex").to_pandas().sort_values("sex")["sex"].unique())
        district_population = district_population.filter(pl.col("sex")==sex)
    with col2:
        mapbox_style = st.selectbox("Mapbox Style", options=map._mapbox_style)
        
        # To select Ethinicity
        ethnicity = st.selectbox("Ethnicity", options=district_population.select("district","ethnicity").to_pandas().sort_values("ethnicity", ascending=False)["ethnicity"].unique())
        district_population = district_population.filter(pl.col("ethnicity")==ethnicity)

        # To select Age
        age = st.selectbox("Age", options=district_population.select("district","age").to_pandas().sort_values("age", ascending=False)["age"].unique())
        district_population = district_population.filter(pl.col("age")==age)

    # To select district
    district_selection = st.multiselect("Districts", options=district_population.select("district","population").to_pandas().sort_values("district")["district"].unique())
    if district_selection != []:
        district_population = district_population.filter(pl.col("district").is_in(district_selection))
        
    # Plot choropleth
    st.plotly_chart(px.choropleth_mapbox(district_population.to_pandas(), 
                                         geojson=district_geojson,
                                         featureidkey="properties.district",
                                         locations="district",
                                         center={"lat": 4.389059008652357, "lon": 108.65244272591418},
                                         color="population",
                                         color_continuous_scale=color_continuous_scale,
                                         mapbox_style=mapbox_style,
                                         zoom=5))

    # Restructure the DF
    district_population = pl.read_parquet(os.path.join(os.path.dirname(os.getcwd()),file._population_district))\
                            .with_columns(pl.col("age").str.replace("5-9", "05-09"))
    for key, value in map._dict_district.items():
        district_population = district_population.with_columns(pl.col("district").str.replace(key, value))
    # To allow change in value for all tabs below
    if district_selection != []:
        district_population = district_population.filter(pl.col("district").is_in(district_selection))

    # Create tabs with name
    tabs = st.tabs(["District", ] + reversed_key)

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
            temp_df = district_population.filter(pl.col(filter_list[num][0][0])==filter_list[num][1][0],
                                                pl.col(filter_list[num][0][1])==filter_list[num][1][1])\
                        .select(pl.col("date").cast(pl.String), "population", reversed_key[num]).to_pandas()\
                        .pivot_table(index=reversed_key[num], columns="date", values="population", aggfunc=sum)
            
            # Calculate percentage
            for column in [column for column in temp_df.columns if column != reversed_key[num]]:
                temp_df.loc[:,f"{column}_%"] = round(temp_df.loc[:,column] / temp_df.loc[:,column].max() * 100, 2)
            
            # Show the dataframe
            st.dataframe(temp_df, use_container_width=True)

    # No need to write for all?
    # Concentrate on the population first, for 10 districts,
    # Merge with parliment to get the parliment involved
    # Divide the parliment str number by total population to get a percentage
    # Use the percentage to times with the z value from ASCII for density
    
if __name__ == "__main__":
    population_analysis()