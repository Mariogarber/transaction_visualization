import pandas as pd
import numpy as np
import geopandas as gpd
import osmnx as ox

class DataManager:
    def __init__(self):
        self.data_description = "Transactions Dataset"
        self.data = None
        self.data_by_country = None

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

    def set_data_by_country(self):
        if self.data is None:
            self.load_data()
        self.data_by_country = {country: df for country, df in self.data.groupby('Country')}
        return self.data_by_country
    
    def get_country_data(self, country):
        if self.data_by_country is None:
            self.set_data_by_country()
        return self.data_by_country.get(country, pd.DataFrame())
    
    def set_folium_data(self):
        clean_data = self.data[['Country', 'Reported by Authority', 'Source of Money', 'Amount (USD)', 'Transaction Type']]
        clean_data_illegal = clean_data[clean_data['Source of Money'] == 'Illegal']
        data_country = clean_data_illegal.groupby('Country')
        map_illegal_data = {}
        map_transactions_data = {}
        for country, group in data_country:
            illegal_count = group['Reported by Authority'].sum()
            illegal_total = len(group)
            map_illegal_data[country] = illegal_count / illegal_total if illegal_total > 0 else 0

            transaction_counts = group['Transaction Type'].value_counts().to_dict()
            map_transactions_data[country] = transaction_counts

        self.folium_map = {
            "map_illegal_data": map_illegal_data,
            "map_transactions_data": map_transactions_data,
            "clean_data_illegal": clean_data_illegal,
            "geo_data": self.geodata
        }
        return self.folium_map

    def set_arrow_data(self):
        # Obtenemos coordenadas (lat/lon) a partir del punto representativo
        transaction = self.merge_data
        transaction_info = transaction[['iso_a3', 'rep_point', 'Destination Country', 'Amount (USD)', 'Date']].drop_duplicates()

        transaction_info['rep_point_origin'] = transaction_info['rep_point']
        transaction_info['rep_point_destination'] = transaction_info['Destination Country'].map(self.geodata.set_index('admin')['rep_point'])

        transaction_info['o_lat'] = transaction_info['rep_point_origin'].apply(lambda point: point.y)
        transaction_info['o_lon'] = transaction_info['rep_point_origin'].apply(lambda point: point.x)
        transaction_info['d_lat'] = transaction_info['rep_point_destination'].apply(lambda point: point.y)
        transaction_info['d_lon'] = transaction_info['rep_point_destination'].apply(lambda point: point.x)

        transaction_info['iso_a3_dest'] = transaction_info['Destination Country'].map(self.iso_a3_dict)

        # obtain origin and destination coordinates
        flows_df = pd.DataFrame(transaction_info)
        flows = flows_df.rename(columns={'Amount (USD)': 'amount', 'iso_a3': 'origin_iso_a3', 'iso_a3_dest': 'dest_iso_a3'})
        self.flows = flows
        return flows

    def filter_flows(self, arrow_options, country, date):
        flows_on_date = self.flows[self.flows['Date'] == pd.to_datetime(date).date()]

        # Filter based on country and arrow options
        if country != 'ALL':
            if 'origin' in arrow_options and 'destiny' not in arrow_options:
                flows_on_date = flows_on_date[flows_on_date['origin_iso_a3'] == self.iso_a3_dict[country]]
            elif 'destiny' in arrow_options and 'origin' not in arrow_options:
                flows_on_date = flows_on_date[flows_on_date['dest_iso_a3'] == self.iso_a3_dict[country]]
            else:
                flows_on_date = flows_on_date[(flows_on_date['origin_iso_a3'] == self.iso_a3_dict[country]) | 
                                              (flows_on_date['dest_iso_a3'] == self.iso_a3_dict[country])]
                
        show_arrows = True
        if 'origin' in arrow_options and 'destiny' in arrow_options:
            total_received = flows_on_date.groupby('dest_iso_a3')['amount'].sum()
            total_sent = flows_on_date.groupby('origin_iso_a3')['amount'].sum() * -1
            total = total_received.add(total_sent, fill_value=0)
        elif 'origin' in arrow_options:
            total = flows_on_date.groupby('origin_iso_a3')['amount'].sum() * -1
        elif 'destiny' in arrow_options:
            total = flows_on_date.groupby('dest_iso_a3')['amount'].sum()
        else:
            total = pd.Series(np.zeros(len(self.geodata)), index=self.geodata['iso_a3'])
            show_arrows = False
        min_amt, max_amt = total.min(), total.max()

        self.flows_info = {
            "flows": flows_on_date,
            "total": total,
            "min_amt": min_amt,
            "max_amt": max_amt,
            "show_arrows": show_arrows,
            "gdf_countries": self.geodata,
            "selected_date": date
        }
                
        return self.flows_info