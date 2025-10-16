import pandas as pd
import numpy as np
import geopandas as gpd
import osmnx as ox

class DataProcessor:
    def __init__(self):
        self.data_description = "Transactions Dataset"
        self.data = None

    def load_data(self):
        data = pd.read_csv("data/transactions.csv")
        data['Date of Transaction'] = pd.to_datetime(data['Date of Transaction'])
        data['Date'] = data['Date of Transaction'].dt.date
        self.data = data
        return data

    def load_geodata(self):
        mapping_countries = {
            'Brazil': 'Brazil',
            'China': 'China',
            'India': 'India',
            'Russia': 'Russia',
            'Singapore': 'Singapore',
            'South Africa': 'South Africa',
            'Switzerland': 'Switzerland',
            'United Arab Emirates': 'UAE',
            'United Kingdom': 'UK',
            'United States of America': 'USA'}
        # Load Singapore shapefile
        gdf_singapore = ox.geocode_to_gdf("Singapore")
        gdf_singapore = gdf_singapore.to_crs("EPSG:4326")          # lat/lon

        poly = gdf_singapore.loc[0, 'geometry']

        singapore = {'admin': 'Singapore', 'iso_a3': 'SGP', 'geometry': poly}

        # Load world countries shapefile
        world = gpd.read_file('data/custom.geo.json')
        countries = ['United States of America', 'South Africa', 'Switzerland', 'Russia', 
             'Brazil', 'United Kingdom', 'India', 'China', 'Singapore', 
             'United Arab Emirates']
        gdf_countries = world[world['admin'].isin(countries)]
        gdf_countries = gdf_countries.drop(columns=['featurecla', 'scalerank', 'labelrank', 'sovereignt', 'sov_a3', 'adm0_dif', 'level'])
        gdf_countries = gdf_countries[['admin', 'geometry', 'iso_a3']]

        gdf_countries['admin'] = gdf_countries['admin'].map(mapping_countries)
        gdf_countries.loc[len(gdf_countries)] = singapore

        gdf_countries['rep_point'] = gdf_countries['geometry'].representative_point()
        gdf_countries.set_crs(epsg=4326, inplace=True)
        self.geodata = gdf_countries
        return gdf_countries

    def get_data(self):
        data = self.load_data()
        gdf_countries = self.load_geodata()
        merge_data = data.merge(gdf_countries, left_on='Country', right_on='admin', how='left')
        self.merge_data = merge_data
        self.iso_a3_dict = merge_data[['Country', 'iso_a3']].drop_duplicates().set_index('Country')['iso_a3'].to_dict()
        return merge_data
