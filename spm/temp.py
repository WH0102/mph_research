import pandas as pd
import geopandas as gpd
from datetime import datetime

class map:
    def convert_pandas_geopandas(df:pd.DataFrame,
                                 lon:str,
                                 lat:str,
                                 crs:str = 'EPSG:4326') -> gpd.GeoDataFrame:
        # Import necessary packages
        from shapely.geometry import Point

        # Changet the point for lat lon
        df["geometry"] = df.apply(lambda row: Point(row[lon], row[lat]), axis=1)

        # Return the dataframe
        return gpd.GeoDataFrame(df, geometry='geometry', crs=crs)
    
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
            distance = df2.apply(lambda row: map.haversine(lat, lon, row[df2_lat], row[df2_lon]), axis=1)
            return df2.loc[distance.idxmin(), column_to_match]
        
        # By looping the first dataframe and then apply the function to loop the second dataframe
        df1.loc[:,column_to_match] = df1.apply(lambda row: find_nearest(row[df1_lat], row[df1_lon]), axis=1)

        # Merge the first and second dataframe together
        df = df1.merge(df2, how="left", on=column_to_match)

        # Calculate the difference between the both match
        df.loc[:,distance_column] = df.apply(lambda row: map.haversine(lat1 = row[df1_lat], lon1 = row[df1_lon], lat2 = row[df2_lat], lon2 = row[df2_lon]), axis = 1)

        # Return the dataframe
        return df

def main():
    print(datetime.now())
    all_gp = pd.read_excel("/Users/wh0102/Downloads/github/mph_research/data/information/private_medical_gp.xlsx", 
                        sheet_name = "gp_list")
    population = pd.read_parquet("/Users/wh0102/Downloads/github/mph_research/data/information/ascii_household_and_gp.parquet")\
                .rename(columns={"X":'lon', "Y":"lat"})

    # temp_pop = map.convert_pandas_geopandas(population.loc[:,("lat", "lon", "Z", "estimated_str", "code_parlimen", "code_state_district", "code_state")],
    #                                         lat="lat", lon="lon")
    # all_gp = map.convert_pandas_geopandas(all_gp, lat="Latitude", lon="Longitude")

    temp_match = map.match_nearest(df1 = population, df1_lat="lat", df1_lon = "lon",
                                   df2 = all_gp, df2_lat="Latitude", df2_lon="Longitude",
                                   column_to_match = "BIL")
    temp_match.to_parquet("/Users/wh0102/Downloads/github/mph_research/data/information/ascii_all_gp.parquet", engine="pyarrow")
    print(datetime.now())
    
if __name__ == "__main__":
    main()