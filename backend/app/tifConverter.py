import rasterio
from rasterio.transform import from_bounds
from pathlib import Path
import re


def convert_to_geotiff(input_path: Path | str, filename: str) -> str:
    filename = str(filename)
    
    with rasterio.open(input_path) as src:
        data = src.read()
        width = src.width
        height = src.height
        orig_crs = src.crs
        orig_bounds = src.bounds
    
    if orig_crs and orig_bounds.left >= -180 and orig_bounds.right <= 180:
        output_path = str(input_path)
        return output_path
    
    bounds = _guess_bounds_from_filename(filename, width, height)
    if not bounds:
        bounds = (-180, -90, 180, 90)
    
    transform = from_bounds(*bounds, width, height)
    
    output_path = str(input_path).replace('.tif', '_geotiff.tif')
    if '_geotiff_geotiff.tif' in output_path:
        output_path = output_path.replace('_geotiff_geotiff.tif', '_geotiff.tif')
    
    with rasterio.open(
        output_path, 'w',
        driver='GTiff',
        height=height,
        width=width,
        count=data.shape[0] if len(data.shape) > 2 else 1,
        dtype=data.dtype,
        crs='EPSG:4326',
        transform=transform
    ) as dst:
        if len(data.shape) > 2:
            for i in range(data.shape[0]):
                dst.write(data[i], i + 1)
        else:
            dst.write(data)
    
    return output_path


def _guess_bounds_from_filename(filename: str, width: int, height: int) -> tuple:
    name = Path(filename).stem.lower()
    
    locations = {
        "kandivali": (72.85, 19.05, 73.02, 19.22),
        "mumbai": (72.77, 18.89, 73.26, 19.27),
        "delhi": (76.80, 28.40, 77.42, 28.89),
        "bangalore": (77.46, 12.83, 77.80, 13.14),
        "bangaluru": (77.46, 12.83, 77.80, 13.14),
        "chennai": (80.18, 12.95, 80.48, 13.14),
        "kolkata": (88.26, 22.48, 88.42, 22.65),
        "calcutta": (88.26, 22.48, 88.42, 22.65),
        "hyderabad": (78.40, 17.25, 78.60, 17.45),
        "pune": (73.77, 18.45, 74.00, 18.65),
        "ahmedabad": (72.50, 22.99, 72.65, 23.08),
        "jaipur": (75.72, 26.82, 75.92, 27.02),
        "surat": (72.83, 21.15, 72.99, 21.25),
        "lucknow": (80.91, 26.84, 81.05, 27.00),
        "karachi": (66.90, 24.81, 67.30, 25.01),
        "london": (-0.51, 51.28, 0.34, 51.70),
        "new york": (-74.26, 40.48, -73.70, 40.93),
        "paris": (2.22, 48.81, 2.46, 48.90),
        "tokyo": (139.57, 35.54, 139.91, 35.82),
        "sydney": (150.52, -33.95, 151.37, -33.74),
        "dubai": (54.98, 24.98, 55.37, 25.37),
        "singapore": (103.64, 1.27, 104.00, 1.46),
        "san francisco": (-122.52, 37.70, -122.35, 37.83),
        "los angeles": (-118.67, 33.70, -118.15, 34.34),
        "ajmer": (74.63, 26.48, 74.68, 26.53),
        "udaipur": (73.68, 24.52, 73.73, 24.57),
        "jodhpur": (72.92, 26.15, 72.98, 26.20),
        "gwalior": (78.16, 26.16, 78.22, 26.20),
        "indore": (75.75, 22.70, 75.85, 22.80),
        "ajay": (86.25, 23.45, 88.25, 24.61),
        "bali": (115.0, -8.5, 115.5, -8.0),
    }
    
    name_clean = re.sub(r'[-_\s]', '', name)
    
    for loc, b in locations.items():
        loc_clean = re.sub(r'[-_\s]', '', loc)
        if loc_clean in name_clean:
            return b
    
    return None