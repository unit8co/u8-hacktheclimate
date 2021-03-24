# Import streamlit pandas and geopandas
import os

import streamlit as st
import pandas as pd
import ee
from utils.folium_utils import add_ee_layer
from utils.df_utils import ee_array_to_df
from utils.ee_utils import (
    get_region_image,
    get_image_collection
)

import numpy as np
import geopandas as gpd

# Import folium and related plugins
import folium
from folium import Marker
from folium.plugins import MarkerCluster

# Geopy's Nominatim
from geopy.geocoders import Nominatim

# Scipy's Spatial
from scipy import spatial

import requests
from io import StringIO
from io import BytesIO

import json


# Get the data from url and request it as json file

@st.cache
### This function reads a csv file which contains a list of concentrations by latitude and longitude
def load_data():
    # print(methane_image.getInfo()[:5])

    return get_image_collection('COPERNICUS/S5P/OFFL/L3_CH4', 'CH4_column_volume_mixing_ratio_dry_air',
                                              '2020-04-01', '2020-07-16')


def get_methane_image(img_col):
    return get_region_image(img_col, 4.8148, 45.7758)


# This function loads a geoJSON file with Oakland city boundary.
def load_oakl_data():
    original_url_oakl = "https://drive.google.com/file/d/1I008pOw0Qz0ARNVC8eBqhEt325DDU_yq/view?usp=sharing"
    file_id_oakl = original_url_oakl.split('/')[-2]
    dwn_url_oakl = 'https://drive.google.com/uc?export=download&id=' + file_id_oakl
    url_oakl = requests.get(dwn_url_oakl).content
    return url_oakl


# path_oakl = BytesIO(url_oakl)
# oakl_geo = gpd.read_file(path_oakl, driver = 'GeoJSON',encoding="utf-8")


def convert_address(address):
    # Here we use Nominatin to convert address to a latitude/longitude coordinates"
    geolocator = Nominatim(user_agent="my_app")  # using open street map API
    Geo_Coordinate = geolocator.geocode(address)
    lat = Geo_Coordinate.latitude
    lon = Geo_Coordinate.longitude
    # Convert the lat long into a list and store is as point
    point = [lat, lon]
    return point


def display_map(point, image_col, oakl_geojson):
    print(get_methane_image(image_col).getInfo()[:25])
    df = ee_array_to_df(get_methane_image(image_col).getInfo(), ['CH4_column_volume_mixing_ratio_dry_air'])

    print(df)
    folium.Map.add_ee_layer = add_ee_layer
    m = folium.Map(point, tiles='OpenStreetMap', zoom_start=11)
    image_col = image_col.mean()
    # Add polygon boundary to folium map
    folium.GeoJson(oakl_geojson, style_function=lambda x: {'color': 'blue', 'weight': 2.5, 'fillOpacity': 0},
                   name='Oakland').add_to(m)

    # Add marker for Location
    folium.Marker(location=point,
                  popup="""
                  <i>BC Concentration: </i> <br> <b>{}</b> ug/m3 <br> <hr>
                  <i>NO<sub>2</sub> Concentration: </i><b><br>{}</b> ppb <br>
                  """.format(
                      'place1',
                      'place2'),
                  icon=folium.Icon()).add_to(m)

    # Set visualization parameters.
    vis_params = {
        'min': 1000,
        'max': 2000,
        'palette': ['blue', 'green', 'yellow', 'red']
    }

    # Add the elevation model to the map object.
    m.add_ee_layer(image_col.updateMask(image_col.gt(1900)), vis_params, 'S5P CH4')

    # Add a layer control panel to the map.
    m.add_child(folium.LayerControl())

    return st.markdown(m._repr_html_(), unsafe_allow_html=True)


## Adding a background to streamlit page
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def authenticate_google_service_account() -> None:
    json_file_name = "gsa.json"
    with open(json_file_name, mode="w") as f:
        f.write(os.environ["GSA_JSON"])
    service_account = 'hacktheclimate-sa@hacktheclimate-308416.iam.gserviceaccount.com'
    credentials = ee.ServiceAccountCredentials(service_account, json_file_name)
    ee.Initialize(credentials)


def main():
    authenticate_google_service_account()
    # Load csv data
    image = load_data()

    # Load geoJSON file using json.loadas
    oakl_json = load_oakl_data()
    oakl_json = oakl_json.decode("utf-8")
    oakl_geojson = json.loads(oakl_json)

    # For the page display, create headers and subheader, and get an input address from the user
    local_css("style.css")
    st.header("Predicting Air Quality in Oakland, California")
    st.text("")
    st.markdown(
        '<p class="big-font">This web-app reports annual average concentrations of Black Carbon and Nitrogen Dioxide in Oakland. Concentrations are based on a machine learning model built to make predictions at any location in Oakland using publicly available data on major sources of emissions in Oakland and neighbouring cities, number of traffic intersections, proximity to highways, and local meteorological data.</p>',
        unsafe_allow_html=True)
    st.text("")
    st.markdown(
        '<p class="big-font"> <b> Enter an address below and click on the marker to know the air quality at your place of interest. </b> </p>',
        unsafe_allow_html=True)

    address = st.text_input("  ", "900 Fallon St, Oakland, CA 94607")

    # Use the convert_address function to convert address to coordinates
    coordinates = convert_address(address)

    # Call the display_map function by passing coordinates, dataframe and geoJSON file
    st.text("")
    display_map(coordinates, image, oakl_geojson)


if __name__ == "__main__":
    main()
