import pandas as pd
import numpy as np
import geopandas as gpd


RENAME = {
    "latitude": 'lat',
    "longitude": 'lng',
    'project': 'name',
    'plant:source': 'plant_source'
}


def load_coal_mines():
    dataset = pd.read_csv('./datasets/coal-mine-infrastructure-dataset.csv').assign(asset_type="coal_mine")
    return dataset.rename(columns=RENAME)


def load_fossil_pipelines():
    dataset = pd.read_csv('./datasets/fossil-pipelines-infrastructure-dataset.csv').assign(asset_type="fossil")
    return dataset.rename(columns=RENAME)


def load_steel_plants():
    dataset = pd.read_csv('./datasets/steel-plant-infrastructure-dataset.csv').assign(asset_type="steel-plant")
    return dataset.rename(columns=RENAME)


def load_power_plants():
    """
    source: https://wiki.openstreetmap.org/wiki/Tag:power%3Dplant

    Plant sources available:
        ['hydro', 'waste', 'gas', nan, 'wind', 'oil', 'coal', 'biofuel',
       'solar;diesel', 'solar', 'oil;gas', 'biomass;oil', 'biomass',
       'gas;oil', 'biogas', 'nuclear', 'battery',
       'abandoned_mine_methane;oil'

    """
    DIRTY_POWER_PLANTS = ['gas', 'oil', 'coal', 'oil;gas',
                          'gas;oil', 'biogas', 'abandoned_mine_methane;oil']

    dataset = pd.read_csv('./datasets/power-plant-infrastructure-dataset.csv')

    dataset = (dataset
               .rename(columns=RENAME)
               .dropna(axis=1, how="all")
               .rename(columns={'plant:source': 'plant_source'})
               .assign(asset_type="power_plant")
               .query("plant_source in @DIRTY_POWER_PLANTS")
               #  matches coal mine dataset
               .assign(type=lambda s: np.where(s.underground == 'yes', 'underground', "surface"))
               )

    return dataset


def pipelines_as_gdf():
    """
    Return pipelines as geodataframes
    """
    from shapely import wkt

    def wkt_loads(x):
        try:
            return wkt.loads(x)
        except Exception:
            return None

    df_fossil_pipelines = load_fossil_pipelines().query("route==route")

    #  Manual transform to line string:
    #  Input 43.5995, 16.3946: 43.6098, 16.5395:
    #  Output: LINESTRING (30 10, 10 30, 40 40)
    df_fossil_pipelines['route'] = 'LINESTRING (' + \
                                   df_fossil_pipelines['route'].str.replace(',', ' ').str.replace(';', ' ').str.replace(':', ',') + \
                                   ')'

    df_fossil_pipelines['route'] = df_fossil_pipelines['route'].apply(wkt_loads)

    return gpd.GeoDataFrame(df_fossil_pipelines, geometry=df_fossil_pipelines['route'])


def plants_as_gdf():
    """
    Return coal mines an power plant as geopandas dataframe
    """
    COLUMNS_TO_KEEP = [
        "name", "lat", "lng", "owner", "status", "operator",
        "country", "region", "url", "asset_type"
    ]
    # Keep only points
    df_coal_mines = load_coal_mines()[COLUMNS_TO_KEEP]
    df_plants = (
        load_power_plants()
            .assign(country="")
            .assign(region="")
            .assign(owner="")
            .assign(status=lambda s: np.where(s.proposed, "proposed", "operating"))
            .assign(url=lambda s: s.wikipedia)
        [COLUMNS_TO_KEEP]
    )

    df_merged = pd.concat([df_plants, df_coal_mines])

    return gpd.GeoDataFrame(
        df_merged, geometry=gpd.points_from_xy(df_merged.lng, df_merged.lat)
    )
