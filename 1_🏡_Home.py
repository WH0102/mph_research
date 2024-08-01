import streamlit as st
from datetime import date
import os
import sys

# To ensure the function can be import
if os.path.dirname(os.getcwd()) not in sys.path:
    sys.path.append(os.path.dirname(os.getcwd()))

# Set streamlit page configuration
st.set_page_config(page_title = "Wei Hong's MPH Research Project", page_icon = "random", layout = "wide")

def home_page() -> None:
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
    st.markdown("""<p class="header">Wei Hong's MPH Research Project's Result</p>""", unsafe_allow_html=True)
    st.markdown(f'<p class="subheader">Date = {date.today()}</p>', unsafe_allow_html=True)
    st.divider()   
    
if __name__ == "__main__":
    home_page()