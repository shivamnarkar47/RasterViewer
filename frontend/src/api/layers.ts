const API_BASE = "http://localhost:8000";

export interface Layer {
  id: string;
  filename: string;
  bounds: {
    left: number;
    bottom: number;
    right: number;
    top: number;
  };
  crs: string;
  width: number;
  height: number;
  bands: number;
}

export async function listLayers(): Promise<Layer[]> {
  const res = await fetch(`${API_BASE}/layers`);
  return res.json();
}

export async function deleteLayer(id: string): Promise<void> {
  await fetch(`${API_BASE}/layers/${id}`, { method: "DELETE" });
}

export async function getTileUrl(layerId: string, z: number, x: number, y: number): string {
  return `${API_BASE}/tiles/${layerId}/${z}/${x}/${y}.png`;
}

export async function getPixelInfo(layerId: string, lat: number, lon: number) {
  const res = await fetch(`${API_BASE}/info/${layerId}?lat=${lat}&lon=${lon}`);
  if (res.status === 204) return null;
  return res.json();
}

export async function initiateUpload(filename: string, totalSize: number): Promise<{ upload_id: string }> {
  const res = await fetch(`${API_BASE}/upload?filename=${encodeURIComponent(filename)}&total_size=${totalSize}`, {
    method: "POST",
  });
  return res.json();
}

export async function uploadChunk(uploadId: string, chunk: Blob, offset: number): Promise<{ complete: boolean }> {
  const res = await fetch(`${API_BASE}/upload/${uploadId}?offset=${offset}`, {
    method: "PATCH",
    body: chunk,
  });
  return res.json();
}