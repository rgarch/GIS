import ee
import json
from pathlib import Path
import geemap
import numpy as np, math, io, base64
import matplotlib.pyplot as plt
from IPython.display import Image, display
print('Libraries loaded.')

PROJECT_ID="ghy512-506701"

ee.Authenticate()
ee.Initialize(project=PROJECT_ID)
print('Earth Engine connected')

roi = ee.Geometry({
    "type": "Polygon",
    "coordinates": [
        [
            [-90.293488, 31.888447],
            [-90.219557, 31.888447],
            [-90.219557, 31.927618],
            [-90.293488, 31.927618],
            [-90.293488, 31.888447]
        ]
    ]
})

collection = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
              .filterDate('2013-04-01', '2026-10-01')
              .filterBounds(roi)
              .filter(ee.Filter.lt('CLOUD_COVER', 40)))

def mask_clouds(img):
    qa = img.select('QA_PIXEL')
    return img.updateMask(
        qa.bitwiseAnd(1 << 3).eq(0).And(qa.bitwiseAnd(1 << 4).eq(0))
    )

def scale(img):
    return img.addBands(
        img.select('SR_B.').multiply(0.0000275).add(-0.2), overwrite=True
    )

def add_ndvi_nir(img):
    ndvi = img.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
    nir  = img.select('SR_B5').rename('NIR')
    return img.addBands([ndvi, nir])

processed = (collection
             .map(mask_clouds)
             .map(scale)
             .map(add_ndvi_nir)
             .select(['NDVI', 'NIR']))

print("Number of images:", processed.size().getInfo())
print(roi.getInfo())
print("Area (m^2):", roi.area().getInfo())

composite = processed.median().clip(roi)
# NDVI Only
#task_ndvi = ee.batch.Export.image.toDrive(
#    image=composite.select('NDVI'),
#    description='NDVI_only',
#    folder='GEE_Exports',
#    fileNamePrefix='NDVI_median',
#    region=roi,
#    scale=30,
#    maxPixels=1e13
#)
#task_ndvi.start()

# NIR only
#task_nir = ee.batch.Export.image.toDrive(
#    image=composite.select('NIR'),
#    description='NIR_only',
#    folder='GEE_Exports',
#    fileNamePrefix='NIR_median',
#    region=roi,
#    scale=30,
#    maxPixels=1e13
#)
#task_nir.start()
