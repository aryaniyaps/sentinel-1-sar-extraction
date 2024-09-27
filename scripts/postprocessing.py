from snappy import ProductIO, GPF, HashMap


# Define a helper function to apply a processing operator
def apply_operator(product, operator, parameters):
    GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
    return GPF.createProduct(operator, parameters, product)


# Path to the Sentinel-1 data
input_file_path = "path_to_your_Sentinel1_data.zip"
output_file_path = "path_to_your_output_file.dim"

# Load the Sentinel-1 product
s1_product = ProductIO.readProduct(input_file_path)

# Step 1: Border Noise Removal
parameters = HashMap()
parameters.put("selectedPolarisations", "VV")
border_noise_removed = apply_operator(s1_product, "Remove-GRD-Border-Noise", parameters)

# Step 2: Thermal Noise Removal
parameters = HashMap()  # No special parameters needed
thermal_noise_removed = apply_operator(
    border_noise_removed, "ThermalNoiseRemoval", parameters
)

# Step 3: Radiometric Calibration (converts to Sigma0)
parameters = HashMap()
parameters.put("outputSigmaBand", True)
parameters.put(
    "sourceBands", "Intensity_VV"
)  # Make sure to specify the correct band (VV)
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
