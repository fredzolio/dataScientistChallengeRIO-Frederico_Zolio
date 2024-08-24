import plotly.graph_objs as go
from shapely import Polygon, wkt
import geopandas as gpd

def get_map_center(gdf):
    center_lat = gdf.geometry.centroid.y.mean()
    center_lon = gdf.geometry.centroid.x.mean()
    return center_lat, center_lon
    
def convert_wkt_to_gdf(df):
    df['geometry'] = df['geometry_wkt'].apply(wkt.loads)
    return gpd.GeoDataFrame(df, geometry='geometry')
