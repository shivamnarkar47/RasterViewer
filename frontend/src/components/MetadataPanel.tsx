import { type Layer } from "../api/layers";

interface MetadataPanelProps {
  layer: Layer | null;
  onClose: () => void;
}

export function MetadataPanel({ layer, onClose }: MetadataPanelProps) {
  if (!layer) return null;

  return (
    <div className="metadata-panel">
      <button className="close-btn" onClick={onClose}>X</button>
      <h3>{layer.filename}</h3>
      <div className="metadata-grid">
        <div className="meta-item"><strong>CRS:</strong> {layer.crs}</div>
        <div className="meta-item"><strong>Size:</strong> {layer.width} x {layer.height} px</div>
        <div className="meta-item"><strong>Bands:</strong> {layer.bands}</div>
        <div className="meta-item"><strong>West:</strong> {layer.bounds.left?.toFixed(4)}</div>
        <div className="meta-item"><strong>East:</strong> {layer.bounds.right?.toFixed(4)}</div>
        <div className="meta-item"><strong>South:</strong> {layer.bounds.bottom?.toFixed(4)}</div>
        <div className="meta-item"><strong>North:</strong> {layer.bounds.top?.toFixed(4)}</div>
      </div>
    </div>
  );
}