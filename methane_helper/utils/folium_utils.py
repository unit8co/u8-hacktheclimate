import ee
import folium
from shapely.geometry import Point

import io
import base64

from methane_helper.utils.geo_utils import point_distance, shape_distance, flip_geojson_coordinates


def add_ee_layer(self, ee_image_object, vis_params, name, opacity=0.5, show=True):
    map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)

    folium.raster_layers.TileLayer(
        tiles=map_id_dict['tile_fetcher'].url_format,
        attr="Map Data © Google Earth Engine",
        name=name,
        overlay=True,
        control=True,
        opacity=opacity,
        show=show
    ).add_to(self)


def add_geo_markers_to_map(folium_map, center, max_distance, df,
                           group_name: str, label_col: str, icon: str, color: str,
                           show: bool = True):
    feature_group = folium.map.FeatureGroup(name=group_name, show=show)
    folium_map.add_child(feature_group)
    latitudes = list(df.lat)
    longitudes = list(df.lng)
    labels = list(df[label_col])

    for lat, lng, label in zip(latitudes, longitudes, labels):
        if point_distance([lat, lng], center) < max_distance:
            folium.Marker(
                location=[lat, lng],
                popup=label,
                icon=folium.Icon(color=color, icon=icon, prefix='fa')
            ).add_to(feature_group)


def add_geo_polygons_to_map(folium_map, center, max_distance, df, polygon_col,
                            group_name: str, label_col: str, color: str,
                            show: bool = True):
    feature_group = folium.map.FeatureGroup(name=group_name, show=show)
    folium_map.add_child(feature_group)
    polygons = list(df[df[polygon_col].notnull()][polygon_col])
    labels = list(df[label_col])

    style = {'fillColor': color, 'color': color}

    for polygon, label in zip(polygons, labels):
        distance_to_center = shape_distance(Point(center[0], center[1]), polygon)
        flipped_line = flip_geojson_coordinates(polygon)

        if (distance_to_center or 1e10) < max_distance/4e5:
            folium.GeoJson(
                flipped_line,
                style_function=lambda x: style,
                popup=label,
                tooltip=label
            ).add_to(feature_group)


def add_circle(folium_map, center, radius, label='search-radius'):
    folium.Circle(
        location=center,
        radius=radius,
        color="light-gray",
        opacity=0.5,
        fill=True,
        fill_opacity=0.1,
        fill_color="light-gray",
    ).add_to(folium_map)


def fig_to_base64(fig):
    tmpfile = io.BytesIO()
    fig.savefig(tmpfile, format='png')
    return base64.b64encode(tmpfile.getvalue()).decode('utf-8')
