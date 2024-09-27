import os
from snappy import ProductIO, GPF, HashMap
import rasterio
import numpy as np

# Define a helper function to apply a processing operator
def apply_operator(product, operator, parameters):
    GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
    return GPF.createProduct(operator, parameters, product)

# Define a function to read TIFF file and create a snappy product
def read_tiff_as_product(tiff_file_path):
    with rasterio.open(tiff_file_path) as src:
        data = src.read(1)  # Read the first band (VV)
        # Create a snappy product from the TIFF data
        product = ProductIO.createProduct(
            "GRD",  # Type of the product
            data.shape[1],  # Width
            data.shape[0],  # Height
            data,  # Band data
            {"Polarisation": "VV"}  # Metadata
        )
        return product

# Path to the downloaded Sentinel-1 TIFF file
input_file_path = "path_to_your_downloaded_tiff_file.tiff"
output_file_path = "path_to_your_output_file.dim"

# Load the Sentinel-1 product from the TIFF file
s1_product = read_tiff_as_product(input_file_path)

# Step 1: Border Noise Removal
parameters = HashMap()
parameters.put("selectedPolarisations", "VV")
border_noise_removed = apply_operator(s1_product, "Remove-GRD-Border-Noise", parameters)

# Step 2: Thermal Noise Removal
parameters = HashMap()  # No special parameters needed
thermal_noise_removed = apply_operator(border_noise_removed, "ThermalNoiseRemoval", parameters)

# Step 3: Radiometric Calibration (converts to Sigma0)
parameters = HashMap()
parameters.put("outputSigmaBand", True)
parameters.put("sourceBands", "Intensity_VV")  # Ensure the correct band is specified
calibrated_product = apply_operator(thermal_noise_removed, "Calibration", parameters)

# Step 4: Ellipsoid Correction (Range-Doppler Terrain Correction)
parameters = HashMap()
parameters.put("demName", "SRTM 1Sec HGT")  # Use SRTM DEM for terrain correction
parameters.put("pixelSpacingInMeter", 10.0)  # Output pixel spacing
parameters.put("mapProjection", "AUTO:42001")  # Automatic UTM/WGS84 projection
terrain_corrected = apply_operator(calibrated_product, "Terrain-Correction", parameters)

# Step 5: Convert to decibels (dB)
parameters = HashMap()
parameters.put("sourceBands", "Sigma0_VV")  # Band from calibration step
parameters.put("targetBands", "Sigma0_VV_dB")
parameters.put("scale", 10.0)  # Log scaling
converted_to_db = apply_operator(terrain_corrected, "LinearToFromdB", parameters)

# Save the final product
ProductIO.writeProduct(converted_to_db, output_file_path, "BEAM-DIMAP")

print(f"Processing completed. Output saved at {output_file_path}")
