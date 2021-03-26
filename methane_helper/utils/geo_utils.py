import geopandas
import numpy as np
from geopy import distance
from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry
import geojson
from shapely.ops import transform


def get_feature_center(feature):
    s = json_to_shape(feature)
    center = s.centroid
    return [center.y, center.x]


def json_to_shape(feature):
    return shape(feature["geometry"])


def pandas_to_geopandas(df):
    return geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df.longitude, df.latitude))


def point_distance(p1, p2):
    coords_1 = (p1[0], p1[1])
    coords_2 = (p2[0], p2[1])

    return distance.distance(coords_1, coords_2).m


def shape_distance(shape1: BaseGeometry, shape2: BaseGeometry):
    if shape1 is not None and shape2 is not None:
        return shape1.distance(shape2)

    return None


def str_to_geoson(json_str: str):
    return geojson.loads(json_str)


def flip(x, y):
    """Flips the x and y coordinate values"""
    return y, x


def flip_geojson_coordinates(geo):
    return transform(flip, geo)
