import polars as pl

class descriptive:
    def pivot_with_percentage(df:pl.DataFrame,
                              columns:str,
                              name:str = "Number of Households") -> pl.DataFrame:
        pt = df.group_by(columns).len(name)
        return pt.with_columns((pl.col(name) / pl.col(name).sum() * 100).alias("Percentage"))
    
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

    def gender_distribution(df:pl.DataFrame) -> pl.DataFrame:
        # To find unique beneficiary ID, then pivot their sex
        sex_ben_pt = df.unique(subset="id_ben")\
               .select("id_ben", "sex_beneficiary").to_pandas()\
               .pivot_table(index="sex_beneficiary", values="id_ben", aggfunc=len, margins=True)\
               .rename(columns={"id_ben":"ben_count"})

        # To find unique partner ID, then pivot their sex
        sex_partner_pt = df.filter(pl.col("id_partner").is_not_null())\
                        .unique(subset="id_partner")\
                        .select("id_partner", "sex_partner").to_pandas()\
                        .pivot_table(index="sex_partner", values="id_partner", aggfunc=len, margins=True)\
                        .rename(columns={"id_partner":"partner_count"})

        # To merge both pivot table result, rename the Malay term into english
        sex_pt = sex_ben_pt.merge(sex_partner_pt, left_index=True, right_index=True)\
                        .rename(index={"LELAKI":"male", "PEREMPUAN":"female"})

        # Calculate the total count
        sex_pt.loc[:,"total_count"] = sex_pt.loc[:,"ben_count"] + sex_pt.loc[:,"partner_count"]

        # To calculate the percentage for each column and rount it to 2 decimal
        for column in sex_pt.columns:
            sex_pt.loc[:,f"{column}_%"] = (sex_pt.loc[:,column] / sex_pt.loc[:,"total_count"] * 100).round(2)

        # Reindex the column so that percentage will be besides each type and then remove the unnamed index before return the dataframe
        sex_pt = sex_pt.reindex(columns=sex_pt.columns.sort_values())\
                       .reset_index()\
                       .rename(columns={"index":"sex"})
        
        # Return the dataframe
        return pl.from_pandas(sex_pt)
    

    def calculate_average_nearest_neighbor(clinic_data, population_data):
        # Convert clinic data to GeoPandas GeoDataFrame
        # clinic_gdf = gpd.GeoDataFrame(clinic_data, 
        #                               geometry=gpd.points_from_xy(clinic_data["Longitude"], clinic_data["Latitude"]))
        
        # Ensure both GeoDataFrames have the same CRS
        # clinic_gdf = clinic_gdf.to_crs('EPSG:4326')

        # Calculate nearest neighbor distances
        distances = []
        for index, clinic in clinic_data.iterrows():
            nearest_distance = clinic["geometry"].distance(population_data.geometry)
            distances.append(nearest_distance)

        # Calculate Average Nearest Neighbor Distance
        return sum(distances) / len(distances)