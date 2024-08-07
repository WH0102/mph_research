from function.file import file
import pandas as pd
import geopandas as gpd

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

    # Dictionary Areas
    _dict_gp_spm = {
        "wp_kuala_lumpur":24,
        "selangor":66,
        "sarawak":6,
        "sabah":6,
        "perak":12,
        "penang":5,
        "johor":17
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
    selangor_district = {
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

        # Spatial join the parlimen and district, but due to some of the parlimen having 
        return list(parlimen.sjoin(district)\
                       .query(f"code_state_district.isin({gp._district_list}) & code_state_left.isin({gp._state_list})")\
                    ["code_parlimen"].unique())
    
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
            distance = df2.apply(lambda row: gp.haversine(lat, lon, row[df2_lat], row[df2_lon]), axis=1)
            return df2.loc[distance.idxmin(), column_to_match]
        
        # By looping the first dataframe and then apply the function to loop the second dataframe
        df1.loc[:,column_to_match] = df1.apply(lambda row: find_nearest(row[df1_lat], row[df1_lon]), axis=1)

        # Merge the first and second dataframe together
        df = df1.merge(df2, how="left", on=column_to_match)

        # Calculate the difference between the both match
        df.loc[:,distance_column] = df.apply(lambda row: gp.haversine(lat1 = row[df1_lat], lon1 = row[df1_lon], lat2 = row[df2_lat], lon2 = row[df2_lon]), axis = 1)

        # Return the dataframe
        return df
    
    def ann(df:pd.DataFrame,
            n_column:str,
            a_column:str,
            distance_column:str,
            district_column:str = "district"):
        from math import sqrt
        from scipy.stats import norm
        
        n = df.loc[:,n_column].sum()
        area = df.drop_duplicates(subset=district_column).loc[:,a_column].sum()

        do = df.loc[:,distance_column].sum()/df.loc[:,n_column].sum()
        de = 0.5/sqrt(n/area)

        ann = do/de
        se = 0.26136/((sqrt(n*n/area)))
        z_score = (do-de)/se
        
        p_value = norm.sf(abs(z_score))

        dict = {"ANN":ann,
                "ann_z_score":z_score,
                "p_value":p_value}

        # Return the dictionary
        return dict