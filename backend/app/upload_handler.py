import uuid
import json
from pathlib import Path
from typing import Optional
import re


class UploadHandler:
    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.temp_dir = storage_dir / "temp"
        self.temp_dir.mkdir(exist_ok=True)
        self.metadata_file = storage_dir / "uploads.json"
        self._load_metadata()

    def _load_metadata(self):
        if self.metadata_file.exists():
            with open(self.metadata_file) as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}

    def _save_metadata(self):
        with open(self.metadata_file, "w") as f:
            json.dump(self.metadata, f)

    def get_filename(self, upload_id: str) -> str:
        return self.metadata.get(upload_id, {}).get("filename", "")

    def get_bounds(self, upload_id: str):
        filename = self.get_filename(upload_id)
        m = re.search(r'bounds=([^&]+)', filename)
        if m:
            parts = m.group(1).split(',')
            if len(parts) == 4:
                return float(parts[0]), float(parts[1]), float(parts[2]), float(parts[3])
        return None

    def initiate(self, filename: str, total_size: int) -> str:
        upload_id = str(uuid.uuid4())
        clean_filename = re.sub(r'\?bounds=.*', '', filename)
        self.metadata[upload_id] = {
            "filename": clean_filename,
            "total_size": total_size,
            "uploaded_size": 0,
            "file_path": str(self.temp_dir / f"{upload_id}.tif"),
            "chunks": [],
        }
        self._save_metadata()
        return upload_id

    def upload_chunk(self, upload_id: str, content: bytes, offset: int) -> dict:
        meta = self.metadata.get(upload_id)
        if not meta:
            raise ValueError(f"Upload {upload_id} not found")
        
        file_path = Path(meta["file_path"])
        
        with open(file_path, "ab") as f:
            f.seek(offset)
            f.write(content)
        
        meta["uploaded_size"] += len(content)
        meta["chunks"].append({"offset": offset, "size": len(content)})
        self._save_metadata()
        
        complete = meta["uploaded_size"] >= meta["total_size"]
        if complete:
            final_path = self.storage_dir / meta["filename"]
            file_path.rename(final_path)
            meta["file_path"] = str(final_path)
            del meta["chunks"]
            self._save_metadata()
        
        return {
            "offset": offset,
            "uploaded_size": meta["uploaded_size"],
            "complete": complete,
            "file_path": meta.get("file_path") or file_path,
        }