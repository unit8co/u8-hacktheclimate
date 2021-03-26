import ee
import pandas as pd

from methane_helper.utils.folium_utils import fig_to_base64


def ee_array_to_df(arr, list_of_bands):
    """Transforms client-side ee.Image.getRegion array to pandas.DataFrame."""
    df = pd.DataFrame(arr)

    # Rearrange the header.
    headers = df.iloc[0]
    df = pd.DataFrame(df.values[1:], columns=headers)

    # Remove rows without data inside.
    df = df[['longitude', 'latitude', 'time', *list_of_bands]].dropna()

    # Convert the data to numeric values.
    for band in list_of_bands:
        df[band] = pd.to_numeric(df[band], errors='coerce')

    # Convert the time field into a datetime.
    df['datetime'] = pd.to_datetime(df['time'], unit='ms')

    # Keep the columns of interest.
    df = df[['time', 'datetime', *list_of_bands]]

    return df


def get_image_collection(source, field, from_date, to_date):
    collection = ee.ImageCollection(source)
    image = collection.select(field)

    return image.filterDate(from_date, to_date)


def get_region_image(image, longitude, latitude, point_buffer=1e10):
    point = ee.Geometry.Point(longitude, latitude)
    buffer_square = point.buffer(ee.Number(point_buffer).sqrt().divide(2), 1).bounds()
    return image.getRegion(buffer_square, point_buffer)


def get_methane_ts_from_polygon(polygon, start_date, end_date):
    roi = ee.Geometry.Polygon(polygon.geometry.coordinates)
    im_coll = (ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_CH4')
               .filterBounds(roi)
               .filterDate(ee.Date(start_date), ee.Date(end_date))
               .map(lambda img: img.set('date', ee.Date(img.date()).format('YYYYMMdd')))
               .sort('date'))
    region_im = im_coll.getRegion(roi, 2000).getInfo()

    df_mth = ee_array_to_df(region_im, ['CH4_column_volume_mixing_ratio_dry_air'])
    df_mth = df_mth.set_index('datetime')

    return df_mth.rename(columns={'CH4_column_volume_mixing_ratio_dry_air': 'methane_level'})
