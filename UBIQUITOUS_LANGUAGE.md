# Ubiquitous Language

## Raster & TIFF

| Term | Definition | Aliases to avoid |
| ---- | ----------- | ----------------- |
| **Raster** | A grid of pixel values with geographic coordinates (georeference) | Image, bitmap, grid |
| **TIFF** | Tagged Image File Format - a lossless raster format that can embed georeference metadata | TIF, GeoTIFF |
| **GeoTIFF** | TIFF with embedded coordinate metadata (CRS, transform, bounds) | — |
| **Pixel Value** | The numeric value stored at a single grid cell | DN (digital number), cell value, intensity |
| **NoData** | Pixel values that represent missing or invalid data | null, empty, nodata |
| **Single-band** | Raster with one value per pixel (grayscale) | Grayscale, 1-band |
| **Multi-band** | Raster with multiple values per pixel (e.g., RGB = 3 bands) | RGB, multi-channel |
| **Colormap** | Function that maps pixel values to colors for display | Color ramp, color scale |
| **Palette** | 256-color lookup table applied to single-band rasters | Color table, LUT |
| **Normalization** | Mapping raw pixel values to displayable 0-255 range | Scaling, stretching |

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
- "Visual" was used for both the rendered tile and the color scheme — "visual" is too vague; use **Colormap** or **Palette** for color mapping, **Rendered tile** for the output image.
- "Render" was used to mean both generating tiles and applying color — **VRT** generates raw tiles, **Colormap** applies color for display.

## Example dialogue

> **Dev:** "User uploads a **TIFF** but it shows nothing on the map. Click queries still work."

> **Domain expert:** "The **Rendered tile** is probably all black. What's the **NoData** value?"

> **Dev:** "0. The raster is elevation data with 0 as sea level."

> **Domain expert:** "Ah - the **Normalization** is treating 0 as **NoData**. It should only treat -1 as **NoData** by default. Also, single-band **Raster** needs a **Colormap** to be visible — without it, it's just grayscale."

> **Dev:** "So we need two fixes: fix **Normalization** to not reject 0, and add a **Palette** for single-band rendering?"

> **Domain expert:** "Exactly. The **Click Query** returns raw **Pixel Value** for analysis, while the **Rendered tile** applies **Normalization** and **Palette** for visualization."