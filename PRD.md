# PRD: RasterViewer - GIS TIFF Viewer

## Problem Statement

Users need a web-based tool to upload, view, and analyze large TIFF raster files on interactive maps. Current solutions require desktop GIS software (QGIS, ArcGIS) which is inaccessible to non-technical users and doesn't handle large files (2GB+) well in browser-only solutions.

## Solution

A React-based web application with a Python backend that allows users to upload TIFF files (any size), view them overlaid on multiple map providers (MapTiler, MapLibre, Leaflet), and perform basic GIS analysis including coordinate alignment and pixel value inspection.

## User Stories

### Upload & Storage
1. As a user, I want to upload TIFF files via chunked upload, so that I can handle files larger than 2GB without timeout
2. As a user, I want to see upload progress with percentage and speed, so that I know the upload is progressing
3. As a user, I want to resume failed uploads, so that I don't lose progress on flaky connections
4. As a user, I want to upload multiple TIFF files, so that I can compare different raster layers
5. As a user, I want to delete uploaded files, so that I can manage storage

### Map Display
6. As a user, I want to view my TIFF overlay on MapTiler map, so that I can see the raster in geographic context
7. As a user, I want to switch between map providers (MapTiler, MapLibre, Leaflet), so that I can compare rendering quality
8. As a user, I want to toggle the TIFF layer on/off, so that I can see the base map underneath
9. As a user, I want to adjust layer opacity, so that I can see the map and raster simultaneously
10. As a user, I want to zoom/pan the map, so that I can explore different areas of the raster
11. As a user, I want to see the raster bounds highlighted, so that I know the coverage area

### Coordinate System
12. As a user, I want the TIFF to automatically align to the correct geographic location, so that I don't have to manually georeference
13. As a user, I want to manually select the CRS if auto-detection fails, so that I can correct misaligned layers
14. As a user, I want the map to display coordinates on mouse hover, so that I can correlate positions

### Analysis
15. As a user, I want to click on the map to get pixel value at that location, so that I can inspect raster values
16. As a user, I want to see the coordinate (lat/lon) of my click, so that I can record locations

### Performance
17. As a user, I want large TIFFs to render as tiles, so that the map remains responsive
18. As a user, I want the map to load tiles incrementally, so that I can start viewing before all tiles load

## Implementation Decisions

### Architecture
- **Frontend**: Vite + React with TypeScript
- **Backend**: Python + FastAPI + rasterio/GDAL
- **Communication**: REST API with tile XYZ endpoints + info endpoint

### Modules

#### Backend Modules
1. **TIFF Parser** - validates TIFF, extracts metadata (bounds, CRS, dimensions, transform), stores file info
2. **Tile Server** - on-demand VRT tile generation from source TIFF, serves XYZ PNG tiles
3. **Upload Handler** - chunked file upload with resumability, progress tracking
4. **Layer Manager** - CRUD operations for uploaded layers, stores metadata in SQLite/JSON
5. **CRS Handler** - auto-detect CRS from GeoTIFF tags, reprojection to WGS84

#### Frontend Modules
1. **MapView** - wrapper around map provider, handles layer overlay and tile fetching
2. **LayerControl** - UI for layer management (toggle, opacity, delete)
3. **UploadControl** - chunked upload UI with progress, chunking logic
4. **InfoPanel** - displays layer metadata and click-value queries

### API Contracts
- `POST /upload` - initiate chunked upload, returns upload ID
- `PATCH /upload/{id}` - upload chunk with range header
- `GET /layers` - list all layers
- `GET /layers/{id}` - get layer metadata
- `DELETE /layers/{id}` - delete layer
- `GET /tiles/{layer_id}/{z}/{x}/{y}.png` - tile endpoint
- `GET /info/{layer_id}?lat=&lon=` - pixel value at coordinate

### Map Provider Configuration
- **MapTiler** - default, vector tiles, requires API key in env
- **MapLibre** - secondary, needs external tile source (OSM, Stadia)
- **Leaflet** - fallback, simpler, can swap tile providers easily

### CRS Handling
- Try to read EPSG code from TIFF tags (GeoTIFF)
- Fallback to EPSG:4326 (WGS84) if not found
- UI dropdown for manual CRS override

## Testing Decisions

### Module Test Strategy
- **TIFF Parser** - test with valid TIFF, corrupt TIFF, non-Geotiff, various CRS codes
- **Tile Server** - test tile XYZ math, out-of-bounds handling, cached vs fresh
- **Upload Handler** - test chunking, resume, duplicate detection

### Good Test Characteristics
- Test external behavior only (API contracts, file I/O)
- Mock GDAL/rasterio for unit tests
- Use sample small TIFFs for integration tests

### Priority Modules for Tests
1. TIFF Parser - validation and metadata extraction (most critical)
2. Tile Server - tile math correctness
3. API endpoints - contract compliance

## Out of Scope

- Pre-tiling during upload (on-demand VRT only for v1)
- User authentication/authorization
- Layer sharing/collaboration
- Export functionality (subset, format conversion)
- Vector overlay support
- Measurement tools (distance, area)
- Mobile responsiveness
- TIFF compression (store as-is)

## Further Notes

- Default to MapTiler for simplest DX
- Add MapLibre/Leaflet as provider swap (can extend later)
- Use SQLite or simple JSON for metadata storage
- Consider adding optional pre-tiling for frequently-accessed layers in v2
