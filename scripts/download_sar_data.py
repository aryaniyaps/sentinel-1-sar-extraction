import geopandas as gpd
from sentinelhub import (
    CRS,
    BBox,
    DataCollection,
    MimeType,
    MosaickingOrder,
    SentinelHubRequest,
    SHConfig,
    bbox_to_dimensions,
)

from config import settings

# Load your Sentinel Hub credentials
config = SHConfig(
    sh_base_url="https://sh.dataspace.copernicus.eu",
    sh_token_url="https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
    sh_client_id=settings.sentinel_hub_client_id,
    sh_client_secret=settings.sentinel_hub_client_secret.get_secret_value(),
)

# Load the GeoJSON area of interest (AOI)
aoi = gpd.read_file("extraction_areas/mumbai_offshore.geojson")

# Convert the AOI to a bounding box (min_x, min_y, max_x, max_y format)
min_x, min_y, max_x, max_y = aoi.total_bounds
bbox = BBox(bbox=[min_x, min_y, max_x, max_y], crs=CRS.WGS84)  # type:ignore[arg-type]

# Define the size of the bounding box area (in pixels)
bbox_size = bbox_to_dimensions(bbox, resolution=30)  # Adjust resolution as needed

print(f"BBox dimensions: {bbox_size}")

# Create a request for Sentinel-1 SAR data (VV polarization)
request = SentinelHubRequest(
    data_folder="./downloads",  # Set your download directory
    evalscript="""
        //VERSION=3
        function setup() {
          return {
            input: ["VV"],
            output: { bands: 1 }
          };
        }

        function evaluatePixel(sample) {
          return [sample.VV];
        }
    """,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL1_IW.define_from(
                "s1iw", service_url=config.sh_base_url
            ),
            time_interval=("2018-09-01", "2023-09-30"),  # Date range
            mosaicking_order=MosaickingOrder.MOST_RECENT,  # Mosaicking order by most recent images
        )
    ],
    bbox=bbox,
    size=bbox_size,
    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
    config=config,
)

# Execute the request and download the products
data = request.get_data(save_data=True, show_progress=True)
print(f"Downloaded {len(data)} images.")
