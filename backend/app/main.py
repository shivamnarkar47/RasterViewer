from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Path as PathParam, Query, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from contextlib import asynccontextmanager
import uuid
import json
from typing import Optional

from app.tiff_parser import TIFFParser
from app.tile_server import TileServer
from app.upload_handler import UploadHandler
from app.layer_manager import LayerManager

LAYERS_DIR = Path(__file__).parent / "uploads"
LAYERS_DIR.mkdir(exist_ok=True)

app = FastAPI(title="RasterViewer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

layer_manager: LayerManager = None

@app.on_event("startup")
async def startup():
    global layer_manager
    layer_manager = LayerManager(LAYERS_DIR)

tiff_parser = TIFFParser()
tile_server = TileServer()
upload_handler = UploadHandler(LAYERS_DIR)


@app.post("/upload")
async def initiate_upload(filename: str, total_size: int):
    upload_id = upload_handler.initiate(filename, total_size)
    return {"upload_id": upload_id}


@app.patch("/upload/{upload_id}")
async def upload_chunk(upload_id: str, request: Request, offset: int = Query(0)):
    content = await request.body()
    if not content:
        raise HTTPException(400, "No content provided")
    result = upload_handler.upload_chunk(upload_id, content, offset)
    if result.get("complete"):
        from app.tifConverter import convert_to_geotiff
        file_path = result["file_path"]
        filename = upload_handler.get_filename(upload_id)
        converted = convert_to_geotiff(file_path, filename)
        layer = tiff_parser.parse(converted)
        layer["file_path"] = converted
        layer_manager.add(layer)
    return result


@app.get("/layers")
async def list_layers():
    return layer_manager.list()


@app.get("/layers/{layer_id}")
async def get_layer(layer_id: str):
    return layer_manager.get(layer_id)


@app.delete("/layers/{layer_id}")
async def delete_layer(layer_id: str):
    return layer_manager.delete(layer_id)


@app.get("/tiles/{layer_id}/{z}/{x}/{y}.png")
async def get_tile(layer_id: str, z: int, x: int, y: int):
    layer = layer_manager.get(layer_id)
    if not layer:
        raise HTTPException(404, "Layer not found")
    tile = tile_server.get_tile(layer, z, x, y)
    if tile is None:
        return Response(status_code=204)
    return Response(content=tile, media_type="image/png")


@app.get("/info/{layer_id}")
async def get_pixel_info(layer_id: str, lat: float = Query(), lon: float = Query()):
    layer = layer_manager.get(layer_id)
    if not layer:
        raise HTTPException(404, "Layer not found")
    info = tile_server.get_pixel_value(layer, lat, lon)
    if info is None:
        raise HTTPException(204, "Outside bounds")
    return info