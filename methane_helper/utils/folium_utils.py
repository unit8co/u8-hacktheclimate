import folium
import ee


def add_ee_layer(self, ee_image_object, vis_params, name):
    map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)

    folium.raster_layers.TileLayer(
        tiles=map_id_dict['tile_fetcher'].url_format,
        attr="Map Data © Google Earth Engine",
        name=name,
        overlay=True,
        control=True
    ).add_to(self)


def add_geo_markers_to_map(folium_map, df, group_name: str, label_col: str, icon: str, color: str, show: bool = False):
    feature_group = folium.map.FeatureGroup(name=group_name, show=show)
    folium_map.add_child(feature_group)
    latitudes = list(df.lat)
    longitudes = list(df.lng)
    labels = list(df[label_col])

    for lat, lng, label in zip(latitudes, longitudes, labels):
        folium.Marker(
            location=[lat, lng],
            popup=label,
            icon=folium.Icon(color=color, icon=icon, prefix='fa')
        ).add_to(feature_group)
