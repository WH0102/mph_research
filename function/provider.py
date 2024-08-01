from function.file import file
import pandas as pd
import geopandas as gpd

class gp:
    _district_list = ['14_1', '10_8', '10_1', '10_5', '10_2', '8_3', '7_4', '1_2']
    _state_list = [14, 10, 8, 7, 1]
    _parlimen_list = ['P.048', 'P.049', 'P.050', 'P.051', 'P.052', 'P.053', 'P.062',
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