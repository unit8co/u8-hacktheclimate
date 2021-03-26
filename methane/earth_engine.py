"""
Earth Engine loading utils
------------------------------

Function to load and export from earth engine
"""
from pathlib import Path

import ee
import pandas as pd


def authenticate_google_service_account(
        json_path: Path,
        service_account: str = 'hacktheclimate-sa@hacktheclimate-308416.iam.gserviceaccount.com',
) -> None:
    credentials = ee.ServiceAccountCredentials(service_account, str(json_path))
    ee.Initialize(credentials)


def load_collection(collection):
    """
    Load collection from Earth Engine

    :param collection: String.
    :return: ee.ImageCollection
    """
    if collection in ('MODIS/006/MCD12Q1', 'MODIS/006/MOD11A1','COPERNICUS/S5P/OFFL/L3_CH4'):
        return ee.ImageCollection(collection)
    elif collection in ('USGS/SRTMGL1_003'):
        return ee.Image(collection)
    else:
        raise ValueError('Unknown collection')


def ee_array_to_df(arr, list_of_bands):
    """Transforms client-side ee.Image.getRegion array to pandas.DataFrame.
    
    :param arr: ee.Array
    :list_of_bands: List[str]
    :return: pd.DataFrame
    """
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
    df = df[['time','datetime',  *list_of_bands]]

    return df


def load_methane_data(start_date, end_date):
    """
    Load collection from Earth Engine

    :param start_date: Initial date of interest (str: 'YYYY-MM-dd')
    :param start_date: inal date of interest (str: 'YYYY-MM-dd')
    :return: ee.ImageCollection
    """
    methane_collection_name = 'COPERNICUS/S5P/OFFL/L3_CH4'
    methane_image_collection = load_collection(methane_collection_name)

    # Selection of appropriate bands and dates for LST.
    methane_image_collection = methane_image_collection.filterDate(start_date, end_date)

    return methane_image_collection


