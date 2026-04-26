interface PixelInfo {
  lat?: number;
  lon?: number;
  values?: number[];
}

interface InfoPanelProps {
  pixelInfo: PixelInfo | null;
  onClose: () => void;
}

export function InfoPanel({ pixelInfo, onClose }: InfoPanelProps) {
  if (!pixelInfo) return null;

  return (
    <div className="info-panel">
      <button className="close-btn" onClick={onClose}>X</button>
      <h3>Pixel Info</h3>
      <p><strong>Lat:</strong> {pixelInfo.lat?.toFixed(6) ?? "N/A"}</p>
      <p><strong>Lon:</strong> {pixelInfo.lon?.toFixed(6) ?? "N/A"}</p>
      <p><strong>Values:</strong> {pixelInfo.values?.join(", ") ?? "N/A"}</p>
    </div>
  );
}