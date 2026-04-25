# Ubiquitous Language

## Raster & TIFF

| Term | Definition | Aliases to avoid |
| ---- | ----------- | ----------------- |
| **Raster** | A grid of pixel values with geographic坐标 (georeference) | Image, bitmap, grid |
| **TIFF** | Tagged Image File Format - a lossless raster format that can embed georeference metadata | TIF, GeoTIFF |
| **GeoTIFF** | TIFF with embedded coordinate metadata (CRS, transform, bounds) | — |
| **Pixel Value** | The numeric value stored at a single grid cell | DN (digital number), cell value, intensity |
| **NoData** | Pixel values that represent missing or invalid data | null, empty, nodata |

## Coordinate Systems

| Term | Definition | Aliases to avoid |
| ---- | ----------- | ----------------- |
| **CRS** | Coordinate Reference System - defines how to map lat/lon to earth coordinates | Coordinate system, spatial reference, SRS |
| **WGS84** | EPSG:4326 - the standard lat/lon coordinate system used by GPS and web maps | EPSG:4326, geographic |
| **Bounds** | Bounding box - min/max x and y coordinates defining raster coverage | bbox, extent, envelope |
| **Transform** | Mathematical parameters that map pixel coordinates to geographic coordinates | geotransform, affine transform |

## Map Layers

| Term | Definition | Aliases to avoid |
| ---- | ----------- | ----------------- |
| **Layer** | A single raster uploaded by user, displayed on map | Raster, overlay, coverage |
| **Map Provider** | Service providing base map tiles (MapTiler, MapLibre, Leaflet) | Map service, tile provider, basemap |
| **Tile Source** | URL endpoint that serves map tiles | Tile server, XYZ source |
| **XYZ Tiles** | Standard tile addressing scheme: zoom (z), column (x), row (y) | Slippy tiles, web mercator tiles |
| **VRT** | Virtual Raster Table - on-demand tile generation from source raster | Virtual raster, dynamic tiles |

## Upload

| Term | Definition | Aliases to avoid |
| ---- | ----------- | ----------------- |
| **Chunked Upload** | File upload split into smaller pieces for large files (>50MB) | Resumable upload, multipart upload |
| **Upload ID** | Unique identifier for an in-progress upload session | Session ID, upload token |
| **Progress** | Percentage and bytes transferred during upload | — |

## Analysis

| Term | Definition | Aliases to avoid |
| ---- | ----------- | ----------------- |
| **Click Query** | User clicks map to retrieve pixel value at that location | Point query, value lookup, identify |
| **Coordinate Display** | Shows lat/lon of mouse position | Mouse coordinates, cursor position |

## Relationships

- A **Layer** (TIFF) has exactly one **CRS** embedded in metadata
- A **Layer** has one **Bounds** computed from the transform
- **XYZ Tiles** are generated on-demand from a **Layer** via **VRT**
- **Map Provider** serves **Tile Source** to render base map

## Flagged ambiguities

- "Tile" was used to mean both map tiles (Map Provider concept) and raster tiles (TIFF rendered as XYZ) — these are distinct: base map tiles come from the **Map Provider**, while raster overlay tiles come from the **VRT** endpoint.
- "Image" was used loosely for both the raw TIFF file and the rendered overlay — the **Raster** is the domain concept; "image" is a rendering view.
- "Overlay" and "layer" used interchangeably — **Layer** is the canonical term for a user's uploaded TIFF.

## Example dialogue

> **Dev:** "When a user uploads a **TIFF**, how do we determine where it goes on the map?"

> **Domain expert:** "We read the **GeoTIFF** metadata to extract the **transform** and **CRS**. The **transform** gives us pixel-to-coordinate mapping, which lets us compute the **Bounds**."

> **Dev:** "What if the TIFF has no CRS embedded?"

> **Domain expert:** "Then we **fallback** to **WGS84** (EPSG:4326) as the default **CRS**, and show a warning in the UI. The user can override via the **CRS dropdown**."

> **Dev:** "And the **Click Query** returns the **pixel value** at the clicked location?"

> **Domain expert:** "Yes. We convert the clicked lat/lon to pixel coordinates using the **transform**, sample the value, and return it along with coordinates. If the click is outside the **Bounds** or is **NoData**, we return null."