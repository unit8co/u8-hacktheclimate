import numpy as np
import geopandas
import shapely
import matplotlib.pyplot as plt


def pandas_to_geopandas(df):
    return geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df.longitude, df.latitude))


def grid_over_df(gdf):
    xmin, ymin, xmax, ymax = gdf.total_bounds
    print(gdf.total_bounds)
    # how many cells across and down
    n_cells = 30
    cell_size = (xmax - xmin) / n_cells
    print(xmin, xmax + cell_size, cell_size)
    # projection of the grid
    crs = "+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs"
    # create the cells in a loop
    grid_cells = []
    for x0 in np.arange(xmin, xmax + cell_size, cell_size):
        for y0 in np.arange(ymin, ymax + cell_size, cell_size):
            # bounds
            x1 = x0 - cell_size
            y1 = y0 + cell_size
            grid_cells.append(shapely.geometry.box(x0, y0, x1, y1))
    cell = geopandas.GeoDataFrame(grid_cells, columns=['geometry'],
                                  crs=crs)

    ax = gdf.plot(markersize=.1, figsize=(12, 8), column='dob', cmap='jet')
    plt.autoscale(False)
    cell.plot(ax=ax, facecolor="none", edgecolor='grey')
    ax.axis("off")

    return cell