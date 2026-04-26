import numpy as np
from rasterio.windows import Window
import rasterio
from pathlib import Path
from typing import Optional
import io
import math


class TileServer:
    def __init__(self):
        self.tile_size = 256

    def get_tile(self, layer: dict, z: int, x: int, y: int) -> Optional[bytes]:
        file_path = layer.get("file_path")
        if not file_path:
            print(f"[DEBUG] get_tile: no file_path")
            return None
        
        bounds = layer["bounds"]
        min_lon, min_lat, max_lon, max_lat = (
            bounds["left"], bounds["bottom"], bounds["right"], bounds["top"]
        )
        
        tile_bounds = self._xyz_to_bounds(z, x, y)
        print(f"[DEBUG] get_tile: z={z} x={x} y={y}, tile_bounds={tile_bounds}, layer_bounds={min_lon},{min_lat},{max_lon},{max_lat}")
        
        # Check y is in valid range
        total_y_tiles = 2 ** (z + 1)  # Latitude spans 180 degrees (-90 to 90), each zoom doubles
        if y < 0 or y >= total_y_tiles:
            print(f"[DEBUG] get_tile: y={y} out of range 0-{total_y_tiles}")
            return None
        
        if not self._bounds_overlap(tile_bounds, (min_lon, min_lat, max_lon, max_lat)):
            print(f"[DEBUG] get_tile: no bounds overlap")
            return None
        
        with rasterio.open(file_path) as src:
            print(f"[DEBUG] get_tile: src bounds={src.bounds}, size={src.width}x{src.height}")
            
            # Read nodata from GeoTIFF metadata
            nodata = src.nodata if hasattr(src, 'nodata') and src.nodata is not None else None
            print(f"[DEBUG] get_tile: nodata={nodata}")
            
            window = self._calc_window(src, tile_bounds)
            print(f"[DEBUG] get_tile: window={window}")
            if window is None:
                print(f"[DEBUG] get_tile: calc_window returned None")
                return None
            
            window = self._calc_window(src, tile_bounds)
            if window is None:
                return None
            
            data = src.read(window=window)
            
            # Apply nodata attribute to data array for _normalize to use
            if nodata is not None:
                data._nodata = nodata
            
            # Handle bands: (bands, height, width) -> (height, width) or (height, width, bands)
            if data.shape[0] == 1:
                data = data[0]  # Single band: (H, W)
            elif data.shape[0] == 2:
                # Two bands: use first band for grayscale, second could be alpha
                data = data[0]
            else:
                # 3+ bands: take first 3 for RGB
                data = data[:3].transpose(1, 2, 0)  # (H, W, 3)
            
            img = self._array_to_image(data)
            if img is None:
                return None
            
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return buf.getvalue()

    def _xyz_to_bounds(self, z: int, x: int, y: int) -> tuple:
        import math
        n = 2 ** z
        
        # Longitude: standard -180 to 180
        lon_min = x / n * 360.0 - 180.0
        lon_max = (x + 1) / n * 360.0 - 180.0
        
        # Latitude: proper Web Mercator (not linear!)
        # y=0 at lat ~85, y=n*2 at lat ~-85
        lat_min_rad = math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n)))
        lat_max_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
        lat_min = math.degrees(lat_min_rad)
        lat_max = math.degrees(lat_max_rad)
        
        return (lon_min, lat_min, lon_max, lat_max)

    def _bounds_overlap(self, a: tuple, b: tuple) -> bool:
        return not (a[2] <= b[0] or a[0] >= b[2] or a[3] <= b[1] or a[1] >= b[3])

    def _calc_window(self, src, tile_bounds: tuple) -> Optional[Window]:
        t_lon, t_lat, t_rlon, t_rlat = tile_bounds
        try:
            row_start, col_start = src.index(t_lon, t_rlat)
            row_end, col_end = src.index(t_rlon, t_lat)
            
            col_start = max(0, min(col_start, col_end))
            col_end = max(0, max(col_start, col_end))
            row_start = max(0, min(row_start, row_end))
            row_end = max(0, max(row_start, row_end))
            
            width = max(1, col_end - col_start)
            height = max(1, row_end - row_start)
            
            if col_start >= src.width or row_start >= src.height:
                return None
                
            return Window(col_start, row_start, width, height)
        except Exception:
            return None

    def _array_to_image(self, arr: np.ndarray):
        from PIL import Image
        print(f"[DEBUG] _array_to_image: dtype={arr.dtype}, shape={arr.shape}, ndim={arr.ndim}")
        
        if arr.dtype != np.uint8:
            arr = self._normalize(arr)
            print(f"[DEBUG] _array_to_image: after normalize dtype={arr.dtype}, shape={arr.shape}")
            
        if arr.ndim == 2:
            # Apply colormap for single-band: viridis-style for visibility
            print(f"[DEBUG] _array_to_image: applying colormap for 2D")
            img = Image.fromarray(arr, mode="L")
            palette = self._get_colormap()
            img.putpalette(palette)
            return img
        elif arr.ndim == 3:
            # arr is now (H, W, bands) after get_tile transposes
            if arr.shape[2] == 3:
                mode = "RGB"
            elif arr.shape[2] == 4:
                mode = "RGBA"
            else:
                print(f"[DEBUG] _array_to_image: unsupported 3D shape")
                return None
            arr = arr.astype(np.uint8)
            return Image.fromarray(arr, mode=mode)
        print(f"[DEBUG] _array_to_image: unsupported ndim {arr.ndim}")
        return None
    
    def _get_colormap(self) -> list:
        # Viridis-inspired colormap (256 colors, index 0-255)
        # Maps low values to dark purple, high values to bright yellow
        palette = []
        for i in range(256):
            t = i / 255.0
            # Viridis approximation
            r = int(68 + t * (255 - 68))
            g = int(1 + t * (230 - 1))
            b = int(83 + t * (33 - 83))
            palette.extend([r, g, b])
        return palette

    def _normalize(self, arr: np.ndarray, nodata: Optional[float] = None) -> np.ndarray:
        arr = arr.astype(np.float64)
        
        # Use explicit nodata, or read from arr nodata attribute, or default to -1
        if nodata is None:
            nodata = getattr(arr, 'nodata', None)
        if nodata is None:
            nodata = -1
        
        valid_mask = arr != nodata
        
        if not np.any(valid_mask):
            return np.zeros_like(arr, dtype=np.uint8)
        
        valid_vals = arr[valid_mask]
        min_val = valid_vals.min()
        max_val = valid_vals.max()
        
        if max_val > min_val:
            result = ((arr - min_val) / (max_val - min_val) * 255).astype(np.uint8)
            result[~valid_mask] = 0
        else:
            result = np.zeros_like(arr, dtype=np.uint8)
        
        return result

    def get_pixel_value(self, layer: dict, lat: float, lon: float) -> Optional[dict]:
        file_path = layer.get("file_path")
        if not file_path:
            return None
        
        bounds = layer["bounds"]
        if not (bounds["left"] <= lon <= bounds["right"] and bounds["bottom"] <= lat <= bounds["top"]):
            return None
        
        with rasterio.open(file_path) as src:
            row, col = src.index(lon, lat)
            if row < 0 or col < 0 or row >= src.height or col >= src.width:
                return None
            
            data = src.read(window=Window(col, row, 1, 1))
            values = data.flatten().tolist()
            
            return {
                "lat": lat,
                "lon": lon,
                "values": values,
                "pixel_row": int(row),
                "pixel_col": int(col),
            }