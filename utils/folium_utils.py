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
