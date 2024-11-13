from geopandas import GeoDataFrame
import plotly.express as px
from shapely.geometry import Point

geometry = [Point(xy) for xy in zip(cities['Longitude'], cities['Latitude'])]
gdf = GeoDataFrame(cities, geometry = geometry)
fig1 = px.scatter_mapbox(cities, lat="Latitude", lon="Longitude", hover_name="City",  zoom=3, height=600, size_max=8)
fig1.update_layout(mapbox_style="carto-positron")
fig1.show()