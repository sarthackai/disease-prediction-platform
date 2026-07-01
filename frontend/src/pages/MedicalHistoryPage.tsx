/**
 * MedicalHistoryPage.tsx
 * Shows all past predictions for the logged-in user.
 */
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../lib/api";

interface HistoryItem {
    prediction_id: string;
    predicted_disease_id: string;
    confidence_score: number;
    severity_score: number;
    symptoms_input: Record<string, number>;
    model_used: string;
    created_at: string;
    top_predictions: { disease: string; probability: number }[];
}

export default function MedicalHistoryPage() {
    const navigate = useNavigate();
    const [history, setHistory] = useState<HistoryItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const res = await api.get("/api/v1/predictions/history");
                setHistory(res.data);
            } catch (err: any) {
                setError("Could not load medical history.");
            } finally {
                setLoading(false);
            }
        };
        fetchHistory();
    }, []);

    const getSelectedSymptoms = (input: Record<string, number>) =>
        Object.entries(input)
            .filter(([, v]) => v === 1)
            .map(([k]) => k.replace(/_/g, " "))
            .slice(0, 5);

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

            <div className="max-w-4xl mx-auto px-6 py-10">
                <h1 className="text-3xl font-bold text-gray-800 mb-2">
                    Medical History
                </h1>
                <p className="text-gray-500 mb-8">
                    All your past disease predictions in one place.
                </p>

                {/* Loading */}
                {loading && (
                    <div className="text-center py-20">
                        <p className="text-gray-500">Loading your history...</p>
                    </div>
                )}

                {/* Error */}
                {error && (
                    <div className="bg-red-50 border border-red-200 text-red-600 rounded-lg p-4 mb-6">
                        {error}
                    </div>
                )}

                {/* Empty State */}
                {!loading && !error && history.length === 0 && (
                    <div className="text-center py-20">
                        <p className="text-5xl mb-4">📋</p>
                        <p className="text-gray-500 mb-4">
                            No predictions yet. Check your symptoms to get started.
                        </p>
                        <button
                            onClick={() => navigate("/symptoms")}
                            className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition"
                        >
                            Check Symptoms
                        </button>
                    </div>
                )}

                {/* History List */}
                {!loading && !error && history.length > 0 && (
                    <div className="space-y-4">
                        {history.map((item, i) => (
                            <div
                                key={item.prediction_id}
                                className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6"
                            >
                                <div className="flex items-start justify-between flex-wrap gap-4">
                                    <div>
                                        <p className="text-xs text-gray-400 mb-1">
                                            #{i + 1} ·{" "}
                                            {new Date(item.created_at).toLocaleDateString(
                                                "en-IN",
                                                {
                                                    day: "numeric",
                                                    month: "short",
                                                    year: "numeric",
                                                    hour: "2-digit",
                                                    minute: "2-digit",
                                                }
                                            )}
                                        </p>
                                        <h3 className="text-xl font-bold text-indigo-700">
                                            {item.top_predictions?.[0]?.disease ||
                                                "Unknown Disease"}
                                        </h3>
                                        <p className="text-sm text-gray-500 mt-1">
                                            Model: {item.model_used}
                                        </p>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm text-gray-500">Confidence</p>
                                        <p className="text-2xl font-bold text-indigo-600">
                                            {item.confidence_score
                                                ? (item.confidence_score * 100).toFixed(1) + "%"
                                                : "N/A"}
                                        </p>
                                    </div>
                                </div>

                                {/* Symptoms used */}
                                <div className="mt-4">
                                    <p className="text-xs text-gray-500 mb-2">
                                        Symptoms reported:
                                    </p>
                                    <div className="flex flex-wrap gap-2">
                                        {getSelectedSymptoms(item.symptoms_input).map(
                                            (s, j) => (
                                                <span
                                                    key={j}
                                                    className="bg-indigo-50 text-indigo-600 text-xs px-3 py-1 rounded-full"
                                                >
                                                    {s}
                                                </span>
                                            )
                                        )}
                                        {Object.values(item.symptoms_input).filter(
                                            (v) => v === 1
                                        ).length > 5 && (
                                                <span className="text-xs text-gray-400 px-2 py-1">
                                                    +
                                                    {Object.values(item.symptoms_input).filter(
                                                        (v) => v === 1
                                                    ).length - 5}{" "}
                                                    more
                                                </span>
                                            )}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}