import streamlit as st
from datetime import date
import pandas as pd
import plotly.express as px
import os
import sys

# To ensure the function can be import
# if os.path.dirname(os.getcwd()) not in sys.path:
#     sys.path.append(os.path.dirname(os.getcwd()))

_mapbox_style = [
        'basic', 'streets', 'outdoors', 'light', 'dark', 'satellite', 'satellite- streets',
        'open-street-map', 'white-bg', 'carto-positron', 'carto-darkmatter', 'stamen-terrain', 'stamen-toner', 'stamen-watercolor'
    ]

def read_google_sheet():
    import gspread
    import ast
    from google.oauth2.service_account import Credentials
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    credentials = Credentials.from_service_account_info(
        ast.literal_eval(os.getenv("GSPREAD")),
        scopes=scopes
    )

    gc = gspread.authorize(credentials)

    sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1qFEXMLsWHXQIvv3gUflwObSOZPqklw8TD_VXilI2ojo/edit")

    worksheet = sh.get_worksheet(0)

    return pd.DataFrame(worksheet.get_all_records())

# @st.cache_data
# def read_gp_data() -> pd.DataFrame:
#     return pd.read_hdf("./geo_project/streamlit/data/gp/gp.h5")

def gp_analysis() -> None:
    # Prepare the data first, if error will prevent the code from running
    df = read_google_sheet()

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
        st.code(
            """# Create empty dataframe
    df = pd.DataFrame()

    # To loop through the **kwargs
    for key, value in state_dict.items():
        # loop through the value in range loop
        for num in range(1, value):
            # Read the html
            temp_df = pd.read_html(f"https://kelayakan-spm.protecthealth.com.my/find-clinics?state_code={key}&page={num}")[0]
            temp_df.loc[:,"state"] = key
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
        df.at[index, "address"] = text_split[1]"""
        )

    # Divider
    st.divider()

    # To display the distribution
    st.markdown("""<p class="subheader">SPM Service Providers Distribution</p>""", unsafe_allow_html=True)

    # Pivot and display
    gp_pt = df.pivot_table(index=["state", "district"], values="clinic_name", aggfunc=len)\
              .rename_axis(None, axis=1).reset_index().rename(columns={"clinic_name":"Number of GPs"})
    gp_pt.loc[:,"Percentage"] = gp_pt.loc[:,"Number of GPs"] / gp_pt.loc[:,"Number of GPs"].sum() * 100
    st.data_editor(gp_pt.round(2), use_container_width=True)

    # To put divider again
    st.divider()

    # To display the distribution
    st.markdown("""<p class="subheader">Scatter Plot of SPM Service Providers</p>""", unsafe_allow_html=True)

    # To put option for scatter plot
    col1, col2 = st.columns(2)
    with col1:
        # lat = st.selectbox("Latitude", options=df.columns)
        color = st.selectbox("Color", options=[None,] + list(df.columns))
        zoom = st.slider("Zoom", min_value=1, max_value=10, value=4,)
    with col2:
        # lon = st.selectbox("Longitude", options=df.columns)
        text = st.selectbox("Text", options=[None,] + list(df.columns))
        mapbox_style = st.selectbox("Mapbox Style", options=_mapbox_style)
    
    # To put scatter plot of the GP
    st.plotly_chart(
        px.scatter_mapbox(df, lat="Latitude", lon="Longitude", 
                          color=color, 
                          text=text,
                          zoom=zoom,
                          center={"lat": 4.389059008652357, "lon": 108.65244272591418},
                          mapbox_style=mapbox_style),
        use_container_width=True
    )

if __name__ == "__main__":
    gp_analysis()