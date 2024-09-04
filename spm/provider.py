from .file import file
import pandas as pd
import geopandas as gpd

class provider:
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
        return df
    
    def haversine(lat1:float, lon1:float, lat2:float, lon2:float) -> float:
        # Import impoartant packages
        import numpy as np

        # Earth radius in kilometers
        R = 6371.0 

        # Find the radians for both lat and lon
        lat1_rad, lon1_rad = np.radians(lat1), np.radians(lon1)
        lat2_rad, lon2_rad = np.radians(lat2), np.radians(lon2)

        # Find the difference of lat and lon between both
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        # Use the haversine formula
        a = np.sin(dlat / 2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

        # Times the earth radius to become km in difference
        distance = R * c

        # Return the value
        return distance
    
    def match_nearest(df1:pd.DataFrame, 
                      df1_lat:str, 
                      df1_lon:str, 
                      df2:pd.DataFrame, 
                      df2_lat:str, 
                      df2_lon:str, 
                      column_to_match:str,
                      distance_column:str="distance_km") -> pd.DataFrame:
        # Define the loop for the second dataframe first
        def find_nearest(lat, lon):
            # Imagine to have a lat lon that will apply throughout the second dataframe's lat lon
            distance = df2.apply(lambda row: gp.haversine(lat, lon, row[df2_lat], row[df2_lon]), axis=1)
            # Return the column to match based on shortest distance
            return df2.loc[distance.idxmin(), column_to_match]
        
        # By looping the first dataframe and then apply the function to loop the second dataframe
        df1.loc[:,column_to_match] = df1.apply(lambda row: find_nearest(row[df1_lat], row[df1_lon]), axis=1)

        # Merge the first and second dataframe together
        df = df1.merge(df2, how="left", on=column_to_match)

        # Calculate the difference between the both match
        df.loc[:,distance_column] = df.apply(lambda row: gp.haversine(lat1 = row[df1_lat], lon1 = row[df1_lon], lat2 = row[df2_lat], lon2 = row[df2_lon]), axis = 1)

        # Return the dataframe
        return df