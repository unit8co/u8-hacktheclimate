# Import streamlit pandas and geopandas
import os
from datetime import datetime, timedelta

import ee
# Import folium and related plugins
import folium
import streamlit as st
import streamlit.components.v1 as components
from altair import Scale, Y

from methane_helper.data import methane_hotspots
from methane_helper.data.infra_data import *
from methane_helper.utils import geo_utils
from methane_helper.utils.ee_utils import (
    get_image_collection, get_methane_ts_from_polygon
)
from methane_helper.utils.folium_utils import add_ee_layer, add_circle, add_geo_markers_to_map, add_geo_polygons_to_map
from methane_helper.utils.geo_utils import str_to_geoson


@st.cache
def load_methane_data():
    return get_image_collection(
        'COPERNICUS/S5P/OFFL/L3_CH4',
        'CH4_column_volume_mixing_ratio_dry_air',
        (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
        datetime.now().strftime("%Y-%m-%d")
    )


@st.cache
def load_ir_data():
    return get_image_collection(
        'COPERNICUS/S2_SR',
        'B11',
        (datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d"),
        datetime.now().strftime("%Y-%m-%d")
    )


def add_infra_markers(folium_map, center, max_distance):
    add_circle(folium_map, center, max_distance)

    # TODO improve labeling
    add_geo_markers_to_map(folium_map, center, max_distance, load_coal_mines(), 'Coal Mines', 'operator', 'fire', 'gray')
    add_geo_markers_to_map(folium_map, center, max_distance, load_power_plants(), 'Power Plants', 'name', 'plug', 'blue')
    add_geo_markers_to_map(folium_map, center, max_distance, load_steel_plants(), 'Steel Plants', 'name', 'industry', 'green')

    add_geo_polygons_to_map(folium_map, center, max_distance, pipelines_as_gdf(), 'route', 'Pipelines', 'name', '#A06B2B')


def extract_hotspot_repr():
    return str_to_geoson(methane_hotspots.HOTSPOTS)


def repr_hotspot(meth_img, ir_img, hotspot):
    feature = hotspot
    feature['fill_color'] = 'red'
    map_center = geo_utils.get_feature_center(feature)

    folium.Map.add_ee_layer = add_ee_layer
    folium_map = folium.Map(map_center, tiles='OpenStreetMap', zoom_start=7)

    add_methane_to_map(meth_img, folium_map)
    add_ir_to_map(ir_img, folium_map)

    style = {'fillColor': '#e80e0e', 'color': '#911414', 'fillOpacity': 1}
    folium.GeoJson(
        feature,
        name="hotspot",
        style_function = lambda x: style
    ).add_to(folium_map)

    # Add markers for all NEARBY infrastructure
    add_infra_markers(folium_map, map_center, 5e4)

    return folium_map


def add_methane_to_map(image_col, fol_map):
    image_col = image_col.mean()

    # Set visualization parameters.
    vis_params = {
        'min': 1750,
        'max': 1970,
        'palette': ['black', 'blue', 'purple', 'cyan', 'green', 'yellow', 'red']
    }

    # Add the elevation model to the map object.
    fol_map.add_ee_layer(image_col, vis_params, 'S5P CH4')


def add_ir_to_map(image_col, fol_map):
    image_col = image_col.max()

    # Set visualization parameters.
    band_viz_B11 = {
        'min': 0,
        'max': 8300,
        'bands': 'B11',
        'palette': ['black', 'blue', 'purple', 'cyan', 'green', 'yellow', 'red']
    }

    # Add the elevation model to the map object.
    fol_map.add_ee_layer(image_col, band_viz_B11, 'Infrared', show=False)


def display_map(meth_img, ir_img, hotspot):
    m = repr_hotspot(meth_img, ir_img, hotspot)
    # Add a layer control panel to the map.
    m.add_child(folium.LayerControl())

    html_string = m.get_root().render()

    return components.html(html_string, height=600, width=900)


def display_methane_ts(hotspot):
    df = get_methane_ts_from_polygon(
        hotspot,
        (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
        datetime.now().strftime("%Y-%m-%d")
    )

    st.line_chart(df['methane_level'])


## Adding a background to streamlit page
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def authenticate_google_service_account() -> None:
    json_file_name = "gsa.json"

    if "GSA_JSON" in os.environ:
        json_auth = os.environ["GSA_JSON"]
    else:
        with open("/mount/data/data/hacktheclimate-308416-d1d36f96dfcf.json", mode="r") as f:
            json_auth = f.read()

    with open(json_file_name, mode="w") as f:
        f.write(json_auth)

    service_account = 'hacktheclimate-sa@hacktheclimate-308416.iam.gserviceaccount.com'
    credentials = ee.ServiceAccountCredentials(service_account, json_file_name)
    ee.Initialize(credentials)


PAGES = {
    "Home": 'home',
    "Hotspots": 'hotspots'
}


def main():
    authenticate_google_service_account()
    st.set_page_config(layout="wide")

    # Page Navigation
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))

    page = PAGES[selection]

    hotspots = extract_hotspot_repr()

    with st.spinner(f"Loading {page} ..."):
        if page == 'hotspots':
            hotspot_names = {'Hotspot {} - {}'.format(i, hotspots.features[i].geometry.coordinates[0][0]): i for i in range(0, len(hotspots.features))}
            sel_hotspot = st.sidebar.selectbox(
                "Select Hotspot", options=list(hotspot_names.keys())
            )
            hotspot_index = hotspot_names[sel_hotspot]
            hotspot = hotspots[hotspot_index]

            # Load csv data
            meth_img = load_methane_data()
            ir_img = load_ir_data()

            st.header("Detecting major methane hotspots around the World")
            st.text("")
            st.markdown(
                '<p class="big-font">This web-app detects probable methane leaks in the past 12 days, and handily provides you an easy view of nearby infrastructure, and other visual components like infra-red imaging.</p>',
                unsafe_allow_html=True)
            st.text("")

            # Create and add the folium map by passing the gee image and hotspot feature
            display_map(meth_img, ir_img, hotspot)

            st.text(
                "Criticality: {:.2f}; Plant Distance: {:.2f}; Pipeline Distance: {:.2f}; Infra Distance: {:.2f}; Start Date: {}; End Date: {}"
                .format(
                    hotspot.properties['criticality']*1000,
                    hotspot.properties['min_distance_to_plant'],
                    hotspot.properties['min_distance_to_pipeline'],
                    hotspot.properties['min_distance_to_infra'],
                    hotspot.properties['start_date'],
                    hotspot.properties['end_date'],
                )
            )

            # Create the timeseries for overall methane in polygon in last month
            display_methane_ts(hotspot)

        else:
            st.header("Detecting major methane hotspots around the World")
            st.text("")
            st.markdown("""## Inspiration

We are entering the last 2 decades before climate change becomes irreversible. Methane is a large contributor to global warming and there is a lack of accountability for large pollution events, especially by  the coal/fossil and gas industry

New satellite imaging has recently allowed to keep track of methane emissions close to real-time. However, access to the data and the potential methane leak event is still complicated. We think we can make that simpler so people can be aware of new leaks as they arrive and enable them to take actions

## What it does

Our tool uses satellite data from (Sentinel 5P and other sources) to automatically detect new potential methane leaks by custering abnormal emissions and linking them to the fossil infrastructure.

An easy UI allows then everyone to look at recent methane events and get more information on what happens: criticality of event, size, location, visual images.

We hope that gives an easy tool for people to track and then easily raise awareness on such events as they unfold

## How we built it

* Use Google Earth Engine to access methane, IR and wind data
* Extract all methane hotspots by abnormal methane cluster
* Link these "hotspots" to the fossil infratructure (mines, plants and pipelines)
* Assess the link between the event and the infrastructure and create a criticality score for events
* Automate the pipeline using Azure function so it refreshes daily 
* Create a user-friendly UI to be able to monitor all events detected with all required contextual information

## Challenges we ran into

* Google Earth Engine is not so user friendly and exporting data from it is challenging
* Identifying methane clusters was challenging. We think we can still improve the detection with more complex logic by better including infrared and with more complex models

## Accomplishments that we're proud of

* Developed an E2E pipeline for detecting methane hotspots linekd to fossile infrastructure
* An easy-to-use UI that run and gets refreshed automatically that can already be used

## What we learned

* Geosatellite data is its own beast
* Methane data is hard to access and any initiative to make it easier to work on it will be helpful to others
* Don't give up, things work out in the end

## What's next for Methane Leaks - Unit8 Climate

* Get feedback on current tools
* Work on improving model and espcially how to best link detected events with a precise source""")


if __name__ == "__main__":
    main()
