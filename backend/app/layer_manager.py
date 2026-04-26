import json
from pathlib import Path
from typing import Optional


class LayerManager:
    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.metadata_file = storage_dir / "layers.json"
        self._load_layers()

    def _load_layers(self):
        if self.metadata_file.exists():
            with open(self.metadata_file) as f:
                self.layers = json.load(f)
        else:
            self.layers = {}

    def _save_layers(self):
        with open(self.metadata_file, "w") as f:
            json.dump(self.layers, f)

    def add(self, layer: dict) -> str:
        layer_id = layer["id"]
        self.layers[layer_id] = layer
        self._save_layers()
        return layer_id

    def get(self, layer_id: str) -> Optional[dict]:
        return self.layers.get(layer_id)

    def list(self) -> list:
        return list(self.layers.values())

    def delete(self, layer_id: str) -> bool:
        if layer_id in self.layers:
            layer = self.layers[layer_id]
            file_path = layer.get("file_path")
            if file_path and Path(file_path).exists():
                Path(file_path).unlink()
            del self.layers[layer_id]
            self._save_layers()
            return True
        return False