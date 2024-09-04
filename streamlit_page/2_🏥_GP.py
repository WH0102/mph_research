import streamlit as st
from datetime import date
import pandas as pd
import polars as pl
import plotly.express as px
import os
import sys

# To ensure the function can be import
# if os.path.dirname(os.getcwd()) not in sys.path:
#     sys.path.append(os.path.dirname(os.getcwd()))

_mapbox_style = [
    'carto-positron', 'open-street-map', 'white-bg', 'carto-darkmatter', 'stamen-terrain', 'stamen-toner', 
    'basic', 'streets', 'outdoors', 'light', 'dark', 'satellite', 'satellite- streets', 'stamen-watercolor',
    ]

def read_gp_data():
    gp_df = pl.read_excel("./data/information/gp_list.xlsx")
    all_gp_df = pl.read_excel("./data/information/private_medical_gp.xlsx")
    # Return the dataframe
    return gp_df, all_gp_df

def gp_analysis() -> None:
    # Prepare the data first, if error will prevent the code from running
    gp_df, all_gp_df = read_gp_data()

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
    st.markdown("""<p class="header">SPM Service Providers Analysis</p>""", unsafe_allow_html=True)
    st.markdown(f'<p class="subheader">Last Update = {date(2024, 6, 28)}</p>', unsafe_allow_html=True)
    st.divider()

    # To get all the gp from ProtectHealth Webpage
    with st.expander("""Code To get latest list of GP From ProtectHealth Webpage"""):
        st.code("""
    class gp:
    _district_code_list = ['14_1', '13_1', '12_7', '10_8', '10_1', '10_5', '10_2', '8_3', '7_4', '1_2']
    _state_code_list = [14, 13, 12, 10, 8, 7, 1]
    _district_name_list = [
        'Gombak', 'Johor Bahru', 'Kinta', 'Klang', 'Kota Kinabalu',
        'Kuching', 'Petaling', 'Timur Laut', 'Ulu Langat', 'W.P. Kuala Lumpur'
    ]
    _parlimen_code_list = ['P.048', 'P.049', 'P.050', 'P.051', 'P.052', 'P.053', 'P.062',
       'P.063', 'P.064', 'P.065', 'P.066', 'P.067', 'P.069', 'P.070',
       'P.071', 'P.072', 'P.073', 'P.094', 'P.095', 'P.096', 'P.097',
       'P.098', 'P.099', 'P.100', 'P.101', 'P.102', 'P.103', 'P.104',
       'P.105', 'P.106', 'P.107', 'P.108', 'P.109', 'P.110', 'P.111',
       'P.112', 'P.113', 'P.114', 'P.115', 'P.116', 'P.117', 'P.118',
       'P.119', 'P.120', 'P.121', 'P.122', 'P.123', 'P.124', 'P.155',
       'P.156', 'P.157', 'P.158', 'P.159', 'P.160', 'P.161', 'P.162',
       'P.163', 'P.165']

    # Dictionary Areas, "selangor":66 pages will have district separated
    _dict_gp_spm = {
        "wp_kuala_lumpur":[24, "14_1"],
        "sarawak":[6, "13_1"],
        "sabah":[6, "12_7"],
        "perak":[12, "8_3"],
        "penang":[5, "7_4"],
        "johor":[17, "1_2"]
    }
    _dict_gp_change_state = {
        "wp_kuala_lumpur":"W.P. Kuala Lumpur",
        "selangor":"Selangor",
        "sarawak":"Sarawak",
        "sabah":"Sabah",
        "perak":"Perak",
        "penang":"Pulau Pinang",
        "johor":"Johor"
    }
    _selangor_district_dict = {
        "Gombak": [1009, 10, "10_1"],
        "Ulu Langat":[1006, 17, "10_8"],
        "Klang":[1001, 15, "10_2"],
        "Petaling":[1008, 28, "10_5"]
    }

    def get_parlimen_list_from_district(parlimen_file:str = file._map_parlimen,
                                        district_file:str = file._map_district):
        # Read the necessary file
        parlimen = gpd.read_file(parlimen_file)
        district = gpd.read_file(district_file)

        # Spatial join the parlimen and district, but due to some of the parlimen having different district or state, result can be duplicated
        return list(parlimen.sjoin(district)\
                       .query(f"code_state_district.isin({gp._district_list}) & code_state_left.isin({gp._state_list})")\
                    ["code_parlimen"].unique())
    
    def read_spm_gp_list(state_dict: dict = _dict_gp_spm,
                         selangot_dict:dict = _selangor_district_dict,
                         dict_gp_change_state:dict = _dict_gp_change_state) -> pd.DataFrame:
        # Import the necessary packages
        import pandas as pd

        # Create empty dataframe
        df = pd.DataFrame()

        # To loop through the **kwargs
        for key, value in state_dict.items():
            # loop through the value in range loop
            for num in range(1, value[0]):
                # Read the html
                temp_df = pd.read_html(f"https://kelayakan-spm.protecthealth.com.my/find-clinics?state_code={key}&page={num}")[0]
                temp_df.loc[:,"state"] = key
                temp_df.loc[:,"code_state_district"] = value[1]
                df = pd.concat([df, temp_df], ignore_index=True)

        for key, value in selangot_dict.items():
            # loop through the value in range loop
            for num in range(1, value[1]):
                # Read the html
                temp_df = pd.read_html(f"https://kelayakan-spm.protecthealth.com.my/find-clinics?state_code=selangor&district_code={value[0]}&page={num}")[0]
                temp_df.loc[:,"state"] = "selangor"
                temp_df.loc[:,"code_state_district"] = value[2]
                df = pd.concat([df, temp_df], ignore_index=True)
        
        # Change the Tutup to Buka 
        df.loc[:,"Nama Klinik"] = df.loc[:,"Nama Klinik"].str.replace("Tutup", "Buka")
        # Changet the Buka to "|" for easier separation later
        df.loc[:,"Nama Klinik"] = df.loc[:,"Nama Klinik"].str.replace("  Buka  ", "|")

        # To clean the unnecessary information
        for item in ["Bimbit", "Lokasi", "Tel", "Laman Web"]:
            df.loc[:,"Nama Klinik"] = df.loc[:,"Nama Klinik"].str.replace(item, "")

        # To loop through the df.
        for index, row in df.iterrows():
            # Split the information
            text_split = row["Nama Klinik"].split("|")
            # To put clinic name
            df.at[index, "clinic_name"] = text_split[0]
            # TO put the clinic address information
            df.at[index, "address"] = text_split[1]

        # To change name
        for key, value in dict_gp_change_state.items():
            df.loc[:,"state"] = df.loc[:,"state"].str.replace(key, value)

        # Return the dataframe
        return df.loc[:,("clinic_name", "address", "state")]
    
    def get_lat_lon(df:pd.DataFrame,
                    address_col:str = "address") -> pd.DataFrame:
        from geopy.geocoders import Nominatim
        from geopy.exc import GeocoderTimedOut, GeocoderRateLimited, GeocoderNotFound
        from geopy.extra.rate_limiter import RateLimiter

        # Setting the nominatim user agent
        geolocator = Nominatim(user_agent="str_address_geocoding")

        # Set the rate limiters
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries = 0)

        try:
            # To get the geolocation of the address
            df.loc[:,"location"] = df.loc[:,address_col].apply(geocode)
            df.loc[:,'Latitude'] = df.loc[:,'location'].apply(lambda loc: tuple(loc.point)[0] if loc else None)
            df.loc[:,'Longitude'] = df.loc[:,'location'].apply(lambda loc: tuple(loc.point)[1] if loc else None)
        except GeocoderTimedOut or GeocoderRateLimited or GeocoderNotFound:
            print("Error")

        # Return the dataframe
        return df"""
        )

    # Divider
    st.divider()

    # To display the distribution
    st.markdown("""<p class="subheader">SPM Service Providers Distribution</p>""", unsafe_allow_html=True)

    # Pivot both spm active provding gp and total private gp registered
    all_gp_pt = all_gp_df.group_by("district").len("registered")\
                        .with_columns((pl.col("registered")/pl.col("registered").sum()).alias("Percentage for Total Private GP"))
    gp_pt = gp_df.group_by("district").len("spm_gp")\
                .with_columns((pl.col("spm_gp")/pl.col("spm_gp").sum()).alias("Percentage of Active SPM Service Providing GPs"))

    # Join both the pivoted table on district and calculate the percentage of gp registered compare to whole district.
    both_gp_pt = gp_pt.join(all_gp_pt, how="left", on="district")\
                      .with_columns((pl.col("spm_gp")/pl.col("registered")).alias("Active SPM Service Providing GP/ Total GP"))\
                      .to_pandas()
    st.data_editor(both_gp_pt.round(2), use_container_width=True)

    # Convert both polars to pandas
    gp_df = gp_df.to_pandas()

    # To put divider again
    st.divider()

    # To display the distribution
    st.markdown("""<p class="subheader">Scatter Plot of SPM Service Providers</p>""", unsafe_allow_html=True)

    # To put option for scatter plot
    col1, col2 = st.columns(2)
    with col1:
        # lat = st.selectbox("Latitude", options=df.columns)
        color = st.selectbox("Color", options=[None,] + list(gp_df.columns))
        zoom = st.slider("Zoom", min_value=1, max_value=10, value=4,)
    with col2:
        # lon = st.selectbox("Longitude", options=df.columns)
        text = st.selectbox("Text", options=[None,] + list(gp_df.columns))
        mapbox_style = st.selectbox("Mapbox Style", options=_mapbox_style)
    
    # To put scatter plot of the GP
    st.plotly_chart(
        px.scatter_mapbox(gp_df, lat="Latitude", lon="Longitude", 
                          color=color, 
                          text=text,
                          zoom=zoom,
                          center={"lat": 4.389059008652357, "lon": 108.65244272591418},
                          mapbox_style=mapbox_style),
        use_container_width=True
    )

if __name__ == "__main__":
    gp_analysis()