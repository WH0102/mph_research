import pandas as pd
import geopandas as gpd

class map:
    # Options
    # Allowed values which do not require a Mapbox API token are 
    # 'open-street-map', 'white-bg', 'carto-positron', 'carto-darkmatter', 'stamen- terrain', 'stamen-toner', 'stamen-watercolor'. 
    # Allowed values which do require a Mapbox API token are 
    # 'basic', 'streets', 'outdoors', 'light', 'dark', 'satellite', 'satellite- streets'.
    _map_center = {"lat": 4.389059008652357, "lon": 108.65244272591418}
    _mapbox_style = [
        'basic', 'streets', 'outdoors', 'light', 'dark', 'satellite', 'satellite- streets',
        'open-street-map', 'white-bg', 'carto-positron', 'carto-darkmatter', 'stamen-terrain', 'stamen-toner', 'stamen-watercolor'
    ]
    _color_scheme = [
        'aggrnyl', 'agsunset', 'algae', 'amp', 'armyrose', 'balance',
        'blackbody', 'bluered', 'blues', 'blugrn', 'bluyl', 'brbg',
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
    
    def get_polygon_area(df:gpd.GeoDataFrame,
                         geometry_column:str = "geometry",
                         area_column:str = "area",
                         final_crs:str = "EPSG:4326") -> gpd.GeoDataFrame:
        df = df.to_crs({'proj':'cea'})
        df.loc[:,area_column] = df.loc[:,geometry_column].area/ 10**6
        return df.to_crs(final_crs)
    
    def haversine(lat1, lon1, lat2, lon2):
        # Import necessary packages
        import numpy as np

        R = 6371.0 # Earth radius in kilometers

        # Radians both lat and lon
        lat1_rad, lon1_rad = np.radians(lat1), np.radians(lon1)
        lat2_rad, lon2_rad = np.radians(lat2), np.radians(lon2)

        # Calculate the difference between lat and lon
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        # Perform the Harversine as per wikipedia
        a = np.sin(dlat / 2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

        # Times with the earth raidus
        distance = R * c
        
        # Return the values
        return distance

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
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        
        # Return fig
        return fig
    
    def extract_coordinates(geometry):
        if geometry.geom_type == 'Polygon':
            return list(geometry.exterior.coords)
        elif geometry.geom_type == 'MultiPolygon':
            coords = []
            for polygon in geometry.geoms:
                coords.extend(list(polygon.exterior.coords))
            return coords
        else:
            return []
        
    def draw_polygon_line(df: gpd.GeoDataFrame,
                      polygon_name:str,
                      geometry_column:str = "geometry",
                      ) -> pd.DataFrame:
        # Import the necessary packages
        from plotly.express import scatter_mapbox
        # Extract coordinates for each feature
        df.loc[:,"coordinates"] = df.loc[:,geometry_column].apply(map.extract_coordinates)

        # Flatten the coordinates and prepare a DataFrame for Plotly
        coords_list = []
        for index, row in df.iterrows():
            for coord in row['coordinates']:
                coords_list.append({
                    'lon': coord[0],
                    'lat': coord[1],
                    'region': row[polygon_name]
                })

        # Create the lat lon with polygon line
        df_coords = pd.DataFrame(coords_list)

        # Create the polygon with plotly
        # Plot the borders of district
        return scatter_mapbox(
            df_coords,
            lat='lat',
            lon='lon',
            color="region",
            text="region",
        ).update_traces(mode='lines')
