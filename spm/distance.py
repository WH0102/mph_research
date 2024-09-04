import pandas as pd

class distance:
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
            distance = df2.apply(lambda row: distance.haversine(lat, lon, row[df2_lat], row[df2_lon]), axis=1)
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
    
    def ann(df:pd.DataFrame,
            n_column:str,
            a_column:str,
            distance_column:str,
            district_column:str = "district"):
        # Import the necessary packages
        from math import sqrt
        from scipy.stats import norm
        
        # Add up the population column
        n = df.loc[:,n_column].sum()

        # To get area that have the population
        area = df.drop_duplicates(subset=district_column).loc[:,a_column].max()

        # Calculate the observed mean of distance
        do = df.loc[:,distance_column].sum()/df.loc[:,n_column].sum()

        # Calculate the expected mean of distance
        de = 0.5/sqrt(n/area)

        # Calculate the ANN
        ann = do/de

        # Calculate the standard error
        se = 0.26136/((sqrt(n*n/area)))

        # Calculate the z-score
        z_score = (do-de)/se

        # Get the p value for the z score
        p_value = norm.sf(abs(z_score))

        # For the dictionary and return
        return {"ANN":ann,
                "ann_z_score":z_score,
                "p_value":p_value}