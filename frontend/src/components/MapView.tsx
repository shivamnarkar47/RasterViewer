import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { type Layer } from "../api/layers";

const API_BASE = "http://localhost:8000";

interface MapViewProps {
  layers: Layer[];
  selectedLayer: string | null;
  opacity: number;
  onMapClick: (lat: number, lon: number) => void;
}

export function MapView({ layers, selectedLayer, opacity, onMapClick }: MapViewProps) {
  const mapRef = useRef<L.Map | null>(null);
  const layersRef = useRef<Map<string, L.TileLayer>>(new Map());
  const onMapClickRef = useRef(onMapClick);
  const initializedRef = useRef(false);

  useEffect(() => {
    onMapClickRef.current = onMapClick;
  }, [onMapClick]);

  useEffect(() => {
    if (mapRef.current) return;
    const map = L.map("map", { zoomControl: true }).setView([24, 87], 9);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: "&copy; OpenStreetMap",
    }).addTo(map);
    map.on("click", (e) => onMapClickRef.current(e.latlng.lat, e.latlng.lng));
    mapRef.current = map;
    initializedRef.current = true;
  }, []);

  useEffect(() => {
    if (!mapRef.current || layers.length === 0) return;
    const latestLayer = layers[layers.length - 1];
    const bounds = latestLayer.bounds;
    
    if (bounds && bounds.left !== bounds.right) {
      const layerBounds = L.latLngBounds(
        [bounds.bottom, bounds.left],
        [bounds.top, bounds.right]
      );
      mapRef.current.fitBounds(layerBounds, { padding: [50, 50] });
    }
  }, [layers.length]);

  useEffect(() => {
    if (!selectedLayer || !mapRef.current) return;
    const layer = layers.find(l => l.id === selectedLayer);
    if (!layer) return;
    
    const bounds = layer.bounds;
    if (bounds && bounds.left !== bounds.right && bounds.bottom !== bounds.top) {
      const layerBounds = L.latLngBounds(
        [bounds.bottom, bounds.left],
        [bounds.top, bounds.right]
      );
      mapRef.current.fitBounds(layerBounds, { padding: [50, 50] });
    }
  }, [selectedLayer, layers]);

  useEffect(() => {
    layersRef.current.forEach((tl, id) => {
      if (!layers.find((l) => l.id === id)) {
        mapRef.current?.removeLayer(tl);
        layersRef.current.delete(id);
      }
    });
    layers.forEach((layer) => {
      let tl = layersRef.current.get(layer.id);
      if (!tl) {
        const urlTemplate = `${API_BASE}/tiles/${layer.id}/{z}/{x}/{y}.png`;
        console.log('Tile URL example:', urlTemplate.replace('{z}', '10').replace('{x}', '757').replace('{y}', '880'));
        
        tl = L.tileLayer(urlTemplate, {
          maxZoom: 18,
          minZoom: 1,
          opacity: opacity,
          zIndex: 1000,
        });
        
        tl.addTo(mapRef.current!);
        layersRef.current.set(layer.id, tl);
      } else {
        tl.setOpacity(opacity);
      }
    });
  }, [layers, opacity]);

  return <div id="map" style={{ height: "100vh", width: "100vw" }} />;
}