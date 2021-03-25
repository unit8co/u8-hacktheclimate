# Import streamlit pandas and geopandas
import os

import ee
# Import folium and related plugins
import folium
import streamlit as st
import streamlit.components.v1 as components

from methane_helper.data.infra_data import *
from methane_helper.utils.ee_utils import (
    get_region_image,
    get_image_collection
)
from methane_helper.utils.folium_utils import add_ee_layer
from methane_helper.utils.folium_utils import add_geo_markers_to_map


@st.cache
### This function reads a csv file which contains a list of concentrations by latitude and longitude
def load_data():
    # print(methane_image.getInfo()[:5])

    return get_image_collection('COPERNICUS/S5P/OFFL/L3_CH4', 'CH4_column_volume_mixing_ratio_dry_air',
                                '2020-04-01', '2020-07-16')


def get_methane_image(img_col):
    return get_region_image(img_col, 4.8148, 45.7758)


def add_infra_markers(folium_map):
    # TODO improve labeling (especially coal and steel)
    add_geo_markers_to_map(folium_map, load_coal_mines(), 'Coal Mines', 'operator', 'fire', 'gray')
    ##add_geo_markers_to_map(folium_map, load_fossil_pipelines(), 'Pipelines', 'name')
    add_geo_markers_to_map(folium_map, load_power_plants(), 'Power Plants', 'name', 'plug', 'blue')
    add_geo_markers_to_map(folium_map, load_steel_plants(), 'Steel Plants', 'name', 'industry', 'green')


def display_map(image_col):
    folium.Map.add_ee_layer = add_ee_layer
    m = folium.Map(tiles='OpenStreetMap', zoom_start=1)
    image_col = image_col.mean()

    # Add markers for all infrastructure
    add_infra_markers(m)

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
    print('HERE')
    m.save("html_example.html")

    with open("html_example.html", mode="r", encoding='utf-8') as f:
        html_string = f.read()

    return components.html(html_string, height=600)


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

    # Call the display_map function by passing coordinates, dataframe and geoJSON file
    st.text("")
    display_map(image)


if __name__ == "__main__":
    main()
