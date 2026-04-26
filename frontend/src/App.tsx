import { useState, useEffect } from "react";
import { MapView } from "./components/MapView";
import { LayerControl } from "./components/LayerControl";
import { UploadControl } from "./components/UploadControl";
import { InfoPanel } from "./components/InfoPanel";
import { MetadataPanel } from "./components/MetadataPanel";
import { listLayers, getPixelInfo, type Layer } from "./api/layers";
import "./App.css";

function App() {
  const [layers, setLayers] = useState<Layer[]>([]);
  const [selectedLayer, setSelectedLayer] = useState<string | null>(null);
  const [selectedLayerData, setSelectedLayerData] = useState<Layer | null>(null);
  const [opacity, setOpacity] = useState(0.7);
  const [pixelInfo, setPixelInfo] = useState<{ lat: number; lon: number; values: number[] } | null>(null);
  const [showMetadata, setShowMetadata] = useState(false);

  const reload = () => listLayers().then(setLayers);

  useEffect(() => {
    reload();
  }, []);

  useEffect(() => {
    if (layers.length > 0 && !selectedLayer) {
      setSelectedLayer(layers[0].id);
    }
  }, [layers]);

  useEffect(() => {
    if (selectedLayer) {
      const layer = layers.find(l => l.id === selectedLayer);
      setSelectedLayerData(layer || null);
    }
  }, [selectedLayer, layers]);

  const handleMapClick = async (lat: number, lon: number) => {
    if (!selectedLayer) return;
    const info = await getPixelInfo(selectedLayer, lat, lon);
    setPixelInfo(info);
  };

  return (
    <div className="app">
      <MapView layers={layers} selectedLayer={selectedLayer} opacity={opacity} onMapClick={handleMapClick} />
      <LayerControl layers={layers} selectedLayer={selectedLayer} onSelect={setSelectedLayer} opacity={opacity} onOpacityChange={setOpacity} onRefresh={reload} />
      <UploadControl onComplete={reload} />
      <InfoPanel pixelInfo={pixelInfo} onClose={() => setPixelInfo(null)} />
      {selectedLayerData && (
        <button className="metadata-toggle" onClick={() => setShowMetadata(!showMetadata)}>
          {showMetadata ? "Hide Metadata" : "Show Metadata"}
        </button>
      )}
      {showMetadata && <MetadataPanel layer={selectedLayerData} onClose={() => setShowMetadata(false)} />}
    </div>
  );
}

export default App;