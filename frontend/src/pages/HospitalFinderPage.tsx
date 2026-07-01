/**
 * HospitalFinderPage.tsx
 * Detects user location and shows nearby hospitals on a map.
 */
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import { getNearbyHospitals } from "../lib/api";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Fix default marker icon issue with React Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
    iconUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
    shadowUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

interface Hospital {
    hospital_id: string;
    name: string;
    latitude: number;
    longitude: number;
    address?: string;
    phone?: string;
    rating?: number;
    distance_km?: number;
}

export default function HospitalFinderPage() {
    const navigate = useNavigate();
    const [hospitals, setHospitals] = useState<Hospital[]>([]);
    const [userLocation, setUserLocation] = useState<[number, number] | null>(
        null
    );
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        // Get user's real GPS location
        if (!navigator.geolocation) {
            setError("Geolocation is not supported by your browser.");
            setLoading(false);
            return;
        }

        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const { latitude, longitude } = position.coords;
                setUserLocation([latitude, longitude]);

                try {
                    const res = await getNearbyHospitals(latitude, longitude, 5000);
                    setHospitals(res.data);
                } catch (err) {
                    setError("Could not fetch nearby hospitals. Try again.");
                } finally {
                    setLoading(false);
                }
            },
            () => {
                setError(
                    "Location access denied. Please allow location access and refresh."
                );
                setLoading(false);
            }
        );
    }, []);

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Navbar */}
            <nav className="bg-white shadow-sm px-6 py-4 flex justify-between items-center">
                <div className="flex items-center gap-2">
                    <span className="text-2xl">🏥</span>
                    <span className="text-xl font-bold text-indigo-700">HealthAI</span>
                </div>
                <button
                    onClick={() => navigate("/dashboard")}
                    className="text-sm text-indigo-600 hover:underline"
                >
                    ← Back to Dashboard
                </button>
            </nav>

            <div className="max-w-6xl mx-auto px-6 py-10">
                <h1 className="text-3xl font-bold text-gray-800 mb-2">
                    Nearby Hospitals
                </h1>
                <p className="text-gray-500 mb-6">
                    Showing hospitals within 5km of your current location.
                </p>

                {/* Loading */}
                {loading && (
                    <div className="text-center py-20">
                        <p className="text-gray-500 text-lg">
                            📍 Detecting your location...
                        </p>
                    </div>
                )}

                {/* Error */}
                {error && (
                    <div className="bg-red-50 border border-red-200 text-red-600 rounded-lg p-4 mb-6">
                        {error}
                    </div>
                )}

                {/* Map + List */}
                {!loading && !error && userLocation && (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Map */}
                        <div className="lg:col-span-2 rounded-2xl overflow-hidden shadow-sm border border-gray-200 h-96">
                            <MapContainer
                                center={userLocation}
                                zoom={14}
                                style={{ height: "100%", width: "100%" }}
                            >
                                <TileLayer
                                    attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>'
                                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                                />
                                {/* User location marker */}
                                <Marker position={userLocation}>
                                    <Popup>📍 Your Location</Popup>
                                </Marker>
                                {/* Hospital markers */}
                                {hospitals.map((h) => (
                                    <Marker
                                        key={h.hospital_id}
                                        position={[h.latitude, h.longitude]}
                                    >
                                        <Popup>
                                            <strong>{h.name}</strong>
                                            <br />
                                            {h.address && <span>{h.address}<br /></span>}
                                            {h.phone && <span>📞 {h.phone}<br /></span>}
                                            {h.distance_km && (
                                                <span>📏 {h.distance_km} km away</span>
                                            )}
                                        </Popup>
                                    </Marker>
                                ))}
                            </MapContainer>
                        </div>

                        {/* Hospital List */}
                        <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
                            {hospitals.length === 0 ? (
                                <p className="text-gray-500 text-sm">
                                    No hospitals found nearby.
                                </p>
                            ) : (
                                hospitals.map((h, i) => (
                                    <div
                                        key={h.hospital_id}
                                        className="bg-white rounded-xl border border-gray-100 shadow-sm p-4"
                                    >
                                        <div className="flex items-start justify-between">
                                            <div>
                                                <p className="font-semibold text-gray-800 text-sm">
                                                    {i + 1}. {h.name}
                                                </p>
                                                {h.address && (
                                                    <p className="text-xs text-gray-500 mt-1">
                                                        📍 {h.address}
                                                    </p>
                                                )}
                                                {h.phone && (
                                                    <p className="text-xs text-gray-500">
                                                        📞 {h.phone}
                                                    </p>
                                                )}
                                            </div>
                                            {h.distance_km && (
                                                <span className="text-xs bg-indigo-50 text-indigo-600 px-2 py-1 rounded-full whitespace-nowrap">
                                                    {h.distance_km} km
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}