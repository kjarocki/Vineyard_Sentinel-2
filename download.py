from sentinelsat import SentinelAPI
import geopandas as gpd
import folium 
from shapely.geometry import MultiPolygon, Polygon


user = 'kjarocki' 
password = 'D*******3' 
try:
    api = SentinelAPI(user, password, 'https://scihub.copernicus.eu/dhus')
    print('Connected')
except:
    print('Connection failed')
nReserve = gpd.read_file('/Volumes/Konrad Jarocki/Konrad/Samplers/Italy_WGS84.shp')

for i in nReserve['geometry']:
    footprint = i
print(footprint)
products = api.query(footprint, date = ('20200601', '20201001'), platformname = 'Sentinel-2', processinglevel = 'Level-2A')
print(len(products))
api.download_all(products)