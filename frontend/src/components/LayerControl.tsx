import { deleteLayer, type Layer } from "../api/layers";

interface LayerControlProps {
  layers: Layer[];
  selectedLayer: string | null;
  onSelect: (id: string | null) => void;
  opacity: number;
  onOpacityChange: (opacity: number) => void;
  onRefresh: () => void;
}

export function LayerControl({ layers, selectedLayer, onSelect, opacity, onOpacityChange, onRefresh }: LayerControlProps) {
  const handleDelete = async (id: string) => {
    await deleteLayer(id);
    onRefresh();
  };

  return (
    <div className="layer-control">
      <h3>Layers</h3>
      <button className="btn-refresh" onClick={onRefresh}>Refresh</button>
      
      {layers.length === 0 && <p>No layers uploaded</p>}
      
      {layers.map((layer) => (
        <div key={layer.id} className="layer-item">
          <label>
            <input
              type="radio"
              name="layer"
              checked={selectedLayer === layer.id}
              onChange={() => onSelect(layer.id)}
            />
            {layer.filename}
          </label>
          <button className="btn-delete" onClick={() => handleDelete(layer.id)}>Delete</button>
        </div>
      ))}
      
      {selectedLayer && (
        <div className="opacity-control">
          <label>
            <span>Opacity: {opacity.toFixed(1)}</span>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={opacity}
              onChange={(e) => onOpacityChange(Number(e.target.value))}
            />
          </label>
        </div>
      )}
    </div>
  );
}