import { useState, useRef } from "react";
import { initiateUpload, uploadChunk } from "../api/layers";

interface UploadControlProps {
  onComplete: () => void;
}

const CHUNK_SIZE = 5 * 1024 * 1024;

export function UploadControl({ onComplete }: UploadControlProps) {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [speed, setSpeed] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    setUploading(true);
    setError(null);
    try {
      const { upload_id } = await initiateUpload(file.name, file.size);
      let offset = 0;
      const start = Date.now();
      while (offset < file.size) {
        const chunk = file.slice(offset, offset + CHUNK_SIZE);
        await uploadChunk(upload_id, chunk, offset);
        const now = Date.now();
        const elapsed = (now - start) / 1000;
        if (elapsed > 0) setSpeed(offset / elapsed / 1024 / 1024);
        offset += CHUNK_SIZE;
        setProgress(Math.min((offset / file.size) * 100, 100));
      }
      onComplete();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  return (
    <div className="upload-control">
      <input
        ref={fileRef}
        type="file"
        accept=".tif,.tiff,image/tiff"
        onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
        disabled={uploading}
      />
      {uploading && (
        <div className="progress">
          <progress value={progress} max={100} />
          <span>{progress.toFixed(1)}% ({speed.toFixed(1)} MB/s)</span>
        </div>
      )}
      {error && <p className="error">{error}</p>}
      <p className="hint">Auto-converts to GeoTIFF with geographic bounds</p>
    </div>
  );
}