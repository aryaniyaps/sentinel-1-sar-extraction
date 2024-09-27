from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from config import settings

# Connect to the Copernicus Data Space Ecosystem API
api = SentinelAPI(
    settings.sentinel_api_username,
    settings.sentinel_api_password,
    "https://apihub.copernicus.eu/dhus",
)

# Define your area of interest (AOI) in GeoJSON format
# Alternatively, you can point this to a local geojson file
footprint = geojson_to_wkt(read_geojson("path_to_aoi.geojson"))

# Search for Sentinel-1 SAR data (VV polarization, IW mode, GRD products)
products = api.query(
    footprint,
    date=("20230901", "20230930"),  # Date range for the search
    platformname="Sentinel-1",
    producttype="GRD",
    sensoroperationalmode="IW",  # Interferometric Wide (IW) swath mode
    polarisationmode="VV",
    cloudcoverpercentage=(0, 30),  # Only select images with low cloud cover
)

# Print the search results
print(f"Found {len(products)} products.")

# Download the products to a specified directory
download_dir = "./downloads"
for product_id, product_info in products.items():
    print(f"Downloading: {product_info['title']}")
    api.download(product_id, directory_path=download_dir)

print("Download complete.")
