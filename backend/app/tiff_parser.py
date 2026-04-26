import rasterio
from pathlib import Path
from typing import Optional
import uuid

class TIFFParser:
    def parse(self, file_path: Path | str) -> dict:
        with rasterio.open(file_path) as src:
            bounds = src.bounds
            crs = self._get_crs(src.crs)
            transform = src.transform
            width = src.width
            height = src.height
            count = src.count
            nodata = src.nodata
            
            return {
                "id": str(uuid.uuid4()),
                "filename": Path(file_path).name,
                "file_path": str(file_path),
                "bounds": {
                    "left": bounds.left,
                    "bottom": bounds.bottom,
                    "right": bounds.right,
                    "top": bounds.top,
                },
                "crs": crs,
                "transform": list(transform),
                "width": width,
                "height": height,
                "bands": count,
                "nodata": nodata,
            }

    def _get_crs(self, crs) -> str:
        if crs is None:
            return "EPSG:4326"
        try:
            epsg = crs.to_epsg()
            if epsg:
                return f"EPSG:{epsg}"
            return "EPSG:4326"
        except Exception:
            return "EPSG:4326"

    def validate(self, file_path: Path | str) -> bool:
        try:
            with rasterio.open(file_path) as src:
                return src.driver == "GTiff"
        except Exception:
            return False