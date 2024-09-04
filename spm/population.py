from .file import file
from .map import map
from .provider import provider
import polars as pl
import pandas as pd

class population:
    def prepare_ascii_file(gp_df:pd.DataFrame,
                           district_geojson:str,
                           parlimen_geojson:str,
                           population_ascii_file:str) -> pd.DataFrame:
        # Import necessary packages
        import geopandas as gpd

        # Read the geojson file of parlimen and district
        parlimen = gpd.read_file(parlimen_geojson)

        # To calculate the area for each district in km2
        district = gpd.read_file(district_geojson)
        district = district.to_crs({'proj':'cea'})
        district["area"] = district['geometry'].area/ 10**6
        district = district.to_crs('EPSG:4326')

        # Prepare the ascii xyz file downloaded from Worldpop.org, conver the xyz into geopandas dataframe
        population_ascii = map.convert_pandas_geopandas(pd.read_csv(population_ascii_file),lat="Y",lon="X")

        # Spatial join population with parlimen and district and drop unnecessary columns
        temp_population = population_ascii.sjoin(parlimen, how="inner")\
                                  .drop(columns=["state", "index_right", "code_state"])\
                                  .sjoin(district, how="inner")\
                                  .drop(columns=["index_right", "geometry"])
        
        # To ensure each point of lat lon within each parlimen have its own population
        temp_population = temp_population.merge(temp_population.pivot_table(index="code_parlimen", values="Z", aggfunc=sum)\
                                                               .reset_index().rename(columns={"Z":"parlimen_z"}),
                              how="left", on="code_parlimen")
        
        # To match the nearest GP for the population and calculate the distance between each point to their nearest gp
        population_gp = gp.match_nearest(df1=temp_population, df1_lat="Y", df1_lon="X",
                                         df2=gp_df, df2_lat="Latitude", df2_lon="Longitude",
                                         column_to_match="id")
        
        # Return the dataframe first
        return temp_population
    
    def merge_population_ascii(str_file:str,
                               merge_column:str,
                               str_count_columns:str|list|tuple,
                               population_ascii_dataframe:pd.DataFrame) -> pd.DataFrame:
        # To merge with dataframe from ProtectHealh, file from ProtectHealth
        str_df = pd.read_csv(str_file)
        
        # Merge the population_ascii_dataframe and str_df
        df = population_ascii_dataframe.merge(str_df, how="left", on=merge_column)

        # Calculate the str_population_per_grid
        if type(str_count_columns) == str:
          df.loc[:,"estimated_str"] = df.loc[:,str_count_columns] * df.loc[:,"Z"] / df.loc[:,"parlimen_z"]
        elif type(str_count_columns) == list | type(str_count_columns) == tuple:
            for column in str_count_columns:
                df.loc[:,f"estimated_{column}"] = df.loc[:,column] * df.loc[:,"Z"] / df.loc[:,"parlimen_z"]

        # Return the dataframe
        return df

    def ann(df:pl.DataFrame,
            n_column:str,
            a_column:str,
            distance_column:str,
            district_column:str = "district"):
        # Import the necessary packages
        from math import sqrt
        from scipy.stats import norm, spearmanr
        
        # For spearmanr r result
        sperman_result = spearmanr(df[n_column], df[distance_column])

        # Add up the population column
        n = df[n_column].sum()

        # To get area that have the population
        area = df.unique(subset=district_column)[a_column].sum()

        # To get district name
        if len(df.unique(subset=district_column)) > 1:
            district_name = f"{len(df.unique(subset=district_column))} districts"
        else:
            district_name = df.unique(subset=district_column)[district_column][0]

        # Calculate the observed mean of distance
        do = df[distance_column].sum()/df[n_column].sum()

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
        return pl.DataFrame({
            "district":[district_name],
            "min":[df[distance_column].min()],
            "median":[df[distance_column].median()],
            "iqr":[df[distance_column].quantile(0.75) - df[distance_column].quantile(0.25)],
            "max":[df[distance_column].max()],
            "spearman_r":[sperman_result[0]],
            "spearman_p_value":[sperman_result[1]],
            "ANN":[ann],
            "ann_z_score":[z_score],
            "p_value":[p_value]
            }) 



    def convert_str_to_long(df:pl.DataFrame) -> pl.DataFrame:
        # Return by having 3 polars dataframe, [beneficiary, partner, dependent]
        return pl.concat([df.select("id", "id_ben", "sex_beneficiary", "ori_ben_age", "str_category", "state", "code_parlimen")\
                            .rename({"ori_ben_age":"age", "sex_beneficiary":"sex"})\
                            .with_columns(pl.col("age").cast(pl.Int64)),
                          df.filter(pl.col("id_partner").is_not_null())\
                            .select("id", "id_partner", "sex_partner", "age_partner", "str_category", "state", "code_parlimen")\
                            .rename({"id_partner":"id_ben", "sex_partner":"sex", "age_partner":"age"})\
                            .with_columns(pl.col("age").cast(pl.Int64)),
                          df.filter(pl.col("id_dependent").is_not_null())\
                            .select("id", "id_dependent", "sex_dependent", "age_dependent", "str_category", "state", "code_parlimen")\
                            .rename({"id_dependent":"id_ben", "sex_dependent":"sex", "age_dependent":"age"})\
                            .with_columns(pl.col("age").cast(pl.Int64))])\
                 .unique(subset='id_ben')
    
    # def get_str_percentage_per_parlimen_district(parlimen_population_parquet:str = file._population_parlimen,
    #                                              parlimen_map_file:str = file._map_parlimen,
    #                                              district_map_file:str = file._map_district,
    #                                              str_df:pl.DataFrame = pl.read_parquet(file._file_spm_parquet)) -> pl.DataFrame:
    #     # Generated the file._population_str_parlimen_district
    #     # Import necessary packages
    #     import geopandas as gpd
    #     import pandas as pd
    #     # Read the necessary file
    #     parlimen_population = pl.read_parquet(parlimen_population_parquet)
    #     code_parlimen_df = gpd.read_file(parlimen_map_file).loc[:,("parlimen", "code_parlimen")]
    #     code_parlimen_district = pl.from_pandas(gpd.read_file(parlimen_map_file).sjoin(
    #                           gpd.read_file(district_map_file).drop(columns = ["state", "code_state"]))\
    #                                 .loc[:,("code_parlimen", "district", "code_state_district")])

    #     # Filter the parliment population date
    #     temp_df = parlimen_population.filter(pl.col("date").cast(pl.String) == "2022-01-01",
    #                                          pl.col("sex") == "both",
    #                                          pl.col("age") == "overall",
    #                                          pl.col("ethnicity") == "overall")\
    #                                 .with_columns(pl.col("population") * 1000).to_pandas()
    #     # Merge the filtered population file from DOSM to get code_parlimen
    #     temp_df = pl.from_pandas(temp_df.merge(code_parlimen_df, how="left", on="parlimen"))

    #     # Read the STR database
    #     long_df = population.convert_str_to_long(df = str_df)

    #     # Combine both the population from DOSM and STR then calculate the percentage
    #     percentage_df = temp_df.join(long_df.group_by("code_parlimen").len("str_count"),
    #                                 how="left", on="code_parlimen")\
    #                         .select("parlimen", "code_parlimen", (pl.col("str_count")/pl.col("population")).alias("str_percentage"))
    #     # return the dataframe
    #     return parlimen_population.join(percentage_df, how="left", on="parlimen")\
    #                               .join(code_parlimen_district, how="left", on="code_parlimen")
    
    def str_population_ascii(method:str) -> pl.DataFrame:
        # Generated the file._population_str_ascii_parlimen
        # Import packages
        import geopandas as gpd
        import pandas as pd

        # To merge the parlimen population from DOSM to geojson file to get teh code_parlimen
        parlimen_population = pl.read_parquet(file._population_parlimen)
        parlimen_population_geo = gpd.GeoDataFrame(data=parlimen_population.to_pandas()\
                                                        .merge(gpd.read_file(file._map_parlimen).drop(columns="state"), 
                                                                how="left", on="parlimen"),
                                                  geometry="geometry", crs='EPSG:4326')
        # Calculate the STR population according to parlimen
        if method == "individual":
          str_parlimen = population.convert_str_to_long(df = pl.read_parquet(file._file_spm_parquet))\
                              .group_by("code_parlimen").len("str_count")
        elif method == "households":
            str_parlimen = pl.read_parquet(file._file_spm_parquet)\
                              .unique(subset="id_ben")\
                              .group_by("code_parlimen").len("str_count")

        # Prepare on ASCII file
        population_ascii = map.convert_pandas_geopandas(pd.read_csv(file._population_ascii), lat="Y", lon="X")
        # Calculate the population per x, y by times the ratio between dosm population and ascii population then * growth rate to get population at year 2023
        population_ascii.loc[:,"ascii_population"] = population_ascii.loc[:,"Z"] * 32447100 /population_ascii.Z.sum() * 1.0287

        # Filter the parliment population date and then get the population per code parlimen
        temp_df = pl.from_pandas(parlimen_population_geo.drop(columns="geometry"))\
                    .filter(pl.col("date").cast(pl.Date).cast(pl.String) == "2020-01-01",
                                                pl.col("sex") == "both",
                                                pl.col("age") == "overall",
                                                pl.col("ethnicity") == "overall")\
                                    .with_columns(pl.col("population") * 1000)\
                    .group_by("code_parlimen").agg(pl.col("population").sum())
        
        # Merge with the str_parlimen population to get each percentage of str by each code_parlimen
        percentage_df = temp_df.join(str_parlimen, on="code_parlimen")\
                                .with_columns((pl.col("str_count")/pl.col("population")).alias("str_percentage"))

        # Merge both ascii and parlimen_population, then join with the percetage above, then times with the projected 2023 population and str ratio to get estimated population of str per lat lon
        temp_df = pl.from_pandas(gpd.sjoin(parlimen_population_geo, population_ascii)\
                    .loc[:,("date", "state", "sex", "age", "ethnicity", "population", "code_parlimen", "X", "Y", "ascii_population")])\
                    .with_columns(pl.col("date").cast(pl.Date))\
                    .join(percentage_df.select("code_parlimen", "str_percentage"), how="left", on ="code_parlimen")\
                    .with_columns((pl.col("ascii_population") * pl.col("str_percentage")).alias("str_ascii"))
        
        # Due to forget to add district, need to convert the temp_df to geopandas again
        temp_df = map.convert_pandas_geopandas(temp_df.to_pandas(), lat="Y", lon="X")

        # Spatial join with district map file and then return the df
        final_df = temp_df.sjoin(gpd.read_file(file._map_district).drop(columns="state")).drop(columns = ["geometry", "index_right"])\
        
        # Return the dataframe
        return pl.from_pandas(final_df).with_columns(pl.col("date").cast(pl.Date))