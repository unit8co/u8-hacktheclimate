# Import streamlit pandas and geopandas
import os
import ee
# Import folium and related plugins
import folium
import streamlit as st
import streamlit.components.v1 as components

from methane_helper.data import methane_hotspots
from methane_helper.data.infra_data import *
from methane_helper.utils import geo_utils
from methane_helper.utils.ee_utils import (
    get_region_image,
    get_image_collection
)
from methane_helper.utils.folium_utils import add_ee_layer, add_circle, add_geo_markers_to_map, add_geo_polygons_to_map
from methane_helper.utils.geo_utils import str_to_geoson


@st.cache
def load_methane_data():
    return get_image_collection('COPERNICUS/S5P/OFFL/L3_CH4', 'CH4_column_volume_mixing_ratio_dry_air',
                                '2020-04-01', '2021-04-01')


def add_infra_markers(folium_map, center, max_distance):
    add_circle(folium_map, center, max_distance)

    # TODO improve labeling
    add_geo_markers_to_map(folium_map, center, max_distance, load_coal_mines(), 'Coal Mines', 'operator', 'fire', 'gray')
    add_geo_markers_to_map(folium_map, center, max_distance, load_power_plants(), 'Power Plants', 'name', 'plug', 'blue')
    add_geo_markers_to_map(folium_map, center, max_distance, load_steel_plants(), 'Steel Plants', 'name', 'industry', 'green')

    add_geo_polygons_to_map(folium_map, center, max_distance, pipelines_as_gdf(), 'route', 'Pipelines', 'name')


def extract_hotspot_repr():
    return str_to_geoson(methane_hotspots.HOTSPOTS)


def repr_hotspot(index):
    feature = extract_hotspot_repr()[index]
    feature['fill_color'] = 'red'
    map_center = geo_utils.get_feature_center(feature)

    folium.Map.add_ee_layer = add_ee_layer
    folium_map = folium.Map(map_center, tiles='OpenStreetMap', zoom_start=7)
    folium.GeoJson(feature, name="hotspot").add_to(folium_map)

    # Add markers for all NEARBY infrastructure
    add_infra_markers(folium_map, map_center, 5e5)

    return folium_map


def display_map(image_col, hotspot_index):
    m = repr_hotspot(hotspot_index)
    image_col = image_col.mean()

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

    html_string = m.get_root().render()

    return components.html(html_string, height=600, width=900)


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


PAGES = {
    "Home": 'home',
    "Hotspots": 'hotspots',
    "Overall View": 'overall'
}


def main():
    authenticate_google_service_account()

    # Page Navigation
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))

    page = PAGES[selection]
    hotspot_index = 0

    with st.spinner(f"Loading {selection} ..."):
        if page == 'hotspots':
            hotspots = {'Hotspot {}'.format(i): i for i in range(0, len(extract_hotspot_repr().features))}
            hotspot = st.sidebar.selectbox(
                "Select Hotspot", options=list(hotspots.keys())
            )
            hotspot_index = hotspots[hotspot]

    # Load csv data
    image = load_methane_data()

    # For the page display, create headers and subheader, and get an input address from the user
    local_css("style.css")
    st.header("Detecting major methane hotspots around the World")
    st.text("")
    st.markdown(
        '<p class="big-font">This web-app detects probable methane leaks in the past 12 days, and handily provides you an easy view of nearby infrastructure, and other visual components like wind direction and infra-red imaging.</p>',
        unsafe_allow_html=True)
    st.text("")

    # Call the display_map function by passing the gee image
    display_map(image, hotspot_index)


if __name__ == "__main__":
    main()
